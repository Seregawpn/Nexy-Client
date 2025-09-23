# Welcome Message Module - Integration Guide

## 📋 Обзор

Модуль `welcome_message` предназначен для воспроизведения приветственного сообщения при запуске приложения Nexy AI Assistant. Поддерживает предзаписанное аудио и fallback на TTS.

## 🏗️ Архитектура

### Основные компоненты

1. **`WelcomePlayer`** - основной плеер приветствия
2. **`WelcomeAudioGenerator`** - генератор аудио (локальный)
3. **`WelcomeConfig`** - конфигурация модуля
4. **`WelcomeMessageIntegration`** - интеграция с EventBus

### Структура модуля

```
modules/welcome_message/
├── core/
│   ├── welcome_player.py          # Основной плеер
│   ├── audio_generator.py         # Генератор аудио
│   └── types.py                   # Типы данных
├── config/
│   └── welcome_config.py          # Загрузчик конфигурации
├── assets/
│   ├── welcome_en.mp3             # Предзаписанное аудио
│   └── welcome_en.wav             # Альтернативный формат
└── tests/
    ├── test_welcome_player.py
    └── test_audio_generator.py
```

## 🔧 Использование

### Базовое использование

```python
from modules.welcome_message import WelcomePlayer, WelcomeConfig

# Создание конфигурации
config = WelcomeConfig(
    enabled=True,
    text="Hi! Nexy is here. How can I help you?",
    audio_file="assets/audio/welcome_en.mp3",
    fallback_to_tts=True
)

# Создание плеера
player = WelcomePlayer(config)

# Воспроизведение
result = await player.play_welcome()
```

### Интеграция с EventBus

```python
from integration.integrations.welcome_message_integration import WelcomeMessageIntegration

# Создание интеграции
integration = WelcomeMessageIntegration(
    event_bus=event_bus,
    state_manager=state_manager,
    error_handler=error_handler
)

# Инициализация и запуск
await integration.initialize()
await integration.start()
```

## ⚙️ Конфигурация

### YAML конфигурация

```yaml
# client/config/unified_config.yaml
welcome_message:
  enabled: true
  text: "Hi! Nexy is here. How can I help you?"
  audio_file: "assets/audio/welcome_en.mp3"
  fallback_to_tts: true
  delay_sec: 1.0
  volume: 0.8
  voice: "en-US-JennyNeural"
  sample_rate: 48000
  channels: 1
  bit_depth: 16
```

### Параметры конфигурации

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `enabled` | bool | true | Включить модуль приветствия |
| `text` | str | "Hi! Nexy is here. How can I help you?" | Текст приветствия |
| `audio_file` | str | "assets/audio/welcome_en.mp3" | Путь к предзаписанному аудио |
| `fallback_to_tts` | bool | true | Использовать TTS fallback |
| `delay_sec` | float | 1.0 | Задержка перед воспроизведением |
| `volume` | float | 0.8 | Громкость воспроизведения |
| `voice` | str | "en-US-JennyNeural" | Голос для TTS |
| `sample_rate` | int | 48000 | Частота дискретизации |
| `channels` | int | 1 | Количество каналов |
| `bit_depth` | int | 16 | Разрядность |

## 🎵 Генерация аудио

### Скрипт генерации

```bash
# Генерация предзаписанного аудио
python client/scripts/generate_welcome_audio.py
```

### Поддерживаемые форматы

- **MP3** (основной)
- **WAV** (fallback)
- **AIFF** (временный для macOS say)

### Технические требования

- **Sample Rate**: 48000 Hz
- **Channels**: 1 (mono)
- **Bit Depth**: 16-bit
- **Format**: PCM s16le

## 🔄 EventBus события

### Входящие события

| Событие | Описание | Приоритет |
|---------|----------|-----------|
| `app.startup` | Запуск приложения | MEDIUM |

### Исходящие события

| Событие | Описание | Данные |
|---------|----------|--------|
| `welcome.started` | Начало воспроизведения | `{"text": str, "method": str}` |
| `welcome.completed` | Завершение воспроизведения | `{"success": bool, "method": str, "duration_sec": float}` |
| `welcome.failed` | Ошибка воспроизведения | `{"error": str, "text": str}` |
| `playback.signal` | Запрос на воспроизведение | `{"pcm": bytes, "sample_rate": int, "channels": int}` |

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты модуля
pytest client/modules/welcome_message/tests/

# Конкретный тест
pytest client/modules/welcome_message/tests/test_welcome_player.py

# С покрытием
pytest client/modules/welcome_message/tests/ --cov=modules.welcome_message
```

### Тестовые сценарии

1. **Инициализация** - создание плеера и генератора
2. **Конфигурация** - загрузка настроек
3. **Воспроизведение** - успешное воспроизведение
4. **Fallback** - переключение на TTS
5. **Ошибки** - обработка исключений
6. **Интеграция** - работа с EventBus

## 🔧 Разработка

### Добавление нового голоса

1. Обновить `WelcomeConfig.voice`
2. Добавить поддержку в `WelcomeAudioGenerator`
3. Обновить тесты
4. Сгенерировать новое аудио

### Добавление нового языка

1. Создать новый аудио файл `welcome_<lang>.mp3`
2. Обновить конфигурацию
3. Добавить логику выбора языка
4. Обновить тесты

### Отладка

```python
import logging
logging.getLogger('modules.welcome_message').setLevel(logging.DEBUG)
```

## 🚫 Ограничения

### Архитектурные принципы

- ✅ Тонкая интеграция - не дублировать код модулей
- ✅ EventBus архитектура - все через события
- ✅ Модульная структура - отдельный модуль
- ✅ Конфигурация через YAML

### Запреты

- ❌ Не дублировать функционал SpeechPlaybackIntegration
- ❌ Не создавать новые режимы приложения
- ❌ Не нарушать EventBus архитектуру
- ❌ Не работать с модулями напрямую

## 📊 Производительность

### Время отклика

- **Предзаписанное аудио**: < 100ms
- **TTS fallback**: 1-3 секунды
- **Fallback tone**: < 50ms

### Память

- **Предзаписанное аудио**: ~200KB (2-3 секунды)
- **TTS кэш**: ~200KB
- **Fallback tone**: < 1KB

## 🔍 Мониторинг

### Логи

```
🎵 [WELCOME_PLAYER] Начинаю воспроизведение приветствия
✅ [WELCOME_PLAYER] Предзаписанное аудио воспроизведено успешно
🎵 [WELCOME_INTEGRATION] Приветствие воспроизведено: prerecorded, 2.5s
```

### Метрики

- Время воспроизведения
- Метод воспроизведения (prerecorded/tts/fallback)
- Успешность воспроизведения
- Ошибки и их типы

## 🆘 Устранение неполадок

### Частые проблемы

1. **Аудио не воспроизводится**
   - Проверить разрешения микрофона
   - Проверить наличие аудио файла
   - Проверить SpeechPlaybackIntegration

2. **TTS не работает**
   - Проверить macOS say command
   - Проверить права доступа
   - Проверить fallback tone

3. **Медленное воспроизведение**
   - Проверить задержку в конфигурации
   - Проверить производительность системы
   - Проверить размер аудио файла

### Отладка

```python
# Включить подробные логи
logging.getLogger('modules.welcome_message').setLevel(logging.DEBUG)

# Проверить состояние плеера
print(player.get_status())

# Проверить конфигурацию
print(config.__dict__)
```
