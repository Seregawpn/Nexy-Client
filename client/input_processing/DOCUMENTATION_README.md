# 📚 Input Processing - Документация

## 🎯 Обзор документации

Данная папка содержит полную документацию для модуля `input_processing`, включая руководства по интеграции, упаковке, сертификации и быстрые чеклисты.

## 📁 Структура документации

### 📖 Основные документы:
- **`INTEGRATION_GUIDE.md`** - Полное руководство по интеграции модуля с проектом
- **`PACKAGING_AND_CERTIFICATION_GUIDE.md`** - Детальное руководство по упаковке и сертификации для macOS
- **`QUICK_CHECKLIST.md`** - Быстрый чеклист для опытных разработчиков
- **`README.md`** - Основная документация модуля

### 🔧 Техническая документация:
- **`INTEGRATION_GUIDE.md`** - Интеграция с основным проектом
- **`PACKAGING_AND_CERTIFICATION_GUIDE.md`** - Требования для macOS упаковки
- **`QUICK_CHECKLIST.md`** - Краткий список действий

## 🚀 Быстрый старт

### Для интеграции:
1. 📖 Прочитайте `INTEGRATION_GUIDE.md` - полное руководство по интеграции
2. 🔍 Изучите примеры кода и API методы
3. ⚡ Используйте `QUICK_CHECKLIST.md` - для быстрой проверки

### Для упаковки:
1. 📦 Изучите `PACKAGING_AND_CERTIFICATION_GUIDE.md` - требования Apple
2. ⚡ Следуйте `QUICK_CHECKLIST.md` - быстрый процесс сборки
3. 🔍 Проверьте все требования безопасности

## 📋 Предварительные требования

### Для интеграции:
- ✅ **Python 3.9+**
- ✅ **pynput>=1.7.6** (для клавиатуры)
- ✅ **speechrecognition>=3.10.0** (для речи)
- ✅ **pyaudio>=0.2.11** (для аудио)
- ✅ **sounddevice>=0.4.5** (для аудио)
- ✅ **numpy>=1.21.0** (для обработки)

### Для упаковки:
- ✅ **Apple Developer Account** ($99/год)
- ✅ **macOS 10.15+** (Catalina или новее)
- ✅ **Xcode Command Line Tools**
- ✅ **Homebrew** для установки зависимостей
- ✅ **PyInstaller** для создания bundle

## 🔧 Процесс интеграции

### 1. Установка зависимостей
```bash
# Установка аудио зависимостей
brew install portaudio

# Установка Python зависимостей
pip3 install pynput speechrecognition pyaudio sounddevice numpy
```

### 2. Базовое использование
```python
from input_processing import KeyboardMonitor, KeyboardConfig, SpeechRecognizer, SpeechConfig

# Конфигурация клавиатуры
keyboard_config = KeyboardConfig(
    key_to_monitor="space",
    short_press_threshold=0.6,
    long_press_threshold=2.0
)

# Конфигурация речи
speech_config = SpeechConfig(
    language="ru-RU",
    timeout=5.0,
    auto_start=True
)

# Создание мониторов
keyboard_monitor = KeyboardMonitor(keyboard_config)
speech_recognizer = SpeechRecognizer(speech_config)

# Запуск
keyboard_monitor.start_monitoring()
await speech_recognizer.start()
```

## 📦 Процесс упаковки

### 1. Подготовка
```bash
# Установка зависимостей
brew install portaudio
pip3 install pyinstaller pynput speechrecognition pyaudio sounddevice numpy
```

### 2. Сборка
```bash
# Сборка приложения
pyinstaller input_processing.spec --clean --noconfirm
```

### 3. Подписание
```bash
# Подписание приложения
codesign --force --sign "Developer ID Application: Your Name" --entitlements entitlements.plist "InputProcessing.app"
```

### 4. Нотаризация
```bash
# Отправка на нотаризацию
xcrun notarytool submit "InputProcessing.pkg" --apple-id "your-id@example.com" --password "app-password" --team-id "TEAM_ID" --wait
```

## ✅ Результат

После успешного выполнения всех шагов вы получите:
- 📦 **Подписанный PKG пакет** готовый к распространению
- 🏛️ **Нотаризованное приложение** прошедшее проверку Apple
- 🔒 **Безопасный код** соответствующий требованиям Gatekeeper
- 🚀 **Готовое к продакшену** решение

## 🆘 Поддержка

### Полезные ресурсы:
- [Apple Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)
- [Apple Notarization Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [pynput Documentation](https://pynput.readthedocs.io/)
- [SpeechRecognition Documentation](https://pypi.org/project/SpeechRecognition/)
- [sounddevice Documentation](https://python-sounddevice.readthedocs.io/)

### Команды для диагностики:
```bash
# Проверка подписи
codesign --verify --verbose "InputProcessing.app"

# Проверка Gatekeeper
spctl --assess --verbose "InputProcessing.app"

# Проверка нотаризации
xcrun stapler validate "InputProcessing.pkg"

# Проверка аудио
python3 -c "import sounddevice; print(sounddevice.query_devices())"

# Проверка клавиатуры
python3 -c "from pynput import keyboard; print('Keyboard OK')"

# Проверка речи
python3 -c "import speech_recognition; print('Speech OK')"
```

## 🎯 Особенности модуля

### ✅ Основные возможности:
- 🔑 **Мониторинг клавиатуры** - отслеживание нажатий пробела
- 🎤 **Распознавание речи** - конвертация голоса в текст
- ⏱️ **Точное измерение** - длительность нажатий до миллисекунд
- 🔄 **Асинхронная обработка** - неблокирующие операции
- 🍎 **macOS интеграция** - полная поддержка macOS требований
- 🚀 **Высокая производительность** - эффективное управление ресурсами

### 🔧 API методы:
- `KeyboardMonitor` - мониторинг клавиатуры
- `SpeechRecognizer` - распознавание речи
- `register_callback()` - регистрация обработчиков событий
- `start_monitoring()` / `stop_monitoring()` - управление клавиатурой
- `start()` / `stop()` - управление речью

### 📊 Типы событий:
- **Клавиатура:** `PRESS`, `RELEASE`, `SHORT_PRESS`, `LONG_PRESS`
- **Речь:** `STARTED`, `RECOGNIZED`, `ERROR`, `STOPPED`

## 🚀 Следующие шаги

1. **Интегрировать в main.py** - добавить обработку ввода
2. **Подключить к основному StateManager** - для управления состоянием
3. **Связать с audio_device_manager** - для аудио записи
4. **Настроить в module_coordinator** - для общего управления
5. **Добавить в упаковку** - включить в macOS bundle

---

**Готово к созданию профессионального macOS приложения!** 🎉
