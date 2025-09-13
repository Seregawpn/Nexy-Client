# 📦 Упаковка Nexy AI Voice Assistant для macOS

## 🔐 Настройка сертификатов

### 1. Проверка существующих сертификатов
```bash
./check_certificates.sh
```

### 2. Настройка нотаризации
```bash
./setup_notarization.sh
```

## 🚀 Сборка приложения

### 1. Установка системных зависимостей
```bash
brew install switchaudio-osx sparkle
```

### 2. Полная сборка
```bash
./build_production.sh
```

### 3. Нотаризация (опционально)
```bash
./notarize.sh Nexy_AI_Voice_Assistant_v1.71.0.pkg
```

## 📋 Структура файлов

### Основные скрипты:
- `build_production.sh` - Главный скрипт сборки
- `check_certificates.sh` - Проверка сертификатов
- `setup_notarization.sh` - Настройка нотаризации
- `create_pkg.sh` - Создание PKG установщика
- `notarize.sh` - Нотаризация PKG
- `integrate_sparkle.sh` - Интеграция Sparkle Framework

### Конфигурационные файлы:
- `nexy.spec` - PyInstaller конфигурация
- `entitlements.plist` - Права доступа для подписи кода
- `notarize_config.sh` - Конфигурация нотаризации

## 🔧 Требования

### Системные зависимости:
- macOS 10.15+ (Catalina или новее)
- Xcode Command Line Tools
- Homebrew

### Сертификаты:
- ✅ Developer ID Application: Sergiy Zasorin (5NKLL2CLB9)
- ✅ Developer ID Installer: Sergiy Zasorin (5NKLL2CLB9)
- ⚠️ App-Specific Password (настройте через setup_notarization.sh)

### Установленные пакеты:
- SwitchAudioSource (через Homebrew)
- Sparkle Framework (через Homebrew)

## 🎯 Bundle ID

Приложение использует Bundle ID: `com.sergiyzasorin.nexy.voiceassistant`

## 🔐 Разрешения macOS

Приложение запрашивает следующие разрешения:
- 🎤 Микрофон (Microphone)
- 📸 Захват экрана (Screen Recording)
- ♿ Accessibility (Управление приложениями)
- 🍎 Apple Events (Автоматизация)

## 📦 Результат сборки

После успешной сборки будет создан:
- `Nexy_AI_Voice_Assistant_v1.71.0.pkg` - Установщик для macOS
- `dist/Nexy.app` - Приложение в формате .app bundle

## ⚠️ Важные замечания

1. **FLAC 1.5.0** уже встроен в Speech Recognition - дополнительная установка не нужна
2. **SwitchAudioSource** устанавливается через Homebrew - не копируется в приложение
3. **Sparkle Framework** интегрируется в .app bundle для автообновлений
4. **Все разрешения** запрашиваются автоматически при первом запуске

## 🆘 Устранение проблем

### Ошибка подписи кода:
```bash
# Проверьте сертификаты
security find-identity -v -p codesigning

# Обновите сертификаты в Apple Developer Portal
```

### Ошибка нотаризации:
```bash
# Проверьте App-Specific Password
./setup_notarization.sh

# Проверьте статус нотаризации
xcrun notarytool history --apple-id sergiyzasorin@gmail.com --password YOUR_PASSWORD --team-id 5NKLL2CLB9
```

### Ошибка зависимостей:
```bash
# Переустановите зависимости
brew reinstall switchaudio-osx sparkle

# Проверьте установку
which SwitchAudioSource
ls /usr/local/lib/Sparkle.framework
```
