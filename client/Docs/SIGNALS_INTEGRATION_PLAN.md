# 🔌 Signals Integration — Implementation Plan

Дата: 18 сентября 2025
Статус: Implemented ✅

## 1) Цель
Подключить модуль `signals` к событийной системе: реагировать на события приложения и выдавать сигналы по конфигурации, без дублирования логики и без прямой работы с модулями трея/плеера в интеграции.

## 2) Роль и границы
- Интеграция — только координирует: подписывается на события EventBus, маппит их в `SignalRequest` и вызывает `SignalService.emit()`.
- Вся генерация/воспроизведение сигналов — внутри модуля `signals` (каналы).

## 3) Подписки и маппинг событий (реализовано)
| Событие | Условие | Pattern |
|---|---|---|
| app.mode_changed | mode == LISTENING | listen_start |
| voice.mic_opened | — | listen_start |
| app.mode_changed | mode == PROCESSING | processing_start (опц.) |
| playback.completed | — | done |
| grpc.request_failed | — | error |
| voice.recognition_failed | — | error |
| interrupt.request | — | cancel |
| playback.cancelled | — | cancel |

Примечания:
- Дублированные триггеры для listen_start (mode_changed и mic_opened) подавляются cooldown‑ом.
- Наличие/отсутствие конкретных сигналов регулируется конфигурацией.

## 4) Конфигурация (по умолчанию в коде; расширяемо)
```yaml
integrations:
  signals:
    enabled: true
    patterns:
      listen_start: { audio: true, visual: false, volume: 0.2, tone_hz: 880, duration_ms: 120, cooldown_ms: 300 }
      processing_start: { audio: false, visual: true }
      done: { audio: true }
      error: { audio: true }
      cancel: { audio: true }
```

## 5) API интеграции (итог)
```python
# signal_integration.py (каркас)
class SignalIntegration:
    def __init__(self, event_bus, state_manager, error_handler, signal_service, config): ...
    async def initialize(self) -> bool: ...  # подписки EventBus
    async def start(self) -> bool: ...
    async def stop(self) -> bool: ...
```

## 6) Последовательность включения в систему (выполнено)
1. Создать SignalService из модуля `signals`, сконфигурировать каналы по конфигу.
2. Создать SignalIntegration и зарегистрировать в `SimpleModuleCoordinator`.
3. Подписаться на события; включить автосигналы из таблицы маппинга.
4. Протянуть метрики/логи в ErrorHandler/LoggingManager.

## 7) Гонки и отказоустойчивость
- Per‑pattern cooldown предотвращает «дребезг» (listen_start может приходить из двух событий подряд).
- Интеграция не держит состояние сигналов; вся очередь и подавления — в сервисе.
- Любые ошибки в каналах не мешают остальной системе; публикуем `signal.failed` и логируем.

## 8) Тестирование
- Интеграционные тесты: вход в LISTENING → один сигнал, без дублей; playback.completed → done; error/cancel.
- Экстремальный кейс: серия быстрых mode_changed → только один сигнал благодаря cooldown.

## 9) Acceptance Criteria

Примечание по реализации: задействован `EventBusAudioSink`, публикующий `playback.signal` с PCM. Обработчик в `SpeechPlaybackIntegration` воспроизводит сигнал немедленно. Ошибка передачи `priority` в `EventBus.publish` исправлена.
- Интеграция не дублирует функционал модулей; все сигналы проходят через `SignalService`.
- Сигналы соответствуют конфигу; нет гонок/дублей; метрики присутствуют.
