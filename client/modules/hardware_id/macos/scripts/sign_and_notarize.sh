#!/bin/bash

# Скрипт для подписи и нотаризации macOS приложения
# Запускать из корневой директории проекта Nexy

# --- Конфигурация ---
MODULE_NAME="hardware_id"
APP_NAME="NexyHardwareID"
DIST_DIR="./dist/${MODULE_NAME}"
APP_PATH="${DIST_DIR}/${APP_NAME}.app"
ENTITLEMENTS_FILE="./client/${MODULE_NAME}/macos/entitlements/${MODULE_NAME}.entitlements"
NOTARIZATION_CONFIG="./client/${MODULE_NAME}/macos/notarization/notarization_config.json"

# Загрузка переменных окружения из файла .env (если есть)
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Проверка наличия необходимых переменных окружения
if [ -z "${APPLE_ID}" ] || [ -z "${APP_SPECIFIC_PASSWORD}" ] || [ -z "${TEAM_ID}" ] || [ -z "${DEVELOPER_ID_APPLICATION_CERT_NAME}" ]; then
    echo "❌ Ошибка: Не установлены необходимые переменные окружения."
    echo "   Убедитесь, что APPLE_ID, APP_SPECIFIC_PASSWORD, TEAM_ID и DEVELOPER_ID_APPLICATION_CERT_NAME установлены."
    echo "   Используйте файл .env или экспортируйте их вручную."
    exit 1
fi

echo "🚀 Начинаем подпись и нотаризацию приложения ${APP_NAME}..."

# 1. Проверяем существование приложения
if [ ! -d "${APP_PATH}" ]; then
    echo "❌ Ошибка: Приложение не найдено по пути ${APP_PATH}. Сначала выполните сборку."
    exit 1
fi

# 2. Подписываем приложение
echo "✍️ Подписываем приложение с entitlements..."
codesign --force --deep --entitlements "${ENTITLEMENTS_FILE}" --options runtime --sign "${DEVELOPER_ID_APPLICATION_CERT_NAME}" "${APP_PATH}"

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при подписании приложения."
    exit 1
fi
echo "✅ Приложение успешно подписано."

# 3. Архивируем приложение для нотаризации
echo "📦 Архивируем приложение для нотаризации..."
xcrun ditto -c -k --sequesterRsrc --keepParent "${APP_PATH}" "${APP_PATH}.zip"

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при архивировании приложения."
    exit 1
fi
echo "✅ Приложение успешно заархивировано: ${APP_PATH}.zip"

# 4. Отправляем на нотаризацию
echo "☁️ Отправляем приложение на нотаризацию..."
REQUEST_UUID=$(xcrun notarytool submit "${APP_PATH}.zip" \
    --apple-id "${APPLE_ID}" \
    --password "${APP_SPECIFIC_PASSWORD}" \
    --team-id "${TEAM_ID}" \
    --wait-for-completion | grep "id:" | awk '{print $NF}')

if [ $? -ne 0 ] || [ -z "${REQUEST_UUID}" ]; then
    echo "❌ Ошибка при отправке на нотаризацию или получении UUID запроса."
    exit 1
fi
echo "✅ Запрос на нотаризацию отправлен. UUID: ${REQUEST_UUID}"

# 5. Проверяем статус нотаризации (уже включено в --wait-for-completion)
# Если --wait-for-completion не работает или нужно больше деталей:
# echo "⏳ Ожидаем завершения нотаризации..."
# xcrun notarytool log "${REQUEST_UUID}" --apple-id "${APPLE_ID}" --password "${APP_SPECIFIC_PASSWORD}" --team-id "${TEAM_ID}" --output-format json > notary_log.json
# cat notary_log.json

# 6. Прикрепляем билет Staple
echo "📎 Прикрепляем билет Staple к приложению..."
xcrun stapler staple "${APP_PATH}"

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при прикреплении билета Staple."
    exit 1
fi
echo "✅ Билет Staple успешно прикреплен."

echo "🎉 Приложение ${APP_NAME} успешно подписано и нотаризовано!"

# Очистка архива
rm "${APP_PATH}.zip"
echo "🧹 Временный архив удален."

# 7. Показываем информацию о подписанном приложении
echo ""
echo "📊 Информация о подписанном приложении:"
echo "   - Приложение: ${APP_NAME}"
echo "   - Путь: ${APP_PATH}"
echo "   - Entitlements: ${ENTITLEMENTS_FILE}"
echo "   - Статус: Подписано и нотаризовано"
echo "   - UUID запроса: ${REQUEST_UUID}"
