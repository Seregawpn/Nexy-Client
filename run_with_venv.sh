#!/bin/bash

# Скрипт для запуска Nexy Client с виртуальным окружением
# Использование: ./run_with_venv.sh

echo "🚀 Запуск Nexy Client..."

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Проверяем наличие виртуального окружения (.venv имеет приоритет)
if [ -d ".venv" ]; then
    echo "📦 Используем существующее окружение .venv"
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "📦 Используем окружение venv"
    source venv/bin/activate
else
    echo "❌ Виртуальное окружение не найдено!"
    echo "Создайте его командой: python3 -m venv .venv"
    echo "Затем установите зависимости: source .venv/bin/activate && pip install -r requirements_updated.txt"
    exit 1
fi

# Проверяем Python версию
echo "🐍 Python версия: $(python --version)"

# Запускаем приложение
echo "🎯 Запуск Nexy Client..."
python main.py

echo "👋 Nexy Client завершен."
