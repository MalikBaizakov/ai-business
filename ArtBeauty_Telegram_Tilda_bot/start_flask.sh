#!/bin/zsh
# Запуск Flask приложения для ArtBeauty

# Активируем виртуальное окружение
source venv/bin/activate

# Экспортируем переменные окружения
export FLASK_APP=main.py
export FLASK_ENV=development
export PYTHONPATH=.

# Запускаем сервер на 5000 порту
python main.py
