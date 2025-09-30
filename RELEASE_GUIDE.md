# 🚀 Руководство по созданию релизов Nexy AI Assistant

## 📋 Обзор процесса

Этот документ описывает правильный процесс создания релизов в GitHub, который позволяет:
- ✅ Создавать новые версии без затрагивания старого кода
- ✅ Четко разделять версии через теги
- ✅ Автоматически генерировать release notes
- ✅ Управлять PKG файлами для каждой версии

## 🏷️ Semantic Versioning

Используем стандарт [Semantic Versioning](https://semver.org/):
- **MAJOR** (X.0.0): Кардинальные изменения, ломающие совместимость
- **MINOR** (0.X.0): Новые функции, обратно совместимые
- **PATCH** (0.0.X): Исправления багов

### Примеры версий:
- `v3.5.0` - VoiceOver интеграция (новая функция)
- `v3.5.1` - Исправление бага в VoiceOver
- `v4.0.0` - Кардинальные изменения архитектуры

## 🔄 Процесс создания релиза

### 1. Подготовка к релизу

```bash
# Убедитесь, что все изменения закоммичены
git status

# Если есть изменения, закоммитьте их
git add .
git commit -m "feat: add new feature description"
git push origin main
```

### 2. Создание релиза

```bash
# Используйте скрипт для создания релиза
./scripts/create_release.sh v3.5.0 "VoiceOver integration completed"

# Или вручную:
git tag -a v3.5.0 -m "VoiceOver integration completed"
git push origin v3.5.0
```

### 3. Создание PKG файла

```bash
# Создайте подписанный PKG файл
./packaging/build_final.sh

# Файл будет в dist/Nexy.pkg
```

### 4. Прикрепление к GitHub Release

```bash
# Если установлен GitHub CLI
gh release upload v3.5.0 dist/Nexy.pkg

# Или вручную через веб-интерфейс GitHub
```

## 📁 Структура релизов

```
releases/
├── v3.4.0/          # Предыдущая версия
│   ├── Nexy.pkg
│   └── release-notes.md
├── v3.5.0/          # Текущая версия
│   ├── Nexy.pkg
│   └── release-notes.md
└── latest/          # Символическая ссылка на последнюю версию
    └── Nexy.pkg
```

## 🎯 Автоматизация через GitHub Actions

### Workflow для автоматических релизов

```yaml
# .github/workflows/release.yml
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

## 📝 Release Notes Template

```markdown
## Что нового в v3.5.0

VoiceOver integration completed - умное управление VoiceOver для пользователей с нарушениями зрения.

### ✨ Новые функции:
- VoiceOver интеграция с умным управлением
- Автоматическое отключение VoiceOver во время записи
- Восстановление VoiceOver после завершения работы

### 🐛 Исправления:
- Исправлен баг с воспроизведением аудио
- Улучшена стабильность переходов между режимами

### 🔧 Технические изменения:
- Добавлен модуль voiceover_control
- Создана интеграция VoiceOverDuckingIntegration
- Обновлена архитектура до 18 интеграций

### 📦 Установка:
1. Скачайте `Nexy.pkg` из Assets ниже
2. Установите через двойной клик
3. Разрешите необходимые разрешения в System Preferences

### ⚠️ Требования:
- macOS 12.0+
- Разрешения: Microphone, Screen Recording, Accessibility, VoiceOver
```

## 🔍 Проверка релиза

### Перед созданием релиза:
- [ ] Все тесты проходят
- [ ] Документация обновлена
- [ ] Версия в конфигурации обновлена
- [ ] PKG файл создан и протестирован
- [ ] Release notes подготовлены

### После создания релиза:
- [ ] Тег создан в GitHub
- [ ] Release создан с правильным описанием
- [ ] PKG файл прикреплен к релизу
- [ ] Release notes опубликованы
- [ ] Пользователи уведомлены о новой версии

## 🚨 Важные правила

### ❌ НЕ ДЕЛАЙТЕ:
- Не изменяйте уже созданные теги
- Не удаляйте релизы после публикации
- Не создавайте релизы с одинаковыми версиями
- Не коммитьте секреты в релизы

### ✅ ДЕЛАЙТЕ:
- Всегда используйте semantic versioning
- Создавайте подробные release notes
- Тестируйте PKG файлы перед публикацией
- Документируйте breaking changes
- Следите за обратной совместимостью

## 📊 Отслеживание версий

### Файлы версионирования:
- `VERSION` - текущая версия проекта
- `client/config/unified_config.yaml` - версия в конфигурации
- `package.json` (если есть) - версия для Node.js зависимостей

### Команды для проверки:
```bash
# Текущая версия
cat VERSION

# Все теги
git tag --list

# История изменений между версиями
git log v3.4.0..v3.5.0 --oneline

# Статистика изменений
git diff --stat v3.4.0..v3.5.0
```

## 🔗 Полезные ссылки

- [Semantic Versioning](https://semver.org/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [GitHub CLI](https://cli.github.com/)
- [macOS Code Signing](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)

---

**Последнее обновление:** 29 сентября 2025
**Текущая версия:** v3.5.0
