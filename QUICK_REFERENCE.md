# 🚀 БЫСТРАЯ СПРАВКА - AI - business

## 📁 Структура проектов

```
Python lessons/
├── 📊 quadratic_equation_project/     # Квадратные уравнения
├── 🏠 mortgage_calculator/            # Ипотечный калькулятор  
├── 🔐 gen pasw/                      # Генератор паролей
├── 🔐 pasw_gener/                    # Хранилище файлов
└── 📦 Архивы и общие файлы
```

## 📝 Краткое описание проектов

### ArtBeauty_Telegram_Tilda_bot
Система онлайн-записи для салона красоты: Telegram-бот, веб-чат для сайта (Tilda), интеграция с Google Sheets, AI-консультации (OpenAI). Локальная отладка через ngrok, деплой в облако.

### common_files
Папка с общими файлами и архивами проектов: резервные копии, перенос, быстрый старт, вспомогательные материалы.

### eleven_labs_voice_bot
Telegram-бот для генерации голосовых сообщений с помощью Eleven Labs AI. Поддержка разных голосов, языков, статистика, быстрый отклик.

### gen pasw
Генератор безопасных паролей с графическим интерфейсом на Python. Настройка длины, типов символов, индикатор силы, копирование в буфер.

### mortgage_calculator
Современное веб-приложение для расчёта ипотечных платежей с красивым интерфейсом (glassmorphism), анимациями и адаптивностью.

### quadratic_equation_project
Набор решений квадратных уравнений: консоль, графический интерфейс, визуализация, сравнение с другими функциями, обучающие примеры.

### qwen_chatbot
Интеллектуальный Telegram-бот на базе Qwen3-14B (через Chutes): общение, анализ, творчество, обучение, история диалогов.

### recipe_bot
Telegram-бот для поиска рецептов по бесплатным API: поиск по названию/ингредиенту, случайные блюда, категории, фото, видео, подробные инструкции.

## 🎯 Что запускать для изучения

### 🔢 **Математика и уравнения**
```bash
cd quadratic_equation_project
python quadratic_solver.py          # Консольный решатель
python quadratic_solver_gui.py      # Окно с графиками
python graph_demo.py                # Демо парабол
```

### 🏠 **Веб-разработка и финансы**
```bash
cd mortgage_calculator
source venv/bin/activate
python app.py                       # Запуск веб-сервера
# Открыть http://localhost:8080
```

### 🔐 **GUI приложения**
```bash
cd "gen pasw"
source venv/bin/activate
python password_generator.py        # Генератор паролей
```

## 🔧 Быстрая установка

```bash
# Для любого проекта:
cd [название_проекта]
pip install -r requirements.txt

# Активация виртуального окружения:
source venv/bin/activate          # или
source .venv/bin/activate
```

## 📚 Что изучаем в каждом проекте

| Проект | Навыки | Технологии |
|--------|---------|-------------|
| **Квадратные уравнения** | Математика, GUI, графики | tkinter, matplotlib |
| **Ипотечный калькулятор** | Веб-разработка, финансы | Flask, HTML/CSS/JS |
| **Генератор паролей** | GUI, безопасность | tkinter, random |

## 💡 Полезные команды

```bash
# Создать виртуальное окружение
python -m venv venv

# Активировать
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Запустить приложение
python [имя_файла].py

# Деактивировать
deactivate
```

## 🎓 Уровни сложности

- 🟢 **Начинающий**: `quadratic_solver.py`, `password_generator.py`
- 🟡 **Средний**: `quadratic_solver_gui.py`, `graph_demo.py`
- 🔴 **Продвинутый**: `quadratic_vs_random.py`, `mortgage_calculator`

## 📖 Документация

- `README.md` - Общее описание
- `[проект]/README.md` - Описание конкретного проекта  
- `[проект]/QUICK_START.md` - Быстрый старт проекта
- `requirements.txt` - Зависимости Python

