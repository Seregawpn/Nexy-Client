# Welcome Message Module - Integration Guide

## 📋 Обзор

Модуль `welcome_message` предназначен для воспроизведения приветственного сообщения при запуске приложения Nexy AI Assistant. Использует серверную генерацию речи через Azure TTS.

## 🏗️ Архитектура

### Основные компоненты

1. **`WelcomePlayer`** - основной плеер приветствия
2. **`WelcomeAudioGenerator`** - генератор аудио (серверный)
3. **`WelcomeConfig`** - конфигурация модуля
4. **`WelcomeMessageIntegration`** - интеграция с EventBus

### Структура модуля

```
modules/welcome_message/
├── core/
│   ├── welcome_player.py          # Основной плеер
│   ├── audio_generator.py         # gRPC генератор
│   └── types.py                   # Типы данных
├── config/
│   └── welcome_config.py          # Загрузчик конфигурации
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
    use_server=True,
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
  delay_sec: 1.0
  volume: 0.8
  voice: "en-US-JennyNeural"
  sample_rate: 48000
  channels: 1
  bit_depth: 16
  use_server: true
  server_timeout_sec: 30.0
```

### Параметры конфигурации

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `enabled` | bool | true | Включить модуль приветствия |
| `text` | str | "Hi! Nexy is here. How can I help you?" | Текст приветствия |
| `use_server` | bool | true | Использовать серверную генерацию |
| `server_timeout_sec` | float | 30.0 | Таймаут RPC `GenerateWelcomeAudio` |
| `delay_sec` | float | 1.0 | Задержка перед воспроизведением |
| `volume` | float | 0.8 | Громкость воспроизведения |
| `voice` | str | "en-US-JennyNeural" | Голос для TTS |
| `sample_rate` | int | 48000 | Частота дискретизации |
| `channels` | int | 1 | Количество каналов |
| `bit_depth` | int | 16 | Разрядность |

## 🎵 Генерация аудио

Приветствие формируется на сервере (Azure TTS) через RPC `GenerateWelcomeAudio`. Локальные файлы и системные fallback'и не используются.

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

- **gRPC вызов**: 300-800ms (Azure TTS)
- **Network retry**: зависит от настроек `GrpcClient`

### Память

- **Память буфера**: зависит от длины приветствия (~200KB на 2-3 секунды PCM)

## 🔍 Мониторинг

### Логи

```
🎵 [WELCOME_PLAYER] Начинаю воспроизведение приветствия
✅ [WELCOME_PLAYER] Серверное приветствие воспроизведено успешно
🎵 [WELCOME_INTEGRATION] Приветствие воспроизведено: server, 2.5s
```

### Метрики

- Время воспроизведения
- Метод воспроизведения (`server`)
- Успешность воспроизведения
- Ошибки и их типы

## 🆘 Устранение неполадок

### Частые проблемы

1. **Аудио не воспроизводится**
   - Проверить доступность gRPC сервера
   - Убедиться, что `GrpcClient` подключается (логи `modules.grpc_client`)
   - Проверить, что `GenerateWelcomeAudio` возвращает чанки (серверные логи)

2. **Высокая задержка**
   - Проверить сетевое соединение
   - Оптимизировать параметр `server_timeout_sec`
   - Убедиться в доступности Azure TTS
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
