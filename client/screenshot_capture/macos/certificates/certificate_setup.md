# Настройка сертификатов для Screenshot Capture

## 📋 **ОБЗОР**

Данный документ описывает процесс настройки сертификатов для подписи и нотаризации модуля `screenshot_capture` на macOS.

## 🔐 **ТРЕБУЕМЫЕ СЕРТИФИКАТЫ**

### **1. Developer ID Application Certificate**
- **Назначение**: Подпись приложения для распространения вне App Store
- **Тип**: Developer ID Application
- **Срок действия**: 1 год
- **Обновление**: Ежегодно

### **2. Apple Developer Account**
- **Требования**: Активная подписка Apple Developer Program
- **Стоимость**: $99/год
- **Функции**: Доступ к сертификатам, нотаризация, распространение

## 🛠️ **ПРОЦЕСС НАСТРОЙКИ**

### **Шаг 1: Создание сертификата**

1. **Войдите в Apple Developer Portal**
   ```
   https://developer.apple.com/account/
   ```

2. **Перейдите в Certificates, Identifiers & Profiles**
   - Выберите "Certificates"
   - Нажмите "+" для создания нового сертификата

3. **Выберите тип сертификата**
   - **Developer ID Application** - для подписи приложений
   - **Developer ID Installer** - для подписи PKG пакетов

4. **Создайте Certificate Signing Request (CSR)**
   ```bash
   # Откройте Keychain Access
   # Перейдите в Keychain Access > Certificate Assistant > Request a Certificate From a Certificate Authority
   # Заполните форму и сохраните CSR файл
   ```

5. **Загрузите CSR и скачайте сертификат**
   - Загрузите CSR файл в Apple Developer Portal
   - Скачайте созданный сертификат (.cer файл)
   - Дважды кликните для установки в Keychain

### **Шаг 2: Настройка переменных окружения**

Создайте файл `.env` в корне проекта:

```bash
# Apple Developer Account
APPLE_ID="your@email.com"
TEAM_ID="YOUR_TEAM_ID"
APP_PASSWORD="app-specific-password"

# Developer ID Certificates
DEVELOPER_ID="Developer ID Application: Your Name (TEAM_ID)"
INSTALLER_ID="Developer ID Installer: Your Name (TEAM_ID)"

# Bundle Identifiers
BUNDLE_ID="com.nexy.screenshot.capture"
```

### **Шаг 3: Создание App-Specific Password**

1. **Войдите в Apple ID Account**
   ```
   https://appleid.apple.com/
   ```

2. **Перейдите в Security**
   - Найдите "App-Specific Passwords"
   - Нажмите "Generate Password"

3. **Создайте пароль**
   - Название: "Nexy Screenshot Capture Notarization"
   - Скопируйте сгенерированный пароль
   - Сохраните в переменной `APP_PASSWORD`

## 🔧 **НАСТРОЙКА ПОДПИСИ**

### **1. Проверка установленных сертификатов**

```bash
# Список всех сертификатов
security find-identity -v -p codesigning

# Проверка конкретного сертификата
security find-identity -v -p codesigning | grep "Developer ID Application"
```

### **2. Настройка entitlements**

Файл `entitlements/screenshot_capture.entitlements` уже настроен с необходимыми правами:

- ✅ **Screen Recording** - для захвата скриншотов
- ✅ **Camera Access** - для доступа к экрану
- ✅ **Apple Events** - для системных событий
- ✅ **File Access** - для работы с файлами

### **3. Настройка Info.plist**

Файл `info/Info.plist` содержит:

- ✅ **Bundle Identifier** - `com.nexy.screenshot.capture`
- ✅ **Version** - `1.0.0`
- ✅ **Usage Descriptions** - описания прав доступа
- ✅ **Architecture Support** - arm64, x86_64

## 🚀 **ПРОЦЕСС СБОРКИ И ПОДПИСИ**

### **1. Сборка приложения**

```bash
cd screenshot_capture/macos/scripts
chmod +x build_macos.sh
./build_macos.sh
```

### **2. Подпись и нотаризация**

```bash
chmod +x sign_and_notarize.sh
./sign_and_notarize.sh
```

### **3. Проверка результата**

```bash
# Проверка подписи
codesign --verify --verbose "dist/Screenshot Capture.app"

# Проверка нотаризации
xcrun stapler validate "dist/Screenshot Capture.app"
```

## ⚠️ **ВАЖНЫЕ ЗАМЕЧАНИЯ**

### **Безопасность**
- **Никогда не коммитьте** сертификаты в Git
- **Используйте** .gitignore для .p12 файлов
- **Храните** пароли в безопасном месте

### **Обновление сертификатов**
- **Проверяйте** срок действия ежемесячно
- **Обновляйте** за 30 дней до истечения
- **Тестируйте** подпись после обновления

### **Устранение проблем**
- **Очищайте** Keychain при проблемах
- **Переустанавливайте** сертификаты при необходимости
- **Проверяйте** права доступа к файлам

## 📚 **ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ**

- [Apple Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)
- [Notarization Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [Developer ID Certificates](https://developer.apple.com/developer-id/)
- [Keychain Access Guide](https://support.apple.com/guide/keychain-access/)

## 🆘 **ПОДДЕРЖКА**

При возникновении проблем:

1. **Проверьте** установку сертификатов
2. **Проверьте** переменные окружения
3. **Проверьте** права доступа
4. **Обратитесь** к документации Apple

---

**Версия**: 1.0.0  
**Дата**: 2024-09-12  
**Автор**: Nexy Development Team
