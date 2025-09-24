# 🏛️ macOS Certification Requirements для Audio Device Manager

## 📋 Обзор требований

Данный документ содержит полный список требований для сертификации и нотаризации модуля `audio_device_manager` в соответствии с политиками Apple.

## 🔐 Требования безопасности

### 1. **Code Signing (Подписание кода)**

#### 1.1 Обязательные сертификаты
- **Developer ID Application** - для подписания исполняемых файлов
- **Developer ID Installer** - для подписания PKG пакетов
- **Apple Development** - для разработки и тестирования

#### 1.2 Hardened Runtime
```xml
<!-- Обязательные entitlements для Hardened Runtime -->
<key>com.apple.security.cs.allow-jit</key>
<true/>
<key>com.apple.security.cs.allow-unsigned-executable-memory</key>
<true/>
<key>com.apple.security.cs.disable-executable-page-protection</key>
<true/>
<key>com.apple.security.cs.disable-library-validation</key>
<true/>
```

#### 1.3 Требования к подписанию
- Все исполняемые файлы должны быть подписаны
- Библиотеки (.dylib, .so) должны быть подписаны
- Использование timestamp для подписей
- Валидация подписей перед распространением

### 2. **Entitlements (Права доступа)**

#### 2.1 Аудио устройства
```xml
<key>com.apple.security.device.audio-input</key>
<true/>
<key>com.apple.security.device.audio-output</key>
<true/>
```
**Обоснование:** Модуль управляет аудио устройствами ввода и вывода

#### 2.2 Сетевые соединения
```xml
<key>com.apple.security.network.client</key>
<true/>
```
**Обоснование:** Для проверки обновлений и связи с серверами

#### 2.3 Файловая система
```xml
<key>com.apple.security.files.user-selected.read-write</key>
<true/>
```
**Обоснование:** Для сохранения конфигурации и логов

#### 2.4 Системные события
```xml
<key>com.apple.security.automation.apple-events</key>
<true/>
```
**Обоснование:** Для управления системными настройками аудио

### 3. **Privacy Requirements (Требования конфиденциальности)**

#### 3.1 Usage Descriptions
```xml
<key>NSMicrophoneUsageDescription</key>
<string>Audio Device Manager needs microphone access to manage audio input devices and monitor audio levels.</string>

<key>NSCameraUsageDescription</key>
<string>Audio Device Manager may need camera access for device management and system integration.</string>
```

#### 3.2 Data Collection
- **Не собираем** персональные данные пользователей
- **Не передаем** данные третьим лицам
- **Локальное хранение** всех настроек и логов
- **Прозрачность** в использовании аудио устройств

## 🏛️ Notarization Requirements (Требования нотаризации)

### 1. **Обязательные проверки**

#### 1.1 Malware Scanning
- Приложение сканируется на наличие вредоносного ПО
- Все библиотеки проверяются на подозрительную активность
- Статический анализ кода на предмет уязвимостей

#### 1.2 Code Integrity
- Проверка целостности всех исполняемых файлов
- Валидация цифровых подписей
- Проверка соответствия Hardened Runtime

#### 1.3 API Usage
- Использование только разрешенных API
- Отсутствие приватных или deprecated API
- Соответствие App Store Guidelines

### 2. **Требования к отправке**

#### 2.1 Формат пакета
- **PKG** (Package) формат для установки
- Подписанный Developer ID Installer сертификатом
- Включение всех необходимых компонентов

#### 2.2 Метаданные
```xml
<key>CFBundleIdentifier</key>
<string>com.yourcompany.audio-device-manager</string>
<key>CFBundleVersion</key>
<string>1.0.0</string>
<key>CFBundleShortVersionString</key>
<string>1.0.0</string>
<key>LSMinimumSystemVersion</key>
<string>10.15</string>
```

### 3. **Процесс нотаризации**

#### 3.1 Отправка на проверку
```bash
xcrun notarytool submit "AudioDeviceManager-1.0.0-signed.pkg" \
    --apple-id "your-apple-id@example.com" \
    --password "app-specific-password" \
    --team-id "YOUR_TEAM_ID" \
    --wait
```

#### 3.2 Прикрепление тикета
```bash
xcrun stapler staple "AudioDeviceManager-1.0.0-signed.pkg"
```

#### 3.3 Проверка статуса
```bash
xcrun stapler validate "AudioDeviceManager-1.0.0-signed.pkg"
```

## 🔍 Gatekeeper Requirements

### 1. **Проверки безопасности**

#### 1.1 Quarantine Removal
- Приложение должно быть подписано Developer ID
- Нотаризация должна быть завершена успешно
- Тикет нотаризации должен быть прикреплен

#### 1.2 System Integration
- Корректная работа с системными аудио API
- Безопасное управление устройствами
- Отсутствие попыток обхода системных ограничений

### 2. **Пользовательский опыт**

#### 2.1 Установка
- Простой процесс установки через PKG
- Отсутствие запросов на дополнительные разрешения
- Автоматическая настройка после установки

#### 2.2 Запуск
- Мгновенный запуск без задержек
- Отсутствие предупреждений безопасности
- Корректная работа с системными настройками

## 📱 App Store Connect (если применимо)

### 1. **Метаданные приложения**

#### 1.1 Описание
```
Audio Device Manager - автоматическое управление аудио устройствами на macOS. 
Автоматически переключается между наушниками, колонками и другими устройствами 
при подключении/отключении. Поддерживает Bluetooth, USB и встроенные устройства.
```

#### 1.2 Ключевые слова
- audio
- device
- manager
- bluetooth
- headphones
- automation
- macos

#### 1.3 Категория
- **Primary:** Utilities
- **Secondary:** Productivity

### 2. **Скриншоты и ресурсы**

#### 2.1 Обязательные размеры
- 1280x800 (Mac App Store)
- 2560x1600 (Mac App Store Retina)
- 512x512 (App Icon)

#### 2.2 Контент
- Главный экран приложения
- Настройки и конфигурация
- Список доступных устройств
- Статистика и мониторинг

## 🧪 Тестирование

### 1. **Функциональное тестирование**

#### 1.1 Базовые функции
- [ ] Обнаружение аудио устройств
- [ ] Автоматическое переключение
- [ ] Ручное управление устройствами
- [ ] Сохранение настроек

#### 1.2 Интеграция с системой
- [ ] Работа с Bluetooth устройствами
- [ ] Поддержка USB устройств
- [ ] Встроенные динамики и микрофон
- [ ] Системные уведомления

### 2. **Тестирование безопасности**

#### 2.1 Code Signing
- [ ] Все файлы подписаны корректно
- [ ] Валидация подписей проходит
- [ ] Hardened Runtime активен

#### 2.2 Notarization
- [ ] Пакет принят на нотаризацию
- [ ] Тикет прикреплен успешно
- [ ] Gatekeeper проверка пройдена

### 3. **Тестирование на разных системах**

#### 3.1 Версии macOS
- [ ] macOS 10.15 (Catalina)
- [ ] macOS 11.0 (Big Sur)
- [ ] macOS 12.0 (Monterey)
- [ ] macOS 13.0 (Ventura)
- [ ] macOS 14.0 (Sonoma)

#### 3.2 Аппаратное обеспечение
- [ ] Intel Mac
- [ ] Apple Silicon (M1/M2)
- [ ] Различные аудио устройства
- [ ] Bluetooth адаптеры

## 📋 Чеклист готовности к сертификации

### Предварительные требования:
- [ ] Apple Developer Account активен
- [ ] Все необходимые сертификаты установлены
- [ ] App-Specific Password создан
- [ ] Team ID получен

### Разработка:
- [ ] Hardened Runtime включен
- [ ] Все entitlements настроены
- [ ] Privacy descriptions добавлены
- [ ] Code signing настроен

### Сборка:
- [ ] Приложение собирается без ошибок
- [ ] Все файлы подписаны корректно
- [ ] PKG пакет создан
- [ ] Метаданные заполнены

### Нотаризация:
- [ ] Пакет отправлен на нотаризацию
- [ ] Нотаризация завершена успешно
- [ ] Тикет прикреплен
- [ ] Gatekeeper проверка пройдена

### Тестирование:
- [ ] Функциональное тестирование пройдено
- [ ] Тестирование безопасности завершено
- [ ] Тестирование на разных системах
- [ ] Пользовательский опыт проверен

## 🚨 Частые проблемы и решения

### 1. **Ошибки подписания**
```bash
# Очистка кэша подписания
sudo rm -rf /var/db/receipts/com.apple.pkg.*
sudo rm -rf /Library/Receipts/com.apple.pkg.*
```

### 2. **Ошибки нотаризации**
```bash
# Проверка логов нотаризации
xcrun notarytool log --apple-id "$APPLE_ID" --password "$APP_PASSWORD" --team-id "$TEAM_ID"
```

### 3. **Gatekeeper блокировка**
```bash
# Временное отключение для тестирования
sudo spctl --master-disable

# Включение обратно
sudo spctl --master-enable
```

### 4. **Проблемы с entitlements**
- Проверьте синтаксис XML
- Убедитесь в корректности ключей
- Проверьте соответствие функциональности

## 📞 Поддержка и ресурсы

### Apple Developer Resources:
- [Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)
- [Notarization Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)

### Полезные команды:
```bash
# Проверка подписи
codesign --verify --verbose "path/to/app"

# Проверка entitlements
codesign -d --entitlements - "path/to/app"

# Проверка Gatekeeper
spctl --assess --verbose "path/to/app"

# Проверка нотаризации
xcrun stapler validate "path/to/pkg"
```

---

**Готово к сертификации!** 🏛️✨
