#!/bin/bash

# Скрипт для запуска Nexy AI Assistant
# Активирует виртуальное окружение и запускает приложение

echo "🚀 Запуск Nexy AI Assistant..."

# Переходим в директорию скрипта
cd "$(dirname "$0")"

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "Создайте виртуальное окружение: python3 -m venv venv"
    echo "Установите зависимости: pip install -r requirements.txt"
    exit 1
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем, что зависимости установлены
if ! python3 -c "import rumps, pynput, grpcio" 2>/dev/null; then
    echo "❌ Не все зависимости установлены!"
    echo "Установите зависимости: pip install -r requirements.txt"
    exit 1
fi

echo "✅ Виртуальное окружение активировано"
echo "✅ Зависимости проверены"
echo "🚀 Запуск приложения..."

# Запускаем приложение
python3 main.py
