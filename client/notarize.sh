#!/bin/bash
set -e

# Загружаем конфигурацию
source "$(dirname "$0")/notarize_config.sh"

PKG_NAME="$1"

if [ -z "$PKG_NAME" ]; then
    echo "❌ Использование: ./notarize.sh <PKG_NAME>"
    exit 1
fi

echo "🔐 Нотаризация PKG: $PKG_NAME"

# Проверка существования файла
if [ ! -f "$PKG_NAME" ]; then
    echo "❌ PKG файл не найден: $PKG_NAME"
    exit 1
fi

# Отправка на нотаризацию
echo "📤 Отправка на нотаризацию Apple..."
if xcrun notarytool submit "$PKG_NAME" \
    --apple-id "$APPLE_ID" \
    --password "$APP_PASSWORD" \
    --team-id "$TEAM_ID" \
    --wait; then
    echo "✅ Нотаризация прошла успешно"
else
    echo "❌ Ошибка нотаризации"
    exit 1
fi

# Прикрепление тикета
echo "📎 Прикрепление нотаризационного тикета..."
if xcrun stapler staple "$PKG_NAME"; then
    echo "✅ Тикет прикреплен успешно"
else
    echo "❌ Ошибка прикрепления тикета"
    exit 1
fi

echo "✅ PKG нотаризован и готов к распространению!"
