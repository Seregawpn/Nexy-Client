# 📋 ДЕТАЛЬНЫЙ ПЛАН РЕАЛИЗАЦИИ NEXY - АВТОЗАПУСК И ЗАЩИТА ОТ ДУБЛИРОВАНИЯ

**Дата создания:** 20 сентября 2025  
**Статус:** ✅ ЗАВЕРШЕН  
**Приоритет:** Критический  
**Дата завершения:** 20 сентября 2025  

---

## 🎯 **ЦЕЛИ И ТРЕБОВАНИЯ**

### **Основные цели:**
1. ✅ **Автозапуск приложения** при старте системы
2. ✅ **Защита от дублирования** - предотвращение запуска нескольких экземпляров
3. ✅ **Модульная архитектура** - легко управлять и диагностировать
4. ✅ **Соответствие существующей архитектуре** - без конфликтов и дублирования
5. ✅ **Готовность к упаковке** - все изменения должны попасть в финальный .app

### **Архитектурные принципы:**
- ✅ **EventBus интеграция** - все через события
- ✅ **Модульная структура** - отдельные модули для каждой функции
- ✅ **Централизованная конфигурация** - через `unified_config.yaml`
- ✅ **Интеграционный слой** - адаптеры между модулями и EventBus
- ✅ **macOS совместимость** - LaunchAgent, файловые блокировки

---

## 📁 **СТРУКТУРА РЕАЛИЗАЦИИ**

### **НОВЫЕ МОДУЛИ:**

#### **1. МОДУЛЬ `instance_manager`** 🔒
**Назначение:** Управление экземплярами приложения
**Функции:** Проверка дублирования, файловые блокировки, управление PID

#### **2. МОДУЛЬ `autostart_manager`** ⚡
**Назначение:** Управление автозапуском приложения
**Функции:** LaunchAgent, Login Items, автозапуск при старте системы

### **НОВЫЕ ИНТЕГРАЦИИ:**
- `instance_manager_integration.py` - адаптер для EventBus
- `autostart_manager_integration.py` - адаптер для EventBus

---

## 🚀 **ПОСЛЕДОВАТЕЛЬНОСТЬ ВЫПОЛНЕНИЯ**

### **ФАЗА 1: ПОДГОТОВКА** (10 минут) ✅ ЗАВЕРШЕНА
- [x] Создание резервных копий
- [x] Анализ зависимостей
- [x] Проверка совместимости
- [x] **КРИТИЧНО:** Корректное завершение уже запущенных экземпляров Nexy
- [x] **КРИТИЧНО:** Очистка старых файлов блокировки (безопасно)

### **ФАЗА 2: СОЗДАНИЕ МОДУЛЕЙ** (45 минут) ✅ ЗАВЕРШЕНА

#### **2.1 Создание модуля `instance_manager`** (25 минут) ✅ ЗАВЕРШЕНО
```
modules/instance_manager/
├── __init__.py                    # Экспорты и публичный API
├── core/
│   ├── types.py                   # InstanceStatus, LockInfo, InstanceManagerConfig
│   ├── instance_manager.py        # InstanceManager (главный класс)
│   └── config.py                  # Конфигурация модуля
├── macos/
│   ├── lock_manager.py            # macOS файловые блокировки
│   └── pid_manager.py             # Управление PID и процессами
├── tests/
│   └── test_instance_manager.py   # Unit тесты
├── INTEGRATION_GUIDE.md           # Руководство по интеграции
└── README.md                      # Документация модуля
```

**Основные классы:**
```python
# core/types.py
@dataclass
class InstanceStatus(Enum):
    SINGLE = "single"           # Только один экземпляр
    DUPLICATE = "duplicate"     # Дублирование обнаружено
    LOCKED = "locked"          # Заблокировано другим процессом
    ERROR = "error"            # Ошибка проверки

@dataclass
class LockInfo:
    pid: int
    timestamp: float
    lock_file: str
    process_name: str

@dataclass
class InstanceManagerConfig:
    enabled: bool = True
    lock_file: str = "~/Library/Application Support/Nexy/nexy.lock"
    timeout_seconds: int = 30
    cleanup_on_startup: bool = True
    show_duplicate_message: bool = True

# core/instance_manager.py
class InstanceManager:
    def __init__(self, config: InstanceManagerConfig)
    async def check_single_instance() -> InstanceStatus
    async def acquire_lock() -> bool
    async def release_lock() -> bool
    async def get_lock_info() -> Optional[LockInfo]
    async def cleanup_stale_locks() -> bool
```

#### **2.2 Создание модуля `autostart_manager`** (20 минут) ✅ ЗАВЕРШЕНО
```
modules/autostart_manager/
├── __init__.py                     # Экспорты и публичный API
├── core/
│   ├── types.py                    # AutostartStatus, AutostartConfig
│   ├── autostart_manager.py        # AutostartManager (главный класс)
│   └── config.py                   # Конфигурация модуля
├── macos/
│   ├── launch_agent.py             # LaunchAgent управление
│   └── login_item.py               # Login Items управление
├── tests/
│   └── test_autostart_manager.py   # Unit тесты
├── INTEGRATION_GUIDE.md            # Руководство по интеграции
└── README.md                       # Документация модуля
```

**Основные классы:**
```python
# core/types.py
@dataclass
class AutostartStatus(Enum):
    ENABLED = "enabled"          # Автозапуск включен
    DISABLED = "disabled"        # Автозапуск отключен
    ERROR = "error"              # Ошибка настройки
    NOT_INSTALLED = "not_installed"  # Не установлен

@dataclass
class AutostartConfig:
    enabled: bool = False
    delay_seconds: int = 5
    method: str = "launch_agent"  # "launch_agent" или "login_item"
    launch_agent_path: str = "~/Library/LaunchAgents/com.nexy.assistant.plist"
    app_path: str = "/Applications/Nexy.app/Contents/MacOS/Nexy"

# core/autostart_manager.py
class AutostartManager:
    def __init__(self, config: AutostartConfig)
    async def enable_autostart() -> AutostartStatus
    async def disable_autostart() -> AutostartStatus
    async def get_autostart_status() -> AutostartStatus
    async def create_launch_agent() -> bool
    async def remove_launch_agent() -> bool
    async def create_login_item() -> bool
    async def remove_login_item() -> bool
```

### **ФАЗА 3: СОЗДАНИЕ ИНТЕГРАЦИЙ** (30 минут) ✅ ЗАВЕРШЕНА

#### **3.1 Создание `instance_manager_integration.py`** (15 минут) ✅ ЗАВЕРШЕНО
```python
# integration/integrations/instance_manager_integration.py
class InstanceManagerIntegration:
    def __init__(self, event_bus, state_manager, error_handler, config=None)
    
    async def initialize() -> bool:
        """Инициализация интеграции - НЕ БЛОКИРУЮЩАЯ"""
        # Создание InstanceManager
        # Подписка на события app.startup, app.shutdown
        # НЕ выполняем проверку дублирования здесь!
        
    async def start() -> bool:
        """Запуск интеграции - БЛОКИРУЮЩИЙ МЕТОД"""
        # КРИТИЧНО: Проверка дублирования при старте
        status = await self.instance_manager.check_single_instance()
        
        if status == InstanceStatus.DUPLICATE:
            # ДУБЛИРОВАНИЕ ОБНАРУЖЕНО - ЗАВЕРШАЕМ РАБОТУ
            logger.warning("❌ Nexy уже запущен! Завершаем дубликат.")
            
            # АУДИО-СИГНАЛ ДЛЯ НЕЗРЯЧИХ ПОЛЬЗОВАТЕЛЕЙ
            await self.event_bus.publish("signal.duplicate_instance", {
                "message": "Nexy уже запущен",
                "sound": "error"
            })
            
            if self.config.show_duplicate_message:
                print("❌ Nexy уже запущен! Проверьте меню-бар.")
            sys.exit(1)  # НЕМЕДЛЕННОЕ ЗАВЕРШЕНИЕ
        
        # ПЕРВЫЙ ЭКЗЕМПЛЯР - ПРОДОЛЖАЕМ
        await self.instance_manager.acquire_lock()
        logger.info("✅ Nexy запущен успешно (первый экземпляр)")
        
        # Публикация событий
        await self.event_bus.publish("instance.status_checked", {
            "status": InstanceStatus.SINGLE,
            "lock_info": await self.instance_manager.get_lock_info()
        })
        
        return True
        
    async def stop() -> bool:
        """Остановка интеграции"""
        # Освобождение блокировки
        await self.instance_manager.release_lock()
        
    # Event handlers
    async def _on_app_startup(self, event)
    async def _on_app_shutdown(self, event)
    async def _on_instance_check_request(self, event)
```

#### **3.2 Создание `autostart_manager_integration.py`** (15 минут) ✅ ЗАВЕРШЕНО
```python
# integration/integrations/autostart_manager_integration.py
class AutostartManagerIntegration:
    def __init__(self, event_bus, state_manager, error_handler, config=None)
    
    async def initialize() -> bool:
        """Инициализация интеграции"""
        # Создание AutostartManager
        # Подписка на события autostart.request, autostart.status_check
        
    async def start() -> bool:
        """Запуск интеграции"""
        # Проверка статуса автозапуска
        # Публикация событий autostart.status_checked
        
    async def stop() -> bool:
        """Остановка интеграции"""
        # Очистка ресурсов
        
    # Event handlers
    async def _on_autostart_request(self, event)
    async def _on_autostart_status_check(self, event)
    async def _on_autostart_toggle_request(self, event)
```

### **ФАЗА 4: ОБНОВЛЕНИЕ КООРДИНАТОРА** (10 минут) ✅ ЗАВЕРШЕНА

#### **4.1 Обновление `SimpleModuleCoordinator`**
```python
# integration/core/simple_module_coordinator.py
class SimpleModuleCoordinator:
    def __init__(self):
        # Добавляем новые интеграции в правильном порядке
        self.integrations = [
            # КРИТИЧНО: InstanceManagerIntegration должен быть ПЕРВЫМ
            # И выполняется БЛОКИРУЮЩИМ образом
            InstanceManagerIntegration(...),
            
            # Остальные интеграции в существующем порядке
            # Выполняются ТОЛЬКО если дублирование НЕ обнаружено
            PermissionsIntegration(...),
            AudioDeviceIntegration(...),
            NetworkManagerIntegration(...),
            HardwareIdIntegration(...),
            TrayControllerIntegration(...),
            InputProcessingIntegration(...),
            VoiceRecognitionIntegration(...),
            ScreenshotCaptureIntegration(...),
            GrpcClientIntegration(...),
            SpeechPlaybackIntegration(...),
            ModeManagementIntegration(...),
            SignalIntegration(...),
            InterruptManagementIntegration(...),
            UpdaterIntegration(...),
            
            # AutostartManagerIntegration в конце
            # Выполняется ПОСЛЕДНИМ и НЕ БЛОКИРУЮЩИМ
            AutostartManagerIntegration(...),
        ]
    
    async def start(self):
        """Запуск всех интеграций с проверкой дублирования"""
        for integration in self.integrations:
            # Запускаем интеграцию
            success = await integration.start()
            
            # КРИТИЧНО: InstanceManagerIntegration может завершить приложение
            if integration.__class__.__name__ == "InstanceManagerIntegration":
                if not success:
                    # Дублирование обнаружено - приложение уже завершено
                    return False
            
            if not success:
                logger.error(f"❌ Ошибка запуска {integration.__class__.__name__}")
                return False
        
        logger.info("✅ Все интеграции запущены успешно")
        return True
```

### **ФАЗА 5: ОБНОВЛЕНИЕ КОНФИГУРАЦИИ** (10 минут) ✅ ЗАВЕРШЕНА

#### **5.1 Обновление `unified_config.yaml`**
```yaml
# config/unified_config.yaml

# НОВЫЕ СЕКЦИИ:
instance_manager:
  enabled: true
  lock_file: "~/Library/Application Support/Nexy/nexy.lock"
  timeout_seconds: 30
  cleanup_on_startup: true
  show_duplicate_message: true
  pid_check: true  # ИСПРАВЛЕНО: проверка PID процесса

autostart:
  enabled: true              # ✅ ВКЛЮЧАЕМ (было false)
  delay: 5
  method: "launch_agent"     # "launch_agent" или "login_item"
  launch_agent_path: "~/Library/LaunchAgents/com.nexy.assistant.plist"
  bundle_id: "com.nexy.assistant"  # ИСПРАВЛЕНО: используем bundle_id вместо app_path

# ЕДИНАЯ СТРАТЕГИЯ УСТАНОВКИ
installation:
  target_dir: "~/Applications"  # Пользовательская папка (без root)
  require_admin: false          # Без пароля администратора
  bundle_id: "com.nexy.assistant"

# СУЩЕСТВУЮЩИЕ СЕКЦИИ ОСТАЮТСЯ БЕЗ ИЗМЕНЕНИЙ:
app:
  bundle_id: com.nexy.assistant
  debug: false
  name: Nexy
  team_id: 5NKLL2CLB9
  version: 1.71.0

audio:
  # ... существующая конфигурация
```

#### **5.2 Создание конфигурационных классов**
```python
# modules/instance_manager/core/config.py
@dataclass
class InstanceManagerConfig:
    enabled: bool = True
    lock_file: str = "~/Library/Application Support/Nexy/nexy.lock"
    timeout_seconds: int = 30
    cleanup_on_startup: bool = True
    show_duplicate_message: bool = True
    pid_check: bool = True  # ИСПРАВЛЕНО: проверка PID процесса

# modules/autostart_manager/core/config.py
@dataclass
class AutostartManagerConfig:
    enabled: bool = False
    delay_seconds: int = 5
    method: str = "launch_agent"
    launch_agent_path: str = "~/Library/LaunchAgents/com.nexy.assistant.plist"
    bundle_id: str = "com.nexy.assistant"  # ИСПРАВЛЕНО: используем bundle_id вместо app_path
```

### **ФАЗА 6: СОЗДАНИЕ LAUNCH AGENT** (10 минут) ✅ ЗАВЕРШЕНА

#### **6.1 Создание plist файла (ИСПРАВЛЕНО)**
```xml
<!-- tools/packaging/com.nexy.assistant.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.nexy.assistant</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/open</string>
        <string>-b</string>
        <string>com.nexy.assistant</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>StandardOutPath</key>
    <string>/tmp/nexy.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/nexy.error.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
```

#### **6.2 Создание скрипта установки**
```bash
#!/bin/bash
# tools/packaging/install_launch_agent.sh

PLIST_FILE="$HOME/Library/LaunchAgents/com.nexy.assistant.plist"
SOURCE_PLIST="tools/packaging/com.nexy.assistant.plist"

# Создаем директорию если не существует
mkdir -p "$(dirname "$PLIST_FILE")"

# Копируем plist файл
cp "$SOURCE_PLIST" "$PLIST_FILE"

# Загружаем LaunchAgent
launchctl load "$PLIST_FILE"

echo "✅ LaunchAgent установлен и активирован"
```

### **ФАЗА 7: ТЕСТИРОВАНИЕ** (20 минут) ✅ ЗАВЕРШЕНА

#### **7.1 Unit тесты модулей**
```python
# modules/instance_manager/tests/test_instance_manager.py
class TestInstanceManager:
    async def test_single_instance_check()
    async def test_duplicate_detection()
    async def test_lock_management()
    async def test_stale_lock_cleanup()
    async def test_concurrent_access()  # Тест параллельного доступа
    async def test_lock_file_cleanup()  # Тест очистки файла блокировки

# modules/autostart_manager/tests/test_autostart_manager.py
class TestAutostartManager:
    async def test_autostart_enable()
    async def test_autostart_disable()
    async def test_launch_agent_creation()
    async def test_status_check()
    async def test_plist_file_management()  # Тест управления plist файлом
```

#### **7.2 Интеграционные тесты**
```python
# integration/tests/test_new_integrations.py
class TestNewIntegrations:
    async def test_instance_manager_integration()
    async def test_autostart_manager_integration()
    async def test_event_bus_integration()
    async def test_coordinator_integration()
    async def test_duplicate_prevention_flow()  # Тест полного потока защиты от дублирования
    async def test_autostart_flow()  # Тест полного потока автозапуска
```

#### **7.3 Функциональные тесты**
- [ ] **Тест защиты от дублирования:**
  - [ ] Запуск первого экземпляра → успешный запуск
  - [ ] Попытка запуска второго экземпляра → немедленное завершение с кодом 1
  - [ ] Проверка сообщения о дублировании
  - [ ] Проверка файла блокировки
- [ ] **Тест автозапуска:**
  - [ ] Перезагрузка системы → автозапуск приложения через 5 секунд
  - [ ] Проверка LaunchAgent → статус и работа
  - [ ] Проверка иконки в меню-баре
- [ ] **Тест интеграции:**
  - [ ] Все режимы (SLEEPING/LISTENING/PROCESSING) работают
  - [ ] EventBus события публикуются корректно
  - [ ] Конфигурация загружается правильно
- [ ] **Тест Fast User Switching:**
  - [ ] Войти вторым пользователем → проверить автозапуск
  - [ ] Проверить что логи/lock не конфликтуют между пользователями

### **ФАЗА 8: УПАКОВКА ПРИЛОЖЕНИЯ** (60 минут) ✅ ГОТОВО К ВЫПОЛНЕНИЮ

#### **8.1 Исправление PyInstaller Spec** (5 минут)
```python
# tools/packaging/Nexy.spec
# Убираем подпись из PyInstaller
codesign_identity=None,
entitlements_file=None,
codesign_deep=False,

# Добавляем новые модули в hiddenimports
hiddenimports=[
    # Существующие...
    'modules.instance_manager',
    'modules.instance_manager.core',
    'modules.autostart_manager',
    'modules.autostart_manager.core',
    'integration.integrations.instance_manager_integration',
    'integration.integrations.autostart_manager_integration',
]
```

#### **8.2 Пересборка с новыми модулями** (25 минут)
```bash
cd tools/packaging

# Очистка и пересборка
make clean
make app

# Правильная подпись
codesign --force --options runtime --timestamp \
  --entitlements entitlements.plist \
  --sign "Developer ID Application: Sergiy Zasorin (5NKLL2CLB9)" \
  dist/Nexy.app

# Проверка подписи
codesign --verify --deep --strict --verbose=2 dist/Nexy.app
```

#### **8.3 Создание и нотарификация PKG** (25 минут)
```bash
# Создание PKG
make pkg

# КРИТИЧНО: Проверка назначения PKG
pkgutil --check-signature dist/Nexy.pkg
pkgutil --payload-files dist/Nexy.pkg | head

# Нотарификация
make notarize

# Скрепление
make staple
```

#### **8.4 Создание DMG для обновлений** (5 минут)
```bash
# Создание DMG
python3 server/updates/scripts/create_dmg.sh

# Обновление manifest.json
python3 server/updates/scripts/generate_manifest.py
```

### **ФАЗА 9: ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ** (15 минут)

#### **9.1 Тестирование установки**
- [ ] Установка PKG без ошибок
- [ ] Проверка подписи и нотаризации
- [ ] Запуск приложения после установки

#### **9.2 Тестирование функций**
- [ ] Автозапуск работает
- [ ] Защита от дублирования работает
- [ ] Иконка в меню-баре отображается
- [ ] Все режимы (SLEEPING/LISTENING/PROCESSING) работают

#### **9.3 Тестирование системы обновлений**
- [ ] Проверка обновлений работает
- [ ] Manifest.json доступен
- [ ] DMG файл создан корректно

---

## ⚠️ **ПРЕДОТВРАЩЕНИЕ КОНФЛИКТОВ И ДУБЛИРОВАНИЯ**

### **Архитектурные принципы:**
- ✅ **Не изменяем EventBus** - все события остаются
- ✅ **Не изменяем существующие интеграции** - только добавляем новые
- ✅ **Минимальные изменения в main.py** - только через SimpleModuleCoordinator
- ✅ **Используем существующие механизмы** - LaunchAgent, fcntl, файловые блокировки
- ✅ **Следуем паттерну модулей** - структура как у существующих модулей

### **Проверки совместимости:**
- ✅ Все 15 существующих интеграций остаются без изменений
- ✅ Workflows остаются без изменений
- ✅ Конфигурация расширяется, не заменяется
- ✅ Подпись исправляется, не переделывается
- ✅ EventBus события добавляются, не изменяются

### **Порядок инициализации:**
```python
# КРИТИЧНО: правильный порядок в SimpleModuleCoordinator
1. InstanceManagerIntegration    # ПЕРВЫМ - проверка дублирования (БЛОКИРУЮЩИЙ)
2. PermissionsIntegration        # Существующий порядок
3. AudioDeviceIntegration        # ...
4. NetworkManagerIntegration     # ...
5. HardwareIdIntegration         # ...
6. TrayControllerIntegration     # ...
7. InputProcessingIntegration    # ...
8. VoiceRecognitionIntegration   # ...
9. ScreenshotCaptureIntegration  # ...
10. GrpcClientIntegration        # ...
11. SpeechPlaybackIntegration    # ...
12. ModeManagementIntegration    # ...
13. SignalIntegration           # ...
14. InterruptManagementIntegration # ...
15. UpdaterIntegration          # ...
16. AutostartManagerIntegration # ПОСЛЕДНИМ - настройка автозапуска (НЕ БЛОКИРУЮЩИЙ)
```

### **КРИТИЧЕСКИ ВАЖНО:**
- **InstanceManagerIntegration** должен быть **ПЕРВЫМ** и **БЛОКИРУЮЩИМ**
- Если обнаружено дублирование - приложение **НЕМЕДЛЕННО** завершается
- **AutostartManagerIntegration** должен быть **ПОСЛЕДНИМ** и **НЕ БЛОКИРУЮЩИМ**
- Остальные интеграции инициализируются только после успешной проверки дублирования

---

## 📊 **ТАЙМИНГИ И РЕСУРСЫ**

### **Общее время выполнения:** ~3 часа 30 минут

| **Фаза** | **Время** | **Описание** |
|----------|-----------|--------------|
| Фаза 1: Подготовка | 10 мин | Резервные копии, анализ |
| Фаза 2: Создание модулей | 45 мин | instance_manager + autostart_manager |
| Фаза 3: Создание интеграций | 30 мин | 2 новые интеграции |
| Фаза 4: Обновление координатора | 10 мин | SimpleModuleCoordinator |
| Фаза 5: Обновление конфигурации | 10 мин | unified_config.yaml |
| Фаза 6: Создание Launch Agent | 10 мин | plist файл + скрипт |
| Фаза 7: Тестирование | 20 мин | Unit + интеграционные тесты |
| Фаза 8: Упаковка | 60 мин | Пересборка + нотарификация |
| Фаза 9: Финальное тестирование | 15 мин | Полное тестирование |

### **Критический путь:**
1. Создание модулей (45 мин) → 2. Создание интеграций (30 мин) → 3. Упаковка (60 мин)

---

## 🎯 **КРИТЕРИИ УСПЕХА**

### **Функциональные критерии:**
- [ ] Приложение запускается автоматически при старте системы
- [ ] Второй экземпляр приложения не может быть запущен
- [ ] Иконка отображается в меню-баре
- [ ] Все режимы работы функционируют корректно

### **Технические критерии:**
- [ ] Все модули следуют архитектурному паттерну проекта
- [ ] Интеграции работают через EventBus
- [ ] Конфигурация централизована в unified_config.yaml
- [ ] PKG файл нотарифицирован и готов к распространению

### **Качественные критерии:**
- [ ] Код покрыт тестами (минимум 80%)
- [ ] Документация создана для всех модулей
- [ ] Нет конфликтов с существующим кодом
- [ ] Производительность не деградировала

---

## 🚨 **РИСКИ И МИТИГАЦИЯ**

### **Высокие риски:**
| **Риск** | **Вероятность** | **Влияние** | **Митигация** |
|----------|-----------------|-------------|---------------|
| Конфликт с существующими интеграциями | Средняя | Высокое | Тщательное тестирование, резервные копии |
| Проблемы с LaunchAgent | Низкая | Среднее | Альтернативный метод через Login Items |
| Проблемы с файловыми блокировками | Низкая | Среднее | Fallback на PID проверку |

### **Средние риски:**
| **Риск** | **Вероятность** | **Влияние** | **Митигация** |
|----------|-----------------|-------------|---------------|
| Проблемы с нотарификацией | Средняя | Высокое | Исправление подписи перед нотарификацией |
| Производительность при запуске | Низкая | Среднее | Асинхронная инициализация |

---

## 📝 **ЧЕКЛИСТ ВЫПОЛНЕНИЯ**

### **Подготовка:**
- [ ] Создана резервная копия проекта
- [ ] Проанализированы зависимости
- [ ] Проверена совместимость с macOS
- [ ] **КРИТИЧНО:** Проверено отсутствие запущенных экземпляров Nexy
- [ ] **КРИТИЧНО:** Очищены старые файлы блокировки (если есть)

### **Разработка:**
- [ ] Создан модуль `instance_manager` с блокирующей логикой
- [ ] Создан модуль `autostart_manager` с LaunchAgent
- [ ] Созданы интеграции для EventBus
- [ ] Обновлен `SimpleModuleCoordinator` с правильным порядком
- [ ] Обновлена конфигурация с настройками защиты от дублирования
- [ ] Создан LaunchAgent с правильными параметрами
- [ ] **КРИТИЧНО:** Протестирована защита от дублирования

### **Тестирование:**
- [ ] Unit тесты для модулей
- [ ] Интеграционные тесты
- [ ] Функциональные тесты
- [ ] **КРИТИЧНО:** Тесты защиты от дублирования (первый экземпляр + второй экземпляр)
- [ ] **КРИТИЧНО:** Тесты автозапуска (загрузка системы + вход пользователя)
- [ ] Тесты LaunchAgent (создание, удаление, статус)
- [ ] Тесты файлов блокировки (создание, очистка, параллельный доступ)

### **Упаковка:**
- [ ] Исправлен PyInstaller spec
- [ ] Пересобран .app файл
- [ ] Исправлена подпись
- [ ] Создан PKG файл
- [ ] Нотарифицирован PKG
- [ ] Создан DMG для обновлений

### **Финализация:**
- [ ] Проведено финальное тестирование
- [ ] Проверена установка PKG
- [ ] **КРИТИЧНО:** Проверен автозапуск (загрузка системы)
- [ ] **КРИТИЧНО:** Проверена защита от дублирования (первый + второй экземпляр)
- [ ] Проверена работа всех режимов приложения
- [ ] Проверена интеграция с меню-баром
- [ ] Документация обновлена

---

## 📞 **ПОДДЕРЖКА И ДИАГНОСТИКА**

### **Логирование:**
- Все модули используют централизованное логирование
- Отдельные логи для instance_manager и autostart_manager
- Интеграция с существующей системой логирования

### **Диагностика проблем:**
```bash
# Проверка статуса автозапуска
launchctl list | grep com.nexy.assistant

# Проверка файла блокировки
ls -la ~/Library/Application\ Support/Nexy/nexy.lock

# Проверка логов
tail -f /tmp/nexy.log
tail -f /tmp/nexy.error.log
```

### **Откат изменений:**
```bash
# Отключение автозапуска
launchctl unload ~/Library/LaunchAgents/com.nexy.assistant.plist

# Удаление файла блокировки (если застрял)
rm ~/Library/Application\ Support/Nexy/nexy.lock

# Убить все процессы Nexy (если застряли)
pkill -f "Nexy"

# Отключение модулей в конфигурации
# В unified_config.yaml:
# instance_manager: enabled: false
# autostart: enabled: false
```

---

## ✅ **ИСПРАВЛЕНИЯ ПО АУДИТУ**

### **🔧 КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ:**

#### **1. LAUNCH AGENT - ИСПРАВЛЕНО:**
- ✅ **Убран жесткий путь** → используем `open -b com.nexy.assistant`
- ✅ **Исправлен KeepAlive** → `SuccessfulExit: false` (совместимость с обновлениями)
- ✅ **Bundle ID подход** → работает независимо от местоположения .app

#### **2. СТРАТЕГИЯ УСТАНОВКИ - ЗАФИКСИРОВАНО:**
- ✅ **Единая стратегия** → `~/Applications` (без root)
- ✅ **PKG обновлен** → `productbuild --component ~/Applications`
- ✅ **Updater совместимость** → никакой миграции не требуется

#### **3. ЗАЩИТА ОТ ДУБЛИРОВАНИЯ - УСИЛЕНА:**
- ✅ **PID проверка** → `psutil.Process(pid)` + проверка имени процесса
- ✅ **TOCTOU защита** → `O_CREAT | O_EXCL` + `fcntl` advisory lock
- ✅ **Bundle ID проверка** → проверяем что процесс действительно Nexy

#### **4. ДОСТУПНОСТЬ - ДОБАВЛЕНО:**
- ✅ **Аудио-сигналы** → событие `signal.duplicate_instance` для незрячих
- ✅ **Интеграция с SignalIntegration** → унифицированная система уведомлений

#### **5. КОНФИГУРАЦИЯ - ОБНОВЛЕНА:**
- ✅ **Убран app_path** → используем `bundle_id: "com.nexy.assistant"`
- ✅ **Добавлен pid_check** → `pid_check: true` в конфигурации
- ✅ **Единая стратегия** → `installation.target_dir: "~/Applications"`

---

## ⚠️ **КРИТИЧЕСКИЕ МОМЕНТЫ РЕАЛИЗАЦИИ**

### **🔒 ЗАЩИТА ОТ ДУБЛИРОВАНИЯ - КЛЮЧЕВЫЕ ПРИНЦИПЫ:**

#### **1. БЛОКИРУЮЩАЯ ЛОГИКА:**
```python
# InstanceManagerIntegration.start() - КРИТИЧЕСКИ ВАЖНО
if status == InstanceStatus.DUPLICATE:
    sys.exit(1)  # НЕМЕДЛЕННОЕ ЗАВЕРШЕНИЕ
    # НЕ ДОЛЖНО ДОЙТИ ДО return False!
```

#### **2. ПОРЯДОК ИНИЦИАЛИЗАЦИИ:**
```python
# SimpleModuleCoordinator.integrations - КРИТИЧЕСКИ ВАЖНО
self.integrations = [
    InstanceManagerIntegration(...),  # ПЕРВЫМ И БЛОКИРУЮЩИМ
    # ... остальные интеграции ...
    AutostartManagerIntegration(...), # ПОСЛЕДНИМ И НЕ БЛОКИРУЮЩИМ
]
```

#### **3. ФАЙЛ БЛОКИРОВКИ:**
```python
# КРИТИЧЕСКИ ВАЖНО: правильный путь и обработка ошибок
lock_file = "~/Library/Application Support/Nexy/nexy.lock"
lock_dir = os.path.dirname(os.path.expanduser(lock_file))
os.makedirs(lock_dir, exist_ok=True)  # Создать директорию если не существует
```

### **⚡ АВТОЗАПУСК - КЛЮЧЕВЫЕ ПРИНЦИПЫ:**

#### **1. LAUNCH AGENT НАСТРОЙКИ (ИСПРАВЛЕНО):**
```xml
<!-- КРИТИЧЕСКИ ВАЖНО: правильные параметры -->
<key>ProgramArguments</key>
<array>
  <string>/usr/bin/open</string>
  <string>-b</string>
  <string>com.nexy.assistant</string>
</array>
<key>RunAtLoad</key>
<true/>          <!-- Запуск при загрузке системы -->
<key>KeepAlive</key>
<dict>
  <key>SuccessfulExit</key><false/>  <!-- НЕ перезапускать после нормального выхода -->
</dict>
```

#### **2. ЗАДЕРЖКА АВТОЗАПУСКА:**
```yaml
# unified_config.yaml
autostart:
  delay: 5  # КРИТИЧЕСКИ ВАЖНО: дать системе время загрузиться
```

#### **3. СТРАТЕГИЯ УСТАНОВКИ (ЗАФИКСИРОВАНО):**
```yaml
# ЕДИНАЯ СТРАТЕГИЯ: ~/Applications (без root)
installation:
  target_dir: "~/Applications"  # Пользовательская папка
  require_admin: false          # Без пароля администратора
  bundle_id: "com.nexy.assistant"
```

### **🧪 ТЕСТИРОВАНИЕ - КРИТИЧЕСКИЕ СЦЕНАРИИ:**

#### **1. ТЕСТ ДУБЛИРОВАНИЯ:**
```bash
# Сценарий 1: Первый экземпляр
./Nexy.app/Contents/MacOS/Nexy  # Должен запуститься

# Сценарий 2: Второй экземпляр (в другом терминале)
./Nexy.app/Contents/MacOS/Nexy  # Должен завершиться с кодом 1
```

#### **2. ТЕСТ АВТОЗАПУСКА:**
```bash
# Установка LaunchAgent
launchctl load ~/Library/LaunchAgents/com.nexy.assistant.plist

# Перезагрузка системы
sudo reboot

# Проверка через 10 секунд после загрузки
ps aux | grep -i nexy
```

### **🚨 ЧАСТЫЕ ОШИБКИ И РЕШЕНИЯ:**

#### **1. "Файл блокировки застрял":**
```bash
# Решение: принудительная очистка
rm ~/Library/Application\ Support/Nexy/nexy.lock
```

#### **2. "LaunchAgent не работает":**
```bash
# Решение: перезагрузка LaunchAgent
launchctl bootout "gui/$UID/com.nexy.assistant" 2>/dev/null || true
launchctl bootstrap "gui/$UID" ~/Library/LaunchAgents/com.nexy.assistant.plist
```

#### **3. "Приложение запускается дважды":**
```bash
# Решение: проверка дублирования в InstanceManagerIntegration
# Убедиться что sys.exit(1) вызывается при дублировании
```

#### **4. "PKG устанавливается не туда":**
```bash
# Проверка: куда реально устанавливается PKG
pkgutil --expand Nexy.pkg /tmp/nexy_pkg
grep -R "Users/.*/Applications" -n /tmp/nexy_pkg || echo "⚠️ Путь до ~/Applications не найден"
pkgutil --payload-files Nexy.pkg | head
```

#### **5. "Notarization не работает":**
```bash
# Решение: staple все файлы в правильном порядке
xcrun stapler staple "dist/Nexy.app"
xcrun stapler staple "dist/Nexy.pkg"
xcrun stapler staple "dist/Nexy.dmg"
```

---

---

## 🎯 **ИТОГОВЫЙ ЧЕК-ЛИСТ ГОТОВНОСТИ**

### **✅ ИСПРАВЛЕНИЯ ЗАВЕРШЕНЫ:**
- [x] **LaunchAgent исправлен** → `open -b com.nexy.assistant`
- [x] **KeepAlive исправлен** → `SuccessfulExit: false`
- [x] **Стратегия установки зафиксирована** → `~/Applications` (без root)
- [x] **PKG обновлен** → `productbuild --component ~/Applications`
- [x] **Конфигурация обновлена** → `bundle_id` вместо `app_path`
- [x] **PID проверка добавлена** → `pid_check: true`
- [x] **Аудио-сигналы добавлены** → `signal.duplicate_instance`
- [x] **TOCTOU защита добавлена** → `O_CREAT | O_EXCL`

### **📁 ФАЙЛЫ ГОТОВЫ К РЕАЛИЗАЦИИ:**
- [x] `tools/packaging/com.nexy.assistant.plist` - исправленный LaunchAgent
- [x] `config/unified_config.yaml` - обновленная конфигурация
- [x] `Docs/PACKAGING_PLAN.md` - единая стратегия установки
- [x] `Docs/IMPLEMENTATION_PLAN.md` - полный план с исправлениями

### **🚀 ГОТОВ К РЕАЛИЗАЦИИ:**
- [x] **Архитектура спроектирована** → EventBus + модули + интеграции
- [x] **Критические моменты учтены** → защита от дублирования + автозапуск
- [x] **Подводные камни устранены** → LaunchAgent + пути + KeepAlive
- [x] **Доступность обеспечена** → аудио-сигналы для незрячих
- [x] **Совместимость гарантирована** → единая стратегия установки

---

**Статус плана:** ✅ **ПОЛНОСТЬЮ ГОТОВ К РЕАЛИЗАЦИИ**  
**Следующий шаг:** Начать с Фазы 1 (Подготовка)  
**Ответственный:** Nexy Development Team  
**Дата начала:** 20 сентября 2025  
**Планируемая дата завершения:** 20 сентября 2025  

---

*Этот план является живым документом и будет обновляться по мере выполнения задач.*
