# 🔄 Система автообновлений для Nexy Server

## 📋 Обзор

Сервер теперь включает в себя систему автообновлений Sparkle, которая позволяет клиентским приложениям автоматически обновляться без вмешательства пользователя.

## 🏗️ Структура

```
server/
├── main.py                    # Основной сервер с обновлениями
├── update_server.py           # Сервер обновлений
├── grpc_server.py            # gRPC сервер
├── updates/                  # Файлы обновлений
│   ├── appcast.xml           # AppCast XML (отдельный файл!)
│   ├── downloads/            # DMG файлы
│   │   └── Nexy_1.71.0.dmg
│   └── keys/                 # Ключи для подписи
│       ├── ed25519_private.pem
│       └── ed25519_public.pem
└── setup_server.sh           # Скрипт настройки
```

## 🚀 Запуск

### 1. Настройка сервера
```bash
cd server
chmod +x setup_server.sh
./setup_server.sh
```

### 2. Запуск сервера
```bash
python3 main.py
```

## 📡 Endpoints

После запуска сервера доступны следующие endpoints:

- **HTTP сервер** (порт 80):
  - `http://localhost:80/` - Главная страница
  - `http://localhost:80/health` - Health check
  - `http://localhost:80/status` - Статус сервера

- **Сервер обновлений** (порт 8080):
  - `http://localhost:8080/` - Главная страница обновлений
  - `http://localhost:8080/appcast.xml` - AppCast XML
  - `http://localhost:8080/downloads/` - DMG файлы
  - `http://localhost:8080/health` - Health check обновлений
  - `http://localhost:8080/api/versions` - API версий

- **gRPC сервер** (порт 50051):
  - Основной функционал приложения

## 🔧 Настройка обновлений

### Обновление AppCast XML
Отредактируйте файл `updates/appcast.xml` для добавления новых версий:

```xml
<item>
    <title>Nexy 1.72.0</title>
    <description>
        <![CDATA[
        <h2>Что нового в версии 1.72.0:</h2>
        <ul>
            <li>Новые функции</li>
            <li>Исправления ошибок</li>
        </ul>
        ]]>
    </description>
    <pubDate>Mon, 08 Sep 2025 18:00:00 +0000</pubDate>
    <enclosure url="http://localhost:8080/downloads/Nexy_1.72.0.dmg"
               sparkle:version="1.72.0"
               sparkle:shortVersionString="1.72.0"
               length="10485760"
               type="application/octet-stream"
               sparkle:edSignature="SIGNATURE_HERE"/>
</item>
```

### Добавление новых DMG файлов
1. Поместите новый DMG файл в `updates/downloads/`
2. Обновите AppCast XML с новой версией
3. Перезапустите сервер

## 🔐 Безопасность

- **ED25519 ключи** используются для подписи обновлений
- **HTTPS** рекомендуется для продакшн использования
- **Проверка целостности** файлов перед установкой

## 📝 Логирование

Сервер выводит подробные логи о:
- Запуске и остановке серверов
- Запросах к AppCast XML
- Загрузке DMG файлов
- Ошибках системы обновлений

## 🎯 Тестирование

### Проверка работы сервера
```bash
# Проверка HTTP сервера
curl http://localhost:80/health

# Проверка сервера обновлений
curl http://localhost:8080/health

# Проверка AppCast XML
curl http://localhost:8080/appcast.xml
```

### Тестирование с клиентом
1. Запустите сервер: `python3 main.py`
2. Запустите клиент с настроенным URL: `http://localhost:8080/appcast.xml`
3. Проверьте логи на наличие обновлений

## ⚠️ Важные замечания

- **AppCast XML** - отдельный файл, легко редактируется
- **DMG файлы** - должны быть реальными для продакшн
- **Ключи** - храните приватный ключ в безопасности
- **Версии** - используйте семантическое версионирование

## 🔄 Обновление системы

Для обновления системы обновлений:
1. Остановите сервер (Ctrl+C)
2. Обновите файлы
3. Запустите сервер снова

---

**Система автообновлений готова к использованию!** 🎉

