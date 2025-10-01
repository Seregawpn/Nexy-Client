# 🔧 Единая конфигурация Nexy AI Assistant

## 📋 Обзор

Теперь у нас есть **единая система конфигурации** с автоматической синхронизацией всех настроек!

## 🎯 Как это работает

### **1. Единый источник истины**
- **`unified_config.yaml`** - единственный файл для всех настроек
- Изменяете в одном месте → применяется везде автоматически

### **2. Автоматическая синхронизация**
- **`unified_config_loader.py`** - загрузчик с кэшированием
- **`server_config_sync.py`** - синхронизирует все файлы при изменениях

### **3. Обратная совместимость**
- Все настройки централизованы в `unified_config.yaml`
- Существующий код продолжает работать без изменений

## 🚀 Использование

### **Изменение настроек:**
1. Редактируйте `unified_config.yaml`
2. Запустите синхронизацию:
   ```bash
   python3 config/server_config_sync.py --sync
   ```

### **В коде приложения:**
```python
from config.unified_config_loader import unified_config

# Получить версию (используется везде)
version = unified_config.get_version()

# Получить AppCast URL (автоматически синхронизируется)
appcast_url = unified_config.get_appcast_url()

# Получить настройки gRPC
grpc_config = unified_config.get_grpc_config("production")

# Получить все настройки аудио
audio_config = unified_config.get_audio_config()
```

## 📁 Структура файлов

```
config/
├── unified_config.yaml          # 🎯 ЕДИНЫЙ ИСТОЧНИК ИСТИНЫ
├── unified_config_loader.py     # Загрузчик конфигурации
├── server_config_sync.py        # Автоматическая синхронизация серверов
├── change_server.py             # CLI для изменения IP серверов
├── logging_config.yaml          # Устарел - используйте unified_config.yaml
├── network_config.yaml          # Автогенерируется из unified_config.yaml
└── README.md                    # Эта документация
```

## ✨ Преимущества

✅ **Единое место изменений** - меняете в `unified_config.yaml`  
✅ **Автоматическая синхронизация** - все файлы обновляются автоматически  
✅ **Консистентность** - нет конфликтов между файлами  
✅ **Обратная совместимость** - старый код работает  
✅ **Кэширование** - быстрая загрузка настроек  
✅ **Типизация** - четкие интерфейсы для доступа  

## 🔄 Примеры синхронизации

### **Изменение версии:**
```yaml
# unified_config.yaml
app:
  version: "1.71.0"  # Меняем здесь
```

После синхронизации версия обновится во всех файлах:
- `sparkle_handler.py`
- `test_update_with_mock_sparkle.py`
- `test_update_standalone.py`
- `test_update_manager.py`

### **Изменение AppCast URL:**
```yaml
# unified_config.yaml
network:
  appcast:
    base_url: "https://api.nexy.ai/updates"  # Меняем здесь
```

После синхронизации URL обновится во всех файлах:
- `simple_module_coordinator.py`
- `test_update_standalone.py`
- `test_update_manager.py`
- `config.py`

### **Изменение gRPC сервера:**
```yaml
# unified_config.yaml
network:
  grpc_servers:
    production:
      host: "new-server.nexy.ai"  # Меняем здесь
      port: 443
      ssl: true
```

Все настройки теперь централизованы в `unified_config.yaml`.

## 🎯 Результат

**Теперь при изменении любой настройки в `unified_config.yaml` все зависимые файлы автоматически обновляются!**

Больше никаких конфликтов и дублирования! 🎉
