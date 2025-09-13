#!/bin/bash
set -e

echo "🚀 Полная сборка Nexy AI Voice Assistant для продакшена"

# Проверка сертификатов
echo "🔍 Проверка сертификатов..."
./check_certificates.sh

# Проверка зависимостей
echo "🔍 Проверка системных зависимостей..."
if ! command -v SwitchAudioSource &> /dev/null; then
    echo "❌ SwitchAudioSource не найден. Установите: brew install switchaudio-osx"
    exit 1
fi

if [ ! -d "/usr/local/lib/Sparkle.framework" ]; then
    echo "❌ Sparkle Framework не найден. Установите: brew install sparkle"
    exit 1
fi

echo "✅ Все зависимости найдены"

# Этап 1: Сборка приложения
echo "🔧 Этап 1: Сборка приложения..."
pyinstaller nexy.spec --clean --noconfirm

# Этап 2: Интеграция Sparkle
echo "🔄 Этап 2: Интеграция Sparkle..."
./integrate_sparkle.sh

# Этап 3: Создание PKG
echo "📦 Этап 3: Создание PKG..."
./create_pkg.sh

# Этап 4: Нотаризация (опционально)
echo "🔐 Этап 4: Нотаризация (опционально)..."
echo "ℹ️ Для нотаризации запустите: ./notarize.sh Nexy_AI_Voice_Assistant_v1.71.0.pkg"

echo "🎉 Сборка завершена успешно!"
echo "📦 Готовый PKG: Nexy_AI_Voice_Assistant_v1.71.0.pkg"
echo "ℹ️ Убедитесь, что пользователи установили зависимости: brew install switchaudio-osx sparkle"
