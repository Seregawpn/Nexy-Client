# 🧪 Локальное тестирование системы обновлений

## 🎯 Что настроено

### ✅ **Полностью настроено:**
1. **EdDSA ключи Sparkle** - для подписания обновлений
2. **Локальный сервер обновлений** - на `localhost:8080`
3. **AppCast XML** - с реальными подписями
4. **PKG файл** - подписан и готов к распространению
5. **Приложение** - с настроенными ключами обновлений

### 🔐 **Ключи подписания:**
- **Публичный ключ:** `yixFT+HhjLehYH6sT8riFb1etq/hpXFWNqiGkZOBHjE=`
- **Приватный ключ:** `../server/updates/keys/sparkle_private_key.pem`

## 🚀 **Запуск тестирования**

### 1. **Запустите локальный сервер обновлений:**
```bash
cd server
./start_local_update_server.sh
```

### 2. **Проверьте сервер в браузере:**
- **Главная страница:** http://localhost:8080
- **AppCast XML:** http://localhost:8080/appcast.xml
- **API проверки:** http://localhost:8080/api/update/check?current=1.70.0

### 3. **Протестируйте в приложении:**
```bash
cd client
# Запустите приложение - оно автоматически проверит обновления
/Applications/Nexy.app/Contents/MacOS/Nexy
```

## 📋 **Что происходит при тестировании:**

1. **Приложение запускается** с версией 1.71.0
2. **Sparkle проверяет** http://localhost:8080/appcast.xml
3. **Находит обновление** (если текущая версия < 1.71.0)
4. **Предлагает установить** обновление
5. **Скачивает PKG** с http://localhost:8080/downloads/
6. **Проверяет подпись** EdDSA
7. **Устанавливает обновление**

## 🔧 **Настройка для продакшена:**

### 1. **Замените localhost на реальный домен:**
```bash
# В nexy.spec
sed -i 's|http://localhost:8080|https://your-domain.com|g' nexy.spec

# В appcast.xml
sed -i 's|http://localhost:8080|https://your-domain.com|g' updates/appcast.xml
```

### 2. **Настройте SSL сертификат** на сервере

### 3. **Загрузите файлы** на продакшен сервер:
- `updates/appcast.xml`
- `updates/downloads/Nexy_AI_Voice_Assistant_v1.71.0.pkg`

## 📊 **Структура файлов:**

```
server/
├── local_update_server.py          # Локальный сервер
├── start_local_update_server.sh    # Скрипт запуска
└── updates/
    ├── appcast.xml                 # AppCast с подписями
    ├── downloads/
    │   └── Nexy_AI_Voice_Assistant_v1.71.0.pkg
    └── keys/
        ├── sparkle_private_key.pem # Приватный ключ
        ├── sparkle_public_key.pem  # Публичный ключ
        ├── generate_sparkle_keys.sh
        └── sign_update.sh
```

## 🎉 **Готово к тестированию!**

Система обновлений полностью настроена и готова к тестированию. Все компоненты работают локально, и вы можете легко перенести их на продакшен сервер.

