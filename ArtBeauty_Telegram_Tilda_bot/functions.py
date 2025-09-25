# functions.py
import os
import re
import uuid
import datetime as dt
from typing import Dict, Any, List

from dotenv import load_dotenv
load_dotenv()

# === Google Sheets (Service Account) ===
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "creds/service_account.json")
SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
SHEET_RANGE   = os.getenv("GOOGLE_SHEETS_RANGE", "artbeauty_sheet_leads!A:L")

_creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
_sheets = build("sheets", "v4", credentials=_creds)

# === OpenAI ===
from openai import OpenAI
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ========= Helpers =========

def now_str() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def normalize_phone(phone: str) -> str:
    """Вернёт +7XXXXXXXXXX (нормализация для KZ/RU)."""
    digits = re.sub(r"\D+", "", phone or "")
    if digits.startswith("8"):
        digits = "7" + digits[1:]
    if not digits.startswith("7"):
        digits = "7" + digits
    return "+" + digits[:11]

def generate_lead_id() -> str:
    return "L-" + uuid.uuid4().hex[:6].upper()

# Категории мастеров
MASTER_CATEGORIES = ["Стилист", "Топ-Стилист", "Ведущий Стилист", "Арт-Директор"]

# ========= Google Sheets =========

def add_lead_to_sheet(data: Dict[str, Any]) -> str:
    """Записывает лид в Google Sheets. Возвращает обновлённый диапазон."""
    row = [[
        now_str(),
        data.get("source", ""),
        data.get("client_name", ""),
        normalize_phone(data.get("phone", "")),
        data.get("service", ""),
        data.get("preferred_date", ""),
        data.get("preferred_time", ""),
        data.get("master_category", ""),
        data.get("comments", ""),
        data.get("status", "new"),
        data.get("telegram_username", ""),
        data.get("lead_id", generate_lead_id()),
    ]]
    res = _sheets.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_RANGE,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": row},
    ).execute()
    return res.get("updates", {}).get("updatedRange", "")

def save_booking_data(payload: Dict[str, Any]) -> str:
    """Обёртка."""
    return add_lead_to_sheet(payload)

# ========= AI Assistant =========

KNOWLEDGE_BASE: List[Dict[str, str]] = [
    {"Вопросы":"Что входит в стандартную процедуру окрашивания в вашем салоне?","Ответы":"В стоимость включены осветление тонирование и укладка."},
    {"Вопросы":"Можно ли провести окрашивание в день консультации?","Ответы":"Да если у мастера будет свободное время после консультации можно сделать окрашивание сразу."},
    {"Вопросы":"Какие категории мастеров есть в вашем салоне?","Ответы":"Стилист, Топ-Стилист, Ведущий Стилист и Арт-Директор."},
    {"Вопросы":"Каковы цены на услуги различных мастеров?","Ответы":"Цена зависит от категории мастера и сложности услуги: от 12 тыс. руб. у стилиста до 30 тыс. руб. у арт-директора."},
    {"Вопросы":"Какие услуги кроме стрижек и окрашиваний?","Ответы":"Маникюр, педикюр и косметология."},
    {"Вопросы":"Часы работы?","Ответы":"С 10:00 до 20:00, пн–сб. Воскресенье — выходной."},
    {"Вопросы":"Адрес?","Ответы":"Москва, ул. Новый Арбат, 77"},
]

SYSTEM_PROMPT = (
    "Ты - ассистент салона красоты ArtBeauty.\n"
    "Главное: консультируешь по услугам и записываешь клиентов. "
    "Если клиент хочет записаться — собираешь имя, телефон, услугу, дату, время, мастера и комментарии. "
    "После сохранения подтверждаешь запись. "
    "Отвечай тёпло и профессионально. Никаких технических ссылок или меток."
)

def build_kb_text() -> str:
    rows = [f"Q: {r['Вопросы']}\nA: {r['Ответы']}" for r in KNOWLEDGE_BASE]
    return "\n\n".join(rows)

def consult(message: str) -> str:
    """Ответ ассистента с базой знаний и ИИ."""
    kb = build_kb_text()
    try:
        resp = _openai.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": "База знаний:\n" + kb},
                {"role": "user", "content": message.strip()},
            ],
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception:
        return "Извините, сейчас не могу ответить. Попробуйте чуть позже."

# ========= Booking detection =========

BOOKING_KEYWORDS = [
    "записать", "запиш", "бронь", "забронировать",
    "хочу записаться", "нужна стрижка", "хочу стрижку",
    "окрашивание", "маникюр", "педикюр",
    "хочу к мастеру", "могу записаться",
    "airtouch", "контуринг", "укладка",
    "стилист", "топ-стилист", "арт-директор"
]

def looks_like_booking(text: str) -> bool:
    """Простая проверка на намерение записи."""
    if not text:
        return False
    t = text.lower()
    return any(k in t for k in BOOKING_KEYWORDS)
