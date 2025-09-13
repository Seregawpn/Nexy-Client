#!/bin/bash
# Полная переупаковка, подписание и нотаризация Nexy AI Voice Assistant

set -e

echo "🔄 ПОЛНАЯ ПЕРЕУПАКОВКА NEXY AI VOICE ASSISTANT"
echo "=============================================="

# Проверка, что мы в правильной директории
if [ ! -f "nexy.spec" ]; then
    echo "❌ Запустите скрипт из директории client/"
    exit 1
fi

# Этап 1: Очистка
echo ""
echo "🧹 ЭТАП 1: Очистка предыдущих сборок"
echo "------------------------------------"
rm -rf build/ dist/ *.pkg
echo "✅ Очистка завершена"

# Этап 2: Проверка зависимостей
echo ""
echo "🔍 ЭТАП 2: Проверка зависимостей"
echo "--------------------------------"
./verify_packaging.sh
echo "✅ Все зависимости проверены"

# Этап 3: Сборка приложения
echo ""
echo "🔨 ЭТАП 3: Сборка приложения"
echo "----------------------------"
echo "📦 Сборка через PyInstaller..."
if python3 -m PyInstaller nexy.spec --clean --noconfirm; then
    echo "✅ Приложение собрано успешно"
else
    echo "❌ Ошибка сборки приложения"
    exit 1
fi

# Проверка, что .app bundle создан
if [ ! -d "dist/Nexy.app" ]; then
    echo "❌ .app bundle не найден после сборки"
    exit 1
fi

# Этап 4: Подпись Sparkle Framework (если есть)
echo ""
echo "🔐 ЭТАП 4: Подпись Sparkle Framework"
echo "-----------------------------------"
if [ -f "sign_sparkle.sh" ]; then
    ./sign_sparkle.sh
    echo "✅ Sparkle Framework обработан"
else
    echo "ℹ️ Sparkle Framework не найден (пропускаем)"
fi

# Этап 5: Создание PKG
echo ""
echo "📦 ЭТАП 5: Создание PKG установщика"
echo "-----------------------------------"
if ./create_pkg.sh; then
    echo "✅ PKG создан успешно"
else
    echo "❌ Ошибка создания PKG"
    exit 1
fi

# Проверка, что PKG создан
if [ ! -f "Nexy_AI_Voice_Assistant_v1.71.0.pkg" ]; then
    echo "❌ PKG файл не найден после создания"
    exit 1
fi

# Этап 6: Нотаризация
echo ""
echo "🔐 ЭТАП 6: Нотаризация PKG"
echo "--------------------------"
if ./notarize.sh Nexy_AI_Voice_Assistant_v1.71.0.pkg; then
    echo "✅ PKG нотаризован успешно"
else
    echo "❌ Ошибка нотаризации"
    exit 1
fi

# Этап 7: Финальная проверка
echo ""
echo "✅ ЭТАП 7: Финальная проверка"
echo "-----------------------------"
echo "🔍 Проверка подписи PKG..."
if codesign --verify --verbose Nexy_AI_Voice_Assistant_v1.71.0.pkg; then
    echo "✅ Подпись PKG корректна"
else
    echo "⚠️ Проблемы с подписью PKG"
fi

echo "📊 Информация о PKG:"
du -h Nexy_AI_Voice_Assistant_v1.71.0.pkg
pkgutil --check-signature Nexy_AI_Voice_Assistant_v1.71.0.pkg

echo ""
echo "🎉 ПЕРЕУПАКОВКА ЗАВЕРШЕНА УСПЕШНО!"
echo "==================================="
echo "📦 Готовый PKG: Nexy_AI_Voice_Assistant_v1.71.0.pkg"
echo "📱 Приложение: dist/Nexy.app"
echo ""
echo "📋 Информация о продукте:"
echo "   • Версия: 1.71.0"
echo "   • Bundle ID: com.sergiyzasorin.nexy.voiceassistant"
echo "   • Подпись: Developer ID Application/Installer"
echo "   • Нотаризация: ✅ Подтверждена Apple"
echo "   • Размер: $(du -h Nexy_AI_Voice_Assistant_v1.71.0.pkg | cut -f1)"
echo ""
echo "🚀 PKG готов к распространению!"

