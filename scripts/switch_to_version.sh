#!/bin/bash

# 🔄 Nexy AI Assistant - Переключение на конкретную версию
# Использование: ./scripts/switch_to_version.sh [версия]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Переход в корень проекта
cd "$(dirname "$0")/.."

# Если версия не указана, показываем список
if [ $# -eq 0 ]; then
    log "📋 Доступные версии:"
    echo ""
    
    git tag -l | sort -V | tail -10
    
    echo ""
    log "Использование: $0 <версия>"
    log "Пример: $0 v1.0.0"
    exit 0
fi

VERSION=$1

# Проверяем, что версия существует
if ! git tag -l | grep -q "^$VERSION$"; then
    error "Версия $VERSION не найдена!"
    echo ""
    log "Доступные версии:"
    git tag -l | sort -V
    exit 1
fi

log "🔄 Переключение на версию $VERSION..."

# Сохраняем текущую ветку
CURRENT_BRANCH=$(git branch --show-current)

# Переключаемся на тег
git checkout "$VERSION"

# Показываем информацию о версии
echo ""
log "📄 Информация о версии:"
git show --no-patch --format="   Версия: %D%n   Дата: %ci%n   Автор: %an%n   Коммит: %H" "$VERSION"

echo ""
log "✅ Переключение на версию $VERSION завершено!"
log "📁 Текущая ветка: $CURRENT_BRANCH (сохранена)"

echo ""
log "🔧 Следующие шаги:"
log "• Установите зависимости: pip install -r requirements.txt"
log "• Запустите приложение: python main.py"

echo ""
log "🔄 Для возврата к последней версии:"
log "git checkout $CURRENT_BRANCH"
