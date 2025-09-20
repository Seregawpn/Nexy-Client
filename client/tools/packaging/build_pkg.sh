#!/usr/bin/env bash
# Финальный скрипт сборки PKG с нотарификацией
# Основан на полном чек-листе PyInstaller + Sparkle + PKG

set -euo pipefail

# ========================================
# КОНФИГУРАЦИЯ (ЗАМЕНИТЕ НА СВОИ ЗНАЧЕНИЯ)
# ========================================
APP_NAME="Nexy"
SPEC_FILE="Nexy.spec"
DIST_DIR="../dist"
PKG="${DIST_DIR}/${APP_NAME}.pkg"

# Сертификаты (уже настроены)
APP_ID="Developer ID Application: Sergiy Zasorin (5NKLL2CLB9)"
PKG_ID="Developer ID Installer: Sergiy Zasorin (5NKLL2CLB9)"

# Notarytool настройки
APPLE_ID="sergiyzasorin@gmail.com"  # TODO: замените на ваш email
TEAM_ID="5NKLL2CLB9"
PROFILE="nexy-notary"

echo "🔧 Начинаем финальную сборку PKG с нотарификацией..."

# ========================================
# ШАГ 1: Очистка предыдущих сборок
# ========================================
echo "🧹 Очищаем предыдущие сборки..."
rm -rf build "${DIST_DIR}" || true

# ========================================
# ШАГ 2: Сборка .app через PyInstaller
# ========================================
echo "🔨 Собираем .app через PyInstaller..."
cd ../..
python3 -m PyInstaller --clean -y client/tools/packaging/${SPEC_FILE}
cd ../..ols/packaging

# ========================================
# ШАГ 3: Очистка extended attributes (КРИТИЧНО!)
# ========================================
echo "🧹 Очищаем extended attributes..."
xattr -rc "${DIST_DIR}/${APP_NAME}.app"

# ========================================
# ШАГ 4: Проверка подписи .app
# ========================================
echo "🔍 Проверяем подпись .app..."
if codesign --verify --deep --strict --verbose=2 "${DIST_DIR}/${APP_NAME}.app"; then
    echo "✅ .app подписан корректно"
else
    echo "❌ .app не подписан корректно"
    exit 1
fi

# Проверка Gatekeeper (может не пройти для неподписанных приложений)
echo "🔍 Проверяем Gatekeeper..."
if spctl -a -vv "${DIST_DIR}/${APP_NAME}.app" 2>/dev/null; then
    echo "✅ .app прошел проверку Gatekeeper"
else
    echo "⚠️ .app не прошел проверку Gatekeeper (нормально для неподписанных приложений)"
fi

# ========================================
# ШАГ 5: Сборка и подпись PKG
# ========================================
echo "📦 Создаем и подписываем PKG..."
pkgbuild \
  --component "${DIST_DIR}/${APP_NAME}.app" \
  --install-location "/Applications" \
  --sign "${PKG_ID}" \
  "${PKG}"

# ========================================
# ШАГ 6: Проверка подписи PKG
# ========================================
echo "🔍 Проверяем подпись PKG..."
if pkgutil --check-signature "${PKG}"; then
    echo "✅ PKG подписан корректно"
else
    echo "❌ PKG не подписан корректно"
    exit 1
fi

# ========================================
# ШАГ 7: Нотарификация PKG
# ========================================
echo "📋 Отправляем PKG на нотаризацию..."
SUBMISSION_ID=$(xcrun notarytool submit "${PKG}" \
  --apple-id "${APPLE_ID}" \
  --team-id "${TEAM_ID}" \
  --keychain-profile "${PROFILE}" \
  --wait | grep "id:" | cut -d' ' -f2)

if [ -n "$SUBMISSION_ID" ]; then
    echo "✅ PKG нотаризирован успешно (ID: $SUBMISSION_ID)"
else
    echo "❌ Ошибка нотаризации"
    exit 1
fi

# ========================================
# ШАГ 8: Скрепление нотаризации
# ========================================
echo "📌 Скрепляем нотаризацию..."
if xcrun stapler staple "${PKG}"; then
    echo "✅ Нотаризация скреплена"
else
    echo "❌ Ошибка скрепления нотаризации"
    exit 1
fi

# ========================================
# ШАГ 9: Финальная проверка
# ========================================
echo "🔍 Финальная проверка PKG..."
if xcrun stapler validate "${PKG}"; then
    echo "✅ PKG прошел финальную проверку"
else
    echo "⚠️ PKG не прошел финальную проверку"
fi

# ========================================
# РЕЗУЛЬТАТ
# ========================================
echo ""
echo "🎉 Сборка завершена успешно!"
echo "📍 Готовый .app: ${DIST_DIR}/${APP_NAME}.app"
echo "📍 Готовый PKG: ${PKG}"
echo ""
echo "💡 Для тестирования установки:"
echo "   sudo installer -pkg \"${PKG}\" -target /"
echo ""
echo "💡 Для обновления appcast.xml:"
echo "   ./sign_appcast.sh local_server/updates/appcast.xml"
