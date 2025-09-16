# gRPC Client Module

Модульный gRPC клиент с расширенными возможностями для Nexy Voice Assistant.

## 🚀 Возможности

- **Модульная архитектура** - легко расширяемый и поддерживаемый код
- **Retry механизмы** - автоматические повторные попытки с различными стратегиями
- **Health Check** - мониторинг состояния соединения
- **Гибкая конфигурация** - настройка для разных окружений
- **Thread-safe операции** - безопасная работа в многопоточной среде
- **Метрики и мониторинг** - детальная статистика работы
- **macOS интеграция** - полная поддержка macOS требований

## 📁 Структура модуля

```
grpc_client/
├── core/                    # Основные компоненты
│   ├── grpc_client.py      # Главный клиент
│   ├── retry_manager.py    # Менеджер повторных попыток
│   ├── health_checker.py   # Система проверки здоровья
│   ├── connection_manager.py # Менеджер соединений
│   └── types.py            # Типы данных
├── config/                  # Конфигурация
│   └── grpc_config.py      # Настройки для разных окружений
├── tests/                   # Тесты
│   └── test_grpc_client.py # Тесты модуля
├── macos/                   # macOS требования
│   ├── entitlements/       # Разрешения
│   ├── info/               # Info.plist
│   ├── scripts/            # Скрипты сборки
│   └── packaging/          # Упаковка
└── __init__.py             # Точка входа модуля
```

## 🔧 Использование

### Базовое использование

```python
from grpc_client import create_default_grpc_client

# Создание клиента
client = create_default_grpc_client()

# Подключение к серверу
await client.connect()

# Выполнение операций
result = await client.execute_with_retry(some_operation)

# Отключение
await client.disconnect()
```

### Конфигурация для разных окружений

```python
from grpc_client import create_grpc_client

# Локальная разработка
local_client = create_grpc_client("local")

# Production
prod_client = create_grpc_client("production")

# Тестирование
test_client = create_grpc_client("test")
```

### Кастомная конфигурация

```python
from grpc_client import GrpcClient

config = {
    'servers': {
        'custom': {
            'address': '192.168.1.100',
            'port': 50051,
            'use_ssl': True,
            'timeout': 60
        }
    },
    'max_retry_attempts': 5,
    'retry_strategy': 'exponential'
}

client = GrpcClient(config)
```

## ⚙️ Конфигурация

### Серверы

```python
servers = {
    'local': {
        'address': '127.0.0.1',
        'port': 50051,
        'use_ssl': False,
        'timeout': 30,
        'retry_attempts': 3,
        'retry_delay': 1.0
    },
    'production': {
        'address': '20.151.51.172',
        'port': 50051,
        'use_ssl': False,
        'timeout': 120,
        'retry_attempts': 5,
        'retry_delay': 2.0
    }
}
```

### Retry стратегии

- `NONE` - без повторных попыток
- `LINEAR` - линейная задержка
- `EXPONENTIAL` - экспоненциальная задержка
- `FIBONACCI` - задержка по числам Фибоначчи

## 📊 Мониторинг

### Состояния соединения

- `DISCONNECTED` - отключен
- `CONNECTING` - подключение
- `CONNECTED` - подключен
- `RECONNECTING` - переподключение
- `FAILED` - ошибка

### Метрики

```python
metrics = client.get_metrics()
print(f"Всего соединений: {metrics.total_connections}")
print(f"Успешных: {metrics.successful_connections}")
print(f"Неудачных: {metrics.failed_connections}")
print(f"Среднее время ответа: {metrics.average_response_time}")
```

## 🧪 Тестирование

```bash
# Запуск тестов
python -m pytest grpc_client/tests/

# Запуск конкретного теста
python -m pytest grpc_client/tests/test_grpc_client.py -v
```

## 🍎 macOS сборка

```bash
# Сборка для macOS
cd grpc_client/macos/scripts
./build.sh

# Результат: dist/grpc_client.pkg
```

## 📋 Требования

- Python 3.9+
- grpcio
- grpcio-tools
- PyInstaller (для сборки)
- macOS 10.15+ (для сборки)

## 🔒 Безопасность

- Поддержка TLS/SSL соединений
- Безопасное управление сертификатами
- Валидация входных данных
- Защита от атак типа "thundering herd"

## 🚀 Производительность

- Асинхронные операции
- Connection pooling
- Эффективные retry стратегии
- Минимальное потребление памяти

## 📝 Логирование

```python
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('grpc_client')

# Логи автоматически выводятся для:
# - Подключений/отключений
# - Retry попыток
# - Health check результатов
# - Ошибок
```

## 🤝 Интеграция

Модуль легко интегрируется с другими компонентами Nexy:

```python
from grpc_client import create_default_grpc_client
# state_management удален - используйте основной StateManager из main.py

# Создание клиента
grpc_client = create_default_grpc_client()

# Интеграция с state management
state_manager = create_default_state_manager(grpc_client=grpc_client)
```

## 📄 Лицензия

MIT License - см. LICENSE файл для деталей.

## 👥 Разработчики

Nexy Development Team

## 📞 Поддержка

Для вопросов и поддержки обращайтесь к команде разработки.
