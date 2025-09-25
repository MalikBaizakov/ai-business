# 💇‍♀️ ArtBeauty: Telegram + Tilda + Google Sheets

## 📌 О проекте
Этот проект реализует систему онлайн-записи для салона красоты:
- Telegram-бот принимает заявки от клиентов.
- Веб-чат на сайте (Tilda) работает по той же логике, что и бот.
- Все заявки автоматически сохраняются в Google Sheets.
- Есть встроенные AI-консультации для клиентов (LLM через OpenAI).

Проект задумывался как **тестовый режим и отладка локально через ngrok**.  
После тестирования и отладки деплой делается в облако (Docker, Cloud Run, VPS).

---

## ⚙️ Технологии и стек
- **Python 3.10+**
- **Flask** — для вебхуков и REST API (`/webchat`).
- **python-telegram-bot v21** — для Telegram-бота.
- **Google Sheets API (Service Account)** — хранилище заявок.
- **OpenAI SDK** — консультации через GPT-модель.
- **Tilda (HTML widget)** — онлайн-чат на сайте.
- **ngrok (dev)** — прокси для локальной отладки.
- **dotenv** — хранение секретов в `.env`.

---

## 🗂 Структура проекта
```
ArtBeauty_Telegram_Tilda_GoogleSheets/
├─ main.py                 # Flask + Telegram polling
├─ functions.py            # логика: консультации, запись, работа с Sheets
├─ tilda_chat_widget.html  # HTML/JS-виджет для Tilda
├─ requirements.txt        # зависимости
├─ .gitignore              # исключения (venv, creds, .env)
└─ README.md               # описание проекта
```

---

## 🔑 Переменные окружения (.env)
```env
# Telegram
TELEGRAM_BOT_TOKEN=xxxxxxxxxxxxxxxxxxxx

# OpenAI
OPENAI_API_KEY=sk-xxxx
OPENAI_MODEL=gpt-4o-mini

# Google Sheets
GOOGLE_APPLICATION_CREDENTIALS=creds/service_account.json
GOOGLE_SHEETS_SPREADSHEET_ID=1AbcDEF...
GOOGLE_SHEETS_RANGE=artbeauty_sheet_leads!A:L

# CORS (для Tilda-домена)
CORS_ALLOW_ORIGINS=*
```

---

## 💻 Интеграция с Tilda
Вставь код из `tilda_chat_widget.html` в блок **T123 → HTML-код**.  
Не забудь заменить URL на твой (`https://.../webchat`).

---

## ✅ Чек-лист перед запуском
- [ ] Указан корректный `TELEGRAM_BOT_TOKEN`.  
- [ ] Service Account имеет доступ **Edit** к Google Sheets.  
- [ ] URL в Tilda-виджете указывает на `/webchat`.  
- [ ] `CORS_ALLOW_ORIGINS` разрешает Tilda-домен.  

---

## 📦 Прод-деплой
- Упаковать в **Docker** или задеплоить в **облако** (Cloud Run, Render, VPS).  
- Секреты брать из менеджера секретов, а не из `.env` в git.  
- Заменить ngrok на постоянный HTTPS-домен.  

---

## ✨ Навыки и опыт, закреплённые в проекте
- Интеграция **Telegram Bot API** (python-telegram-bot v21).  
- Разработка REST API на **Flask**.  
- Работа с **Google Sheets API** через Service Account.  
- Подключение **AI-модели (OpenAI)** для консультаций.  
- Интеграция с сайтом (**Tilda**) через HTML/JS-виджет.  
- Использование **ngrok** для локальной отладки вебхуков.  
- Настройка окружений через `.env` и `.gitignore`.  
