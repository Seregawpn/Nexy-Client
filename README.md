# 🎤 Голосовой Ассистент для macOS

Интеллектуальный голосовой ассистент с поддержкой анализа экрана, Google Search интеграцией, использующий Google Gemini LLM и Edge TTS.

## ✨ Возможности

- 🎤 **Голосовое управление** - push-to-talk с распознаванием речи
- 🔍 **Google Search интеграция** - актуальная информация в реальном времени
- 🖥️ **Анализ экрана** - понимание контекста через скриншоты
- 🧠 **ИИ-агент** - LangChain AgentExecutor с инструментами
- 📊 **База данных** - PostgreSQL с логированием всех взаимодействий
- 🔊 **Нейронный TTS** - Microsoft Edge TTS с русскими голосами

## 🏗️ Архитектура

- **Клиент**: macOS приложение с push-to-talk логикой
- **Сервер**: gRPC сервер с LangChain + Gemini
- **База данных**: PostgreSQL с JSONB для гибкости
- **TTS**: Microsoft Edge TTS (нейронные голоса)

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Активируем виртуальное окружение
source .venv/bin/activate

# Устанавливаем зависимости для клиента
pip install -r client/requirements.txt

# Устанавливаем зависимости для сервера
pip install -r server/requirements.txt
```

### 2. Генерация Protocol Buffers

```bash
# Генерируем proto файлы для клиента
cd client
python -m grpc_tools.protoc --python_out=. --grpc_python_out=. --proto_path=. streaming.proto

# Генерируем proto файлы для сервера
cd ../server
python -m grpc_tools.protoc --python_out=. --grpc_python_out=. --proto_path=. streaming.proto
```

### 2. Настройка базы данных

#### Установка PostgreSQL
```bash
# macOS с Homebrew
brew install postgresql
brew services start postgresql

# Или скачать с официального сайта
# https://www.postgresql.org/download/macosx/
```

#### Создание базы данных
```bash
# Подключаемся к PostgreSQL
psql postgres

# Создаем базу данных
CREATE DATABASE voice_assistant_db;

# Выходим
\q
```

#### Применение схемы
```bash
# Применяем схему базы данных
psql -d voice_assistant_db -f server/database/schema.sql
```

### 3. Настройка конфигурации

Скопируйте `server/config.env.example` в `server/config.env` и заполните:

```bash
cd server
cp config.env.example config.env
```

Отредактируйте `config.env`:
```env
# Google Gemini API (получить на https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=your_gemini_api_key_here

# Google Search API (получить в Google Cloud Console)
GSEARCH_API_KEY=your_google_search_api_key_here

# Custom Search Engine ID (создать на https://cse.google.com/)
GSEARCH_CSE_ID=your_custom_search_engine_id_here

# PostgreSQL Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=voice_assistant_db
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 🔑 Получение API ключей

#### Google Gemini API
1. Перейдите на [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Создайте новый API ключ
3. Скопируйте ключ в `GOOGLE_API_KEY`

#### Google Search API
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Custom Search API
4. Создайте учетные данные (API ключ)
5. Скопируйте ключ в `GSEARCH_API_KEY`

#### Custom Search Engine
1. Перейдите на [Google Custom Search](https://cse.google.com/)
2. Создайте новую поисковую машину
3. Скопируйте Search Engine ID в `GSEARCH_CSE_ID`

### 4. Запуск системы

#### Запуск сервера
```bash
cd server
python grpc_server.py
```

#### Запуск клиента
```bash
cd client
python main.py
```

## 🎯 Управление

- **Зажмите пробел** → Активация микрофона + захват экрана
- **Удерживайте пробел** → Запись команды
- **Отпустите пробел** → Отправка команды на сервер
- **Короткое нажатие** → Прерывание речи ассистента

## 🗄️ База данных

### Структура таблиц

- **users** - Пользователи (Hardware ID)
- **sessions** - Сессии работы
- **commands** - Команды пользователей
- **llm_answers** - Ответы LLM
- **screenshots** - Метаданные скриншотов
- **performance_metrics** - Метрики производительности
- **error_logs** - Логи ошибок

### Особенности

- **UUID** для всех идентификаторов
- **JSONB** для гибких метаданных
- **Автоматические триггеры** для updated_at
- **Индексы** для быстрого поиска

## 🔧 Разработка

### Структура проекта
```
├── client/                 # Клиентская часть (macOS)
│   ├── requirements.txt    # Зависимости для клиента
│   ├── streaming.proto     # Protocol Buffers (для клиента)
│   ├── main.py            # Основной клиент
│   ├── grpc_client.py     # gRPC клиент
│   ├── stt_recognizer.py  # Распознавание речи
│   ├── screen_capture.py  # Захват экрана
│   ├── audio_player.py    # Воспроизведение
│   └── utils/             # Утилиты для клиента
│       └── hardware_id.py # Генерация Hardware ID
├── server/                 # Серверная часть (gRPC + LLM + TTS + БД)
│   ├── requirements.txt    # Зависимости для сервера
│   ├── streaming.proto     # Protocol Buffers (для сервера)
│   ├── grpc_server.py     # gRPC сервер
│   ├── text_processor.py  # Обработка LLM
│   ├── audio_generator.py # Генерация TTS
│   ├── config.py          # Конфигурация
│   ├── config.env         # Переменные окружения
│   └── database/          # База данных
│       ├── schema.sql     # Схема БД
│       └── database_manager.py # Менеджер БД
└── README.md              # Документация
```

### Тестирование

```bash
# Тест Hardware ID
python utils/hardware_id.py

# Тест базы данных
cd server
python -c "from database.database_manager import DatabaseManager; print('DB OK')"
```

### 8. 📊 Метрики и аналитика ✅ ГОТОВО
- Сбор метрик производительности
- Статистика пользователей и сессий
- Аналитика использования ассистента
- База данных PostgreSQL для хранения метрик

## 🚨 Устранение неполадок

### Ошибки подключения к БД
```bash
# Проверяем статус PostgreSQL
brew services list | grep postgresql

# Проверяем подключение
psql -h localhost -U postgres -d voice_assistant_db
```

### Ошибки gRPC
```bash
# Проверяем порт
lsof -i :50051

# Перезапускаем сервер
cd server && python grpc_server.py
```

### Ошибки Hardware ID
```bash
# Тестируем генерацию
python utils/hardware_id.py

# Проверяем права доступа
sudo system_profiler SPHardwareDataType
```

## 🔮 Планы развития

- [ ] macOS .app bundle
- [ ] Code signing и notarization
- [ ] .dmg установщик
- [ ] GitHub releases
- [ ] Веб-сайт для скачивания
- [ ] App Store (долгосрочно)

## 📝 Лицензия

MIT License - см. LICENSE файл для деталей.

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Commit изменения
4. Push в branch
5. Создайте Pull Request

## 📞 Поддержка

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Wiki**: GitHub Wiki
