# main.py
import os
import logging

from typing import Dict, cast
from telegram import Message, Update   # 👈 ОБА нужны

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

from functions import (
    consult, looks_like_booking, save_booking_data,
    generate_lead_id, normalize_phone, MASTER_CATEGORIES
)

def msg(update: Update) -> Message:
    # В PTB message может быть None (например, callback-кнопки),
    # а у нас только текстовые апдейты — значит смело кастуем.
    return cast(Message, update.message)

load_dotenv()

# ===== Flask (веб-чат для Tilda) =====
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ALLOW_ORIGINS", "*")}})

# Простейшая in-memory сессия по IP (демо). Для продакшена — куки/redis.
WEB_SESSIONS: Dict[str, Dict] = {}

def web_state(key: str) -> Dict:
    if key not in WEB_SESSIONS:
        WEB_SESSIONS[key] = {"step": None, "data": {}}
    return WEB_SESSIONS[key]

@app.post("/webchat")
def webchat():
    body = request.get_json(silent=True) or {}
    text = (body.get("message") or "").strip()
    sid = request.headers.get("X-Forwarded-For", request.remote_addr) or "anon"
    state = web_state(sid)

    # Если уже идёт запись — продолжаем шаги
    if state["step"]:
        return jsonify({"reply": web_booking_flow_step(state, text)})

    # Если это намерение на запись — запускаем диалог записи
    if looks_like_booking(text):
        state["step"] = "ASK_NAME"
        state["data"] = {"source": "web", "status": "new", "lead_id": generate_lead_id()}
        return jsonify({"reply": "Отлично! Давайте оформим запись. Как вас зовут?"})

    # Иначе — просто консультация
    return jsonify({"reply": consult(text)})

def web_booking_flow_step(state: Dict, text: str) -> str:
    data = state["data"]
    step = state["step"]

    if step == "ASK_NAME":
        data["client_name"] = text
        state["step"] = "ASK_PHONE"
        return "Укажите ваш телефон (например, +7 701 000 00 00):"

    if step == "ASK_PHONE":
        data["phone"] = normalize_phone(text)
        state["step"] = "ASK_SERVICE"
        return "Какую услугу вы хотите? (например, Маникюр/Стрижка/Окрашивание)"

    if step == "ASK_SERVICE":
        data["service"] = text
        state["step"] = "ASK_DATE"
        return "Желаемая дата (в формате ГГГГ-ММ-ДД):"

    if step == "ASK_DATE":
        data["preferred_date"] = text
        state["step"] = "ASK_TIME"
        return "Желаемое время (например, 15:00):"

    if step == "ASK_TIME":
        data["preferred_time"] = text
        state["step"] = "ASK_CATEGORY"
        cats = " / ".join(MASTER_CATEGORIES)
        return f"Выберите категорию мастера: {cats}"

    if step == "ASK_CATEGORY":
        data["master_category"] = text
        state["step"] = "ASK_COMMENTS"
        return "Есть ли дополнительные пожелания? Если нет — напишите «нет»."

    if step == "ASK_COMMENTS":
        data["comments"] = "" if text.lower() == "нет" else text
        # Сохраняем
        updated_range = save_booking_data({
            **data,
            "telegram_username": "",
        })
        state["step"] = None
        msg = (
            "Отлично! Сохраняю вашу запись…\n"
            "✅ Готово! Мы свяжемся с вами для подтверждения.\n"
            f"ID заявки: {data.get('lead_id')}"
        )
        return msg

    # fallback
    state["step"] = None
    return "Начнём заново. Как вас зовут?"

# ===== Telegram bot (python-telegram-bot 20.x, async) =====
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters,
)

logging.basicConfig(level=logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")))
logger = logging.getLogger("artbeauty")

ASK_NAME, ASK_PHONE, ASK_SERVICE, ASK_DATE, ASK_TIME, ASK_CATEGORY, ASK_COMMENTS = range(7)

def kb_row(options):
    return ReplyKeyboardMarkup([options], resize_keyboard=True, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data.update({
        "lead_id": generate_lead_id(),
        "source": "telegram",
        "status": "new",
        "telegram_username": ("@"+update.effective_user.username) if update.effective_user and update.effective_user.username else "",
    })
    await msg(update).reply_text(
        "ArtBeauty — с радостью поможем. Хотите консультацию или сразу записаться?",
        reply_markup=kb_row(["Консультация", "Запись"])
    )
    return ASK_NAME


async def handle_first_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.message.text or "").lower()
    if "зап" in txt:
        await msg(update).reply_text(
            "Отлично! Как вас зовут?", reply_markup=ReplyKeyboardRemove()
        )
        return ASK_PHONE

    # консультация
    answer = consult(update.message.text)
    await msg(update).reply_text(answer)
    await msg(update).reply_text(
        "Если хотите записаться — просто напишите услугу или «хочу записаться»."
    )
    return ASK_NAME


async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["client_name"] = update.message.text.strip()
    await msg(update).reply_text(
        "Укажите телефон (например, +7 701 000 00 00):"
    )
    return ASK_SERVICE


async def ask_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = normalize_phone(update.message.text)
    await msg(update).reply_text(
        "Какую услугу хотите? (Маникюр/Стрижка/Окрашивание и т.д.)"
    )
    return ASK_DATE


async def ask_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["service"] = update.message.text.strip()
    await msg(update).reply_text(
        "Желаемая дата (ГГГГ-ММ-ДД):"
    )
    return ASK_TIME


async def ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["preferred_date"] = update.message.text.strip()
    await msg(update).reply_text(
        "Желаемое время (например, 15:00):"
    )
    return ASK_CATEGORY


async def ask_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["preferred_time"] = update.message.text.strip()
    cats = " / ".join(MASTER_CATEGORIES)
    await msg(update).reply_text(
        f"Категория мастера: {cats}\nНапишите нужную категорию."
    )
    return ASK_COMMENTS


async def ask_comments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["master_category"] = update.message.text.strip()
    await msg(update).reply_text(
        "Есть пожелания по длине/цвету/дизайну? Если нет — напишите «нет»."
    )
    return ConversationHandler.END


async def finalize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # текст от пользователя на последнем шаге (может быть "нет")
    txt = (msg(update).text or "").strip()
    context.user_data["comments"] = "" if txt.lower() == "нет" else txt

    payload = {
        "source":            context.user_data.get("source"),
        "client_name":       context.user_data.get("client_name"),
        "phone":             context.user_data.get("phone"),
        "service":           context.user_data.get("service"),
        "preferred_date":    context.user_data.get("preferred_date"),
        "preferred_time":    context.user_data.get("preferred_time"),
        "master_category":   context.user_data.get("master_category"),
        "comments":          context.user_data.get("comments"),
        "status":            context.user_data.get("status"),
        "telegram_username": context.user_data.get("telegram_username"),
        "lead_id":           context.user_data.get("lead_id"),
    }

    try:
        save_booking_data(payload)
        await msg(update).reply_text(
            "Отлично! Все данные собраны, сохраняю запись…\n"
            "✅ Готово! Ваша заявка создана. Мы свяжемся с вами для подтверждения.\n"
            f"ID: {payload.get('lead_id')}"
        )
    except Exception:
        logger.exception("Sheet append error")
        await msg(update).reply_text(
            "Не удалось сохранить запись, попробуйте ещё раз позже.",
            reply_markup=ReplyKeyboardRemove()
        )
    finally:
        context.user_data.clear()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await msg(update).reply_text(
        "Ок, отменяем. Если захотите, начнём заново — /start",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

def build_tg_app():
    token = cast(str, os.getenv("TELEGRAM_BOT_TOKEN"))

    return Application.builder().token(token).build()

def add_handlers(app: Application):
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_first_choice)
            ],
            ASK_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)
            ],
            ASK_SERVICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_service)
            ],
            ASK_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_date)
            ],
            ASK_TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_time)
            ],
            ASK_CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_category)
            ],
            ASK_COMMENTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_comments),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    # Финал — любое следующее сообщение после ASK_COMMENTS
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, finalize))

if __name__ == "__main__":
    # Собираем Telegram и навешиваем хендлеры
    tg_app = build_tg_app()
    add_handlers(tg_app)

    # Flask поднимем в фоне
    from threading import Thread
    def run_flask():
          # в потоке обязательно отключаем reloader, иначе падает с "signal only works..."
        app.run(
            host="0.0.0.0", 
            port=8000, 
            debug=True, 
            use_reloader=False, 
            threaded=True)


    Thread(target=run_flask, daemon=True).start()

    # Telegram polling (PTB v21)
    tg_app.run_polling()   # блокирующий вызов

