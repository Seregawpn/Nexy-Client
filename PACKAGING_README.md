# 📦 СИСТЕМА УПАКОВКИ NEXY AI VOICE ASSISTANT

## 🎯 ОБЗОР

Полная система автоматизации упаковки, подписания и нотаризации macOS приложения Nexy AI Voice Assistant в профессиональный PKG установщик.

## 📚 ДОКУМЕНТАЦИЯ

| Документ | Описание | Аудитория |
|----------|----------|-----------|
| [`COMPLETE_PACKAGING_GUIDE.md`](COMPLETE_PACKAGING_GUIDE.md) | Полное руководство | Все пользователи |
| [`QUICK_PACKAGING_CHECKLIST.md`](QUICK_PACKAGING_CHECKLIST.md) | Быстрый чеклист | Опытные пользователи |
| [`TECHNICAL_SPECIFICATION.md`](TECHNICAL_SPECIFICATION.md) | Техническая спецификация | Разработчики |

## 🚀 БЫСТРЫЙ СТАРТ

### 1. Подготовка
```bash
cd client/
chmod +x *.sh
```

### 2. Проверка готовности
```bash
./verify_packaging.sh
```

### 3. Полная сборка
```bash
./rebuild_and_notarize.sh
```

### 4. Результат
```
✅ Nexy_AI_Voice_Assistant_v1.71.0.pkg (59MB)
   • Подписан Developer ID
   • Нотаризован Apple
   • Готов к распространению
```

## 🔧 КОМПОНЕНТЫ СИСТЕМЫ

### Основные скрипты
- **`rebuild_and_notarize.sh`** - Полная автоматизация
- **`build_complete.sh`** - Основная сборка
- **`create_pkg.sh`** - Создание PKG
- **`notarize.sh`** - Нотаризация
- **`verify_packaging.sh`** - Проверка готовности

### Конфигурационные файлы
- **`nexy.spec`** - PyInstaller конфигурация
- **`entitlements.plist`** - macOS разрешения
- **`notarize_config.sh`** - Настройки нотаризации
- **`requirements.txt`** - Python зависимости

### Вспомогательные скрипты
- **`sign_sparkle.sh`** - Подпись Sparkle Framework
- **`update_flac.sh`** - Обновление FLAC
- **`check_certificates.sh`** - Проверка сертификатов

## 📋 ТРЕБОВАНИЯ

### Системные
- macOS 10.15+
- Xcode Command Line Tools
- Python 3.9+
- Homebrew

### Apple Developer
- Apple Developer Account ($99/год)
- Developer ID Application сертификат
- Developer ID Installer сертификат
- App-Specific Password для нотаризации

### Python зависимости
```bash
pip3 install -r requirements.txt
```

### Системные зависимости
```bash
brew install switchaudio-osx sparkle
```

## 🔄 ПРОЦЕСС УПАКОВКИ

### Автоматический (рекомендуется)
```bash
./rebuild_and_notarize.sh
```

### Ручной пошаговый
```bash
# 1. Проверка
./verify_packaging.sh

# 2. Сборка
python3 -m PyInstaller nexy.spec --clean --noconfirm

# 3. Создание PKG
./create_pkg.sh

# 4. Нотаризация
./notarize.sh Nexy_AI_Voice_Assistant_v1.71.0.pkg
```

## 🧪 ТЕСТИРОВАНИЕ

### Проверка подписи
```bash
pkgutil --check-signature Nexy_AI_Voice_Assistant_v1.71.0.pkg
```

### Проверка нотаризации
```bash
xcrun stapler validate Nexy_AI_Voice_Assistant_v1.71.0.pkg
```

### Тестовая установка
```bash
sudo installer -pkg Nexy_AI_Voice_Assistant_v1.71.0.pkg -target /
```

## 📊 ХАРАКТЕРИСТИКИ

| Параметр | Значение |
|----------|----------|
| **Размер PKG** | ~59MB |
| **Размер .app** | ~200MB |
| **Время сборки** | 5-10 минут |
| **Время нотаризации** | 10-15 минут |
| **Совместимость** | macOS 10.15+ |
| **Архитектура** | arm64 (Apple Silicon) |

## 🔐 БЕЗОПАСНОСТЬ

### Подписание
- Developer ID Application для .app bundle
- Developer ID Installer для PKG
- Hardened Runtime включен
- Entitlements настроены

### Нотаризация
- Apple Notary Service
- Автоматическая проверка
- Тикет прикреплен

### Разрешения
- Микрофон (TCC)
- Камера (TCC)
- Захват экрана (TCC)
- Apple Events (TCC)
- Сеть (клиент/сервер)
- Bluetooth (аудио устройства)

## 🎯 РЕЗУЛЬТАТ

### Готовый PKG установщик
- ✅ Профессиональная подпись
- ✅ Apple нотаризация
- ✅ Автозапуск приложения
- ✅ Все необходимые разрешения
- ✅ Система автообновлений (опционально)

### Для пользователей
- Простая установка (двойной клик)
- Автоматический автозапуск
- Запрос разрешений при первом запуске
- Работа в системном трее

## ❗ УСТРАНЕНИЕ НЕПОЛАДОК

### Частые проблемы
1. **Ошибка подписания** → Очистить атрибуты: `xattr -cr file.app`
2. **Ошибка нотаризации** → Проверить Apple ID в `notarize_config.sh`
3. **PyInstaller не найден** → Использовать `python3 -m PyInstaller`
4. **Отсутствуют зависимости** → `pip3 install -r requirements.txt`

### Диагностика
```bash
# Проверка сертификатов
security find-identity -v -p codesigning

# Проверка подписи
codesign --verify --verbose dist/Nexy.app

# Проверка нотаризации
xcrun stapler validate Nexy_AI_Voice_Assistant_v1.71.0.pkg
```

## 📞 ПОДДЕРЖКА

### Документация
- Полное руководство: `COMPLETE_PACKAGING_GUIDE.md`
- Быстрый старт: `QUICK_PACKAGING_CHECKLIST.md`
- Техническая спецификация: `TECHNICAL_SPECIFICATION.md`

### Полезные ссылки
- [Apple Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)
- [Apple Notarization Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)

---

**🎉 Система готова к использованию! Следуйте документации для получения профессионального PKG установщика.**

