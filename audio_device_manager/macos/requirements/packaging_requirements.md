# 📦 ТРЕБОВАНИЯ ДЛЯ MACOS УПАКОВКИ AUDIO_DEVICE_MANAGER

## 🎯 УПАКОВКА ПРИЛОЖЕНИЯ

### Зависимости для включения:
- `PyObjC` (Core Audio, Foundation, AppKit, SystemConfiguration, Quartz)
- `SwitchAudioSource` (командная строка для переключения устройств)
- `asyncio` (асинхронные операции)
- `logging` (логирование)
- `typing` (типизация)
- `dataclasses` (структуры данных)
- `enum` (перечисления)
- `subprocess` (выполнение команд)
- `json` (конфигурация)
- `re` (регулярные выражения)

### Файлы для включения:
- `audio_device_manager/core/` (вся папка)
- `audio_device_manager/config/` (вся папка)
- `audio_device_manager/macos/` (вся папка)
- `audio_device_manager/__init__.py`
- `audio_device_manager/README.md`

### Скрытые импорты (hiddenimports):
- `audio_device_manager.core.device_manager`
- `audio_device_manager.core.device_monitor`
- `audio_device_manager.core.device_switcher`
- `audio_device_manager.core.types`
- `audio_device_manager.config.device_priorities`
- `audio_device_manager.macos.core_audio_bridge`
- `audio_device_manager.macos.device_detector`
- `audio_device_manager.macos.switchaudio_bridge`

---

## 🔐 ПОДПИСАНИЕ КОДА (Code Signing)

### Entitlements (разрешения):
- `com.apple.security.device.audio-input` - доступ к микрофонам
- `com.apple.security.device.audio-output` - доступ к динамикам
- `com.apple.security.device.audio-unit` - работа с Core Audio
- `com.apple.security.device.bluetooth` - управление Bluetooth устройствами
- `com.apple.security.device.usb` - управление USB устройствами
- `com.apple.security.device.system-events` - системные события
- `com.apple.security.network.client` - сетевое соединение
- `com.apple.security.files.user-selected.read-write` - доступ к файлам
- `com.apple.security.files.downloads.read-write` - доступ к загрузкам
- `com.apple.security.temporary-exception.files.absolute-path.read-write` - временные файлы
- `com.apple.security.cs.allow-jit` - JIT компиляция
- `com.apple.security.cs.allow-unsigned-executable-memory` - выполнение кода
- `com.apple.security.cs.debugger` - отладка
- `com.apple.security.cs.allow-dyld-environment-variables` - переменные окружения
- `com.apple.security.device.audio-settings` - настройки аудио
- `com.apple.security.automation.apple-events` - Apple Events

### Требования к сертификату:
- **Developer ID Application** (для распространения вне App Store)
- **Developer ID Installer** (для PKG пакетов)
- Действующий сертификат от Apple Developer Program
- Валидная цепочка сертификатов

### Параметры подписания:
- `--force` - принудительное подписание
- `--sign "Developer ID Application: [Name]"` - идентификатор сертификата
- `--entitlements` - файл разрешений
- `--options runtime` - включение Hardened Runtime
- `--timestamp` - временная метка

---

## 🏷️ СЕРТИФИКАЦИЯ (Hardened Runtime)

### Обязательные настройки:
- Включить Hardened Runtime (`--options runtime`)
- Отключить JIT компиляцию (кроме разрешенных случаев)
- Ограничить выполнение кода только подписанными библиотеками
- Включить проверку целостности кода
- Ограничить доступ к системным ресурсам

### Исключения для аудио модуля:
- Разрешить JIT для Python интерпретатора
- Разрешить выполнение динамически загружаемых модулей
- Разрешить доступ к Core Audio API
- Разрешить выполнение системных команд (SwitchAudioSource)

---

## 🎫 НОТАРИЗАЦИЯ (Notarization)

### Требования к пакету:
- Подписанный PKG или DMG файл
- Включенный Hardened Runtime
- Все зависимости подписаны
- Валидная цепочка сертификатов

### Процесс нотаризации:
1. **Загрузка в Apple:**
   - `xcrun notarytool submit` - загрузка пакета
   - `--apple-id` - Apple ID разработчика
   - `--password` - App-Specific Password
   - `--team-id` - Team ID

2. **Проверка статуса:**
   - `xcrun notarytool info` - проверка статуса
   - `--apple-id` - Apple ID
   - `--password` - App-Specific Password

3. **Прикрепление тикета:**
   - `xcrun stapler staple` - прикрепление тикета
   - `--verbose` - подробный вывод

### Дополнительные требования:
- **App-Specific Password** для Apple ID
- **Team ID** из Apple Developer Account
- **Bundle ID** должен соответствовать сертификату
- **Версия** должна быть уникальной для каждого релиза

---

## 📦 PKG УПАКОВКА

### Структура пакета:
- `/usr/local/bin/audio_device_manager` - исполняемый файл
- `/usr/local/lib/audio_device_manager/` - библиотеки модуля
- `/usr/local/share/audio_device_manager/` - конфигурация и ресурсы

### Метаданные пакета:
- **Identifier:** `com.nexy.audio-device-manager`
- **Version:** `1.0.0`
- **Install Location:** `/usr/local/bin`
- **Minimum OS Version:** `10.15`

### Скрипты установки:
- **preinstall** - проверка зависимостей
- **postinstall** - настройка разрешений
- **preuninstall** - остановка сервисов
- **postuninstall** - очистка файлов

---

## ⚠️ ВАЖНЫЕ ОСОБЕННОСТИ ДЛЯ AUDIO_DEVICE_MANAGER

### Специфичные требования:
- **SwitchAudioSource** должен быть установлен в системе
- **Core Audio** API требует специальных разрешений
- **Bluetooth** устройства требуют дополнительных entitlements
- **Системные настройки** аудио требуют особых разрешений

### Потенциальные проблемы:
- Конфликты с существующими аудио драйверами
- Ограничения Sandbox для доступа к аудио устройствам
- Необходимость пользовательских разрешений для Bluetooth
- Зависимость от системных утилит (SwitchAudioSource)

### Рекомендации:
- Тестировать на чистой системе macOS
- Проверять совместимость с разными версиями macOS
- Валидировать работу с различными аудио устройствами
- Убедиться в корректной работе после перезагрузки

---

## ✅ ИТОГОВЫЙ ЧЕКЛИСТ

### Упаковка:
- [ ] Все зависимости включены
- [ ] Скрытые импорты настроены
- [ ] Файлы ресурсов включены
- [ ] Конфигурация корректна

### Подписание:
- [ ] Сертификат Developer ID Application
- [ ] Entitlements файл создан
- [ ] Hardened Runtime включен
- [ ] Все библиотеки подписаны

### Нотаризация:
- [ ] App-Specific Password настроен
- [ ] Team ID указан
- [ ] Пакет загружен в Apple
- [ ] Тикет прикреплен

### Тестирование:
- [ ] Работа на чистой системе
- [ ] Совместимость с macOS версиями
- [ ] Работа с различными устройствами
- [ ] Корректность после перезагрузки

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

### Документация Apple:
- [Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)
- [Hardened Runtime](https://developer.apple.com/documentation/security/hardened_runtime)
- [Notarization](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)

### Полезные команды:
```bash
# Проверка подписи
codesign -dv --verbose=4 audio_device_manager

# Проверка entitlements
codesign -d --entitlements - audio_device_manager

# Проверка нотаризации
spctl -a -v audio_device_manager
```

---

*Документ создан: $(date)*
*Версия модуля: 1.0.0*
*Автор: Nexy Development Team*
