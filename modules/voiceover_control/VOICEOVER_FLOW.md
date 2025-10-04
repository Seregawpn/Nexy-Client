# VoiceOver Control - Логика работы

## 🔄 Когда происходит отключение/включение VoiceOver

### 1. **Автоматическое управление по режимам приложения**

VoiceOver автоматически управляется при смене режимов приложения через EventBus:

```
Пользователь нажимает пробел → Приложение переходит в режим LISTENING
                                    ↓
                            EventBus публикует app.mode_changed
                                    ↓
                    VoiceOverDuckingIntegration.handle_mode_change()
                                    ↓
                        controller.apply_mode("listening")
                                    ↓
                    Проверка: "listening" в duck_on_modes?
                                    ↓
                                ДА → controller.duck()
                                    ↓
                            Command+F5 → VoiceOver ОТКЛЮЧАЕТСЯ
```

### 2. **Точные моменты срабатывания**

#### 🎤 **ОТКЛЮЧЕНИЕ VoiceOver (Ducking):**
- **При переходе в режим `LISTENING`** (долгое нажатие пробела)
- **При переходе в режим `PROCESSING`** (отпускание пробела)
- **При нажатии клавиши** (если `engage_on_keyboard_press: true`)

#### 🔄 **ВКЛЮЧЕНИЕ VoiceOver (Release):**
- **При переходе в режим `SLEEPING`** (завершение обработки)
- **При завершении работы приложения** (`app.shutdown`)

### 3. **Последовательность событий**

```
1. SLEEPING (VoiceOver включен, _ducked = false)
   ↓ Пользователь нажимает и удерживает пробел
2. LISTENING (VoiceOver отключается) ← Command+F5, _ducked = true
   ↓ Пользователь отпускает пробел
3. PROCESSING (VoiceOver остается отключенным, _ducked = true)
   ↓ Обработка завершена
4. SLEEPING (VoiceOver включается) ← Command+F5, _ducked = false
```

### 4. **Умная логика переключения**

**Не переключаем VoiceOver постоянно!**

- **LISTENING**: Отключаем VoiceOver только если он еще не отключен (`_ducked = false`)
- **PROCESSING**: Проверяем состояние - если уже отключен, оставляем как есть
- **SLEEPING**: Включаем VoiceOver только если он был отключен нами (`_ducked = true`)

### 5. **Конфигурация режимов**

В `unified_config.yaml`:
```yaml
voiceover_control:
  duck_on_modes:      # Когда ОТКЛЮЧАТЬ VoiceOver
    - listening
    - processing
  release_on_modes:   # Когда ВКЛЮЧАТЬ VoiceOver
    - sleeping
```

### 6. **Дополнительные триггеры**

#### При нажатии клавиши:
```python
# Если engage_on_keyboard_press: true
async def handle_keyboard_press(self, event):
    await self.controller.duck(reason="keyboard.press")
```

#### При завершении работы:
```python
async def handle_shutdown(self, event):
    await self.controller.shutdown()  # Восстанавливает VoiceOver
```

## 📊 Логи для мониторинга

### При отключении VoiceOver:
```
INFO - VoiceOverController: Ducking VoiceOver for mode listening
INFO - VoiceOverController: Using Command+F5 to disable VoiceOver (reason=mode:listening)
INFO - VoiceOverController: Command+F5 executed successfully
```

### При включении VoiceOver:
```
INFO - VoiceOverController: Releasing VoiceOver for mode sleeping
INFO - VoiceOverController: VoiceOver restored via Command+F5
```

### Когда VoiceOver уже в нужном состоянии:
```
DEBUG - VoiceOverController: VoiceOver already ducked, staying in mode processing
DEBUG - VoiceOverController: VoiceOver not ducked, staying in mode sleeping
```

## ⚙️ Настройки поведения

### В конфигурации:
```yaml
voiceover_control:
  enabled: true                    # Включить модуль
  engage_on_keyboard_press: true   # Ducking при нажатии клавиши
  debounce_seconds: 0.25          # Задержка между операциями
  debug_logging: true             # Детальное логирование
```

## 🎯 Практический пример

### Сценарий использования:
1. **Пользователь с VoiceOver** запускает Nexy
2. **VoiceOver включен** - пользователь слышит интерфейс
3. **Пользователь нажимает пробел** - начинается запись
4. **VoiceOver отключается** - нет помех для записи
5. **Пользователь отпускает пробел** - начинается обработка
6. **VoiceOver остается отключенным** - нет помех для воспроизведения ответа
7. **Обработка завершена** - VoiceOver включается обратно
8. **Пользователь снова слышит интерфейс**

## 🔍 Диагностика

### Проверить, что интеграция работает:
```bash
# В логах приложения искать:
grep "VoiceOverDuckingIntegration" logs/app.log
grep "Command+F5" logs/app.log
grep "mode:listening" logs/app.log
```

### Проверить подписки на события:
```bash
grep "app.mode_changed" logs/app.log
grep "keyboard.press" logs/app.log
```

---

## 🎉 **Итог**

**VoiceOver умно управляется при смене режимов приложения:**

- **LISTENING** → VoiceOver отключается (если еще не отключен)
- **PROCESSING** → VoiceOver остается отключенным (проверка состояния)
- **SLEEPING** → VoiceOver включается (если был отключен нами)

**Умная логика предотвращает лишние переключения VoiceOver!**

**Все происходит автоматически через EventBus без дополнительного кода!**
