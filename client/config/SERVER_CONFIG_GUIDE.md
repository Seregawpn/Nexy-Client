# 🎯 Централизованная конфигурация серверов Nexy

## 📋 Обзор

Теперь у нас есть **единая система управления серверами** с автоматической синхронизацией всех конфигурационных файлов!

## 🚀 Быстрый старт

### Изменить IP-адрес сервера:
```bash
# Изменить production сервер
python config/change_server.py 192.168.1.100 production

# Изменить local сервер  
python config/change_server.py 127.0.0.1 local

# Изменить fallback сервер
python config/change_server.py backup.example.com fallback
```

### Показать текущую конфигурацию:
```bash
python config/server_config_sync.py --show --environment production
```

### Синхронизировать все файлы:
```bash
python config/server_config_sync.py --sync --environment production
```

## 🏗️ Архитектура

### Единый источник истины
**`unified_config.yaml`** - единственное место для настройки серверов:

```yaml
servers:
  grpc_servers:
    local:
      host: 127.0.0.1
      port: 50051
      ssl: false
    production:
      host: 20.151.51.172  # ⚠️ ИЗМЕНИТЕ ЭТОТ IP НА НУЖНЫЙ
      port: 50051
      ssl: false
    fallback:
      host: backup.nexy.ai
      port: 443
      ssl: true
```

### Автоматическая синхронизация
- **`server_config_sync.py`** - синхронизирует все конфигурационные файлы
- **`change_server.py`** - удобный CLI для изменения IP-адресов
- **Автогенерация** - `network_config.yaml` создается автоматически
- **Обновление модулей** - хардкод в `grpc_client` обновляется автоматически

## 📁 Структура файлов

```
config/
├── unified_config.yaml          # 🎯 ЕДИНЫЙ ИСТОЧНИК ИСТИНЫ
├── server_config_sync.py        # 🔄 Автоматическая синхронизация
├── change_server.py             # 🚀 CLI для изменения серверов
├── network_config.yaml          # 🌐 Автогенерируется
└── unified_config_loader.py     # 🔧 Загрузчик конфигурации
```

## ⚠️ Важные правила

### ✅ ДЕЛАЙ:
- Изменяй серверы ТОЛЬКО через `python config/change_server.py`
- Используй `unified_config.yaml` как единый источник истины
- Проверяй синхронизацию после изменений

### ❌ НЕ ДЕЛАЙ:
- НЕ редактируй `network_config.yaml` вручную
- НЕ изменяй хардкод в модулях напрямую
- НЕ дублируй настройки серверов в разных файлах

## 🔧 Компоненты системы

### ServerConfigSynchronizer
- Синхронизирует все конфигурационные файлы
- Обновляет хардкод в модулях
- Обеспечивает согласованность настроек

### change_server.py CLI
- Удобный интерфейс для изменения IP-адресов
- Автоматическая синхронизация после изменений
- Проверка корректности конфигурации

### UnifiedConfigLoader
- Загружает конфигурацию из `unified_config.yaml`
- Поддерживает новую структуру `servers.grpc_servers`
- Обеспечивает обратную совместимость

## 🎯 Преимущества

- **🎯 Единая точка управления:** Изменение IP только в одном месте
- **🔄 Автоматическая синхронизация:** Все файлы обновляются автоматически
- **🚀 Простота использования:** Одна команда для изменения сервера
- **🛡️ Предотвращение ошибок:** Нет риска рассинхронизации конфигураций
- **📋 Прозрачность:** Все настройки серверов в одном месте

## 🚨 Устранение неполадок

### Проблема: Конфигурация не синхронизируется
**Решение:**
```bash
python config/server_config_sync.py --sync --environment production
```

### Проблема: Неправильный IP в модулях
**Решение:**
```bash
# Изменить IP и синхронизировать
python config/change_server.py <правильный_ip> production
```

### Проблема: Ошибки в network_config.yaml
**Решение:**
```bash
# Пересоздать файл
python config/server_config_sync.py --sync --environment production
```

## 📚 Дополнительная информация

- **Архитектурный обзор:** `Docs/ARCHITECTURE_OVERVIEW.md`
- **Текущий статус:** `Docs/CURRENT_STATUS_REPORT.md`
- **Правила разработки:** `.cursorrules`
