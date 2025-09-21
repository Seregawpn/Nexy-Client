# 🎯 ФИНАЛЬНЫЙ ЧЕК-ЛИСТ NEXY AI ASSISTANT

**Дата:** 20 сентября 2025  
**Версия:** 3.1.0  
**Статус:** ✅ ГОТОВ К ПРОДАКШЕНУ  
**Цель:** Pre-merge gate для проверки всех критических моментов

---

## 🚨 **PRE-MERGE GATE - ОБЯЗАТЕЛЬНЫЕ ПРОВЕРКИ**

### **🔒 ЗАЩИТА ОТ ДУБЛИРОВАНИЯ**

- [ ] **InstanceManagerIntegration запускается ПЕРВЫМ** в SimpleModuleCoordinator
- [ ] **Блокирующая логика работает** - при дублировании вызывается `sys.exit(1)`
- [ ] **Файл блокировки создается** в `~/Library/Application Support/Nexy/nexy.lock`
- [ ] **PID валидация работает** - проверка `psutil.Process(pid)` и имени процесса
- [ ] **Аудио-сигнал для незрячих** - событие `signal.duplicate_instance` публикуется
- [ ] **TOCTOU защита** - используется `O_CREAT | O_EXCL` + `fcntl` advisory lock

### **⚡ АВТОЗАПУСК**

- [ ] **AutostartManagerIntegration запускается ПОСЛЕДНИМ** в SimpleModuleCoordinator
- [ ] **LaunchAgent использует bundle_id** - `open -b com.nexy.assistant` (НЕ жесткий путь)
- [ ] **KeepAlive настроен правильно** - `SuccessfulExit: false` (совместимость с обновлениями)
- [ ] **Скрипты используют правильные команды** - `launchctl bootstrap/bootout` (НЕ load/unload)
- [ ] **НЕТ app_path в конфигурации** - только `bundle_id` и `launch_agent_path`

### **📦 УПАКОВКА**

- [ ] **Staging pipeline работает** - `make all` проходит на чистой машине
- [ ] **PKG устанавливается в ~/Applications** - единая стратегия без root
- [ ] **PyInstaller spec включает новые модули** - instance_manager, autostart_manager
- [ ] **Все артефакты подписаны** - .app, .pkg, .dmg
- [ ] **Все артефакты нотарифицированы** - .app, .pkg, .dmg
- [ ] **Все артефакты stapled** - .app, .pkg, .dmg (НЕ только DMG)
- [ ] **Codesigning проходит** - `codesign --verify --deep --strict` на `dist/Nexy.app`
- [ ] **Gatekeeper проходит** - `spctl --assess -v dist/Nexy.app` после нотаризации

---

## 🔍 **РЕГРЕССИОННЫЕ ПРОВЕРКИ**

### **🔍 Поиск по репозиторию:**

- [ ] **НЕТ остатков app_path в автозапуске** - только bundle_id
- [ ] **НЕТ load/unload в скриптах** - только bootstrap/bootout
- [ ] **НЕТ жестких путей к .app** - везде bundle_id подход
- [ ] **НЕТ дублирования конфигурации** - только unified_config.yaml

### **🧪 Функциональные тесты:**

- [ ] **Тест дублирования экземпляров** - первый запускается, второй завершается с кодом 1
- [ ] **Тест автозапуска** - перезагрузка системы → приложение запускается через LaunchAgent
- [ ] **Тест Fast User Switching** - каждый пользователь получает свой автозапуск, логи не конфликтуют
- [ ] **Тест PKG payload** - `pkgutil --expand` подтверждает путь в ~/Applications
- [ ] **Тест всех режимов** - SLEEPING → LISTENING → PROCESSING → SLEEPING

---

## 📊 **АРХИТЕКТУРНЫЕ ПРОВЕРКИ**

### **🏗️ Структура проекта:**

- [ ] **17 интеграций** - все созданы и подключены
- [ ] **16 модулей** - включая instance_manager и autostart_manager
- [ ] **Правильный порядок запуска** - InstanceManager первым, AutostartManager последним
- [ ] **EventBus события** - новые события добавлены без нарушения существующих

### **⚙️ Конфигурация:**

- [ ] **unified_config.yaml обновлен** - новые секции instance_manager и autostart
- [ ] **Устаревшие секции удалены** - update_manager заменен на updater
- [ ] **Единая стратегия установки** - target_dir: ~/Applications, require_admin: false
- [ ] **Bundle ID везде** - com.nexy.assistant, никаких жестких путей

---

## 🛠️ **ТЕХНИЧЕСКИЕ ПРОВЕРКИ**

### **📦 PyInstaller:**

- [ ] **hiddenimports включает новые модули** - instance_manager.*, autostart_manager.*
- [ ] **hiddenimports включает новые интеграции** - instance_manager_integration, autostart_manager_integration
- [ ] **НЕТ codesign в spec файле** - подпись только после сборки
- [ ] **Правильная архитектура** - target_arch='arm64' (Apple Silicon)

### **🔐 Подпись и нотаризация:**

- [ ] **Developer ID Application** - для .app файла
- [ ] **Developer ID Installer** - для .pkg файла
- [ ] **Hardened Runtime** - --options runtime
- [ ] **Timestamp** - --timestamp для всех подписей
- [ ] **Entitlements** - корректные разрешения (микрофон, экран, сеть)

---

## 🎯 **КРИТЕРИИ ГОТОВНОСТИ**

### **✅ ФУНКЦИОНАЛЬНЫЕ:**
- [ ] Приложение запускается автоматически при старте системы
- [ ] Второй экземпляр приложения не может быть запущен
- [ ] Иконка отображается в меню-баре
- [ ] Все режимы работы функционируют корректно
- [ ] Push-to-Talk работает: LONG_PRESS → LISTENING → RELEASE → PROCESSING

### **✅ ТЕХНИЧЕСКИЕ:**
- [ ] Все модули следуют архитектурному паттерну проекта
- [ ] Интеграции работают через EventBus
- [ ] Конфигурация централизована в unified_config.yaml
- [ ] PKG файл нотарифицирован и готов к распространению
- [ ] Система обновлений работает (HTTP + DMG + миграция)

### **✅ КАЧЕСТВЕННЫЕ:**
- [ ] Код покрыт тестами (минимум 80%)
- [ ] Документация создана для всех модулей
- [ ] Нет конфликтов с существующим кодом
- [ ] Производительность не деградировала
- [ ] Доступность обеспечена (аудио-сигналы для незрячих)

---

## 🚨 **КРИТИЧЕСКИЕ "НЕЛЬЗЯ"**

### **❌ ЗАПРЕЩЕНО:**
- ❌ **НЕЛЬЗЯ** использовать жесткие пути к .app в LaunchAgent
- ❌ **НЕЛЬЗЯ** использовать `launchctl load/unload` (только bootstrap/bootout)
- ❌ **НЕЛЬЗЯ** смешивать `/Applications` и `~/Applications`
- ❌ **НЕЛЬЗЯ** выполнять codesign внутри PyInstaller spec
- ❌ **НЕЛЬЗЯ** степлить только DMG (все артефакты)
- ❌ **НЕЛЬЗЯ** оставлять app_path в конфигурации автозапуска
- ❌ **НЕЛЬЗЯ** запускать AutostartManagerIntegration до InstanceManagerIntegration

---

## 📋 **БЫСТРЫЕ КОМАНДЫ ДЛЯ ПРОВЕРКИ**

### **🔍 Проверка дублирования:**
```bash
# Запуск первого экземпляра
./dist/Nexy.app/Contents/MacOS/Nexy

# Попытка запуска второго (в другом терминале)
./dist/Nexy.app/Contents/MacOS/Nexy  # Должен завершиться с кодом 1
```

### **⚡ Проверка автозапуска:**
```bash
# Установка LaunchAgent
bash tools/packaging/install_launch_agent.sh

# Проверка статуса
launchctl print "gui/$UID/com.nexy.assistant"

# Удаление (при необходимости)
bash tools/packaging/uninstall_launch_agent.sh
```

### **📦 Проверка PKG:**
```bash
# Проверка подписи
pkgutil --check-signature dist/Nexy.pkg

# Проверка payload
pkgutil --expand dist/Nexy.pkg /tmp/nexy_pkg
grep -R "Users/.*/Applications" -n /tmp/nexy_pkg

# Проверка назначения
pkgutil --payload-files dist/Nexy.pkg | head
```

---

## 🎉 **DEFINITION OF DONE**

### **✅ ПРИЕМКА:**
- [ ] Второй запуск завершает процесс с кодом 1 и отдает сигнал/озвучку
- [ ] Перезагрузка системы приводит к запуску через LaunchAgent
- [ ] .app, .pkg, .dmg — нотарифицированы и **stapled**
- [ ] `pkgutil --expand` подтверждает путь в `~/Applications`
- [ ] Нет хард-путей к .app в коде/конфиге/plist
- [ ] Тест «Fast User Switching» пройден
- [ ] Все 17 интеграций работают корректно
- [ ] Архитектура соответствует принципам проекта

---

## 🛠️ **КОМАНДЫ ПРОВЕРКИ STAGING PIPELINE**

### **Быстрая проверка:**
```bash
# Полный пайплайн
make all

# Проверка подписи
codesign --verify --deep --strict --verbose=2 dist/Nexy.app

# Проверка Gatekeeper (после нотаризации)
spctl --assess --type execute --verbose dist/Nexy.app

# Проверка PKG/DMG (после нотаризации)
spctl -a -v Nexy.pkg
spctl -a -v Nexy.dmg
```

### **Переменные окружения:**
```bash
export DEVELOPER_ID_APP="Developer ID Application: Sergiy Zasorin (5NKLL2CLB9)"
export DEVELOPER_ID_INSTALLER="Developer ID Installer: Sergiy Zasorin (5NKLL2CLB9)"
export APPLE_NOTARY_PROFILE="NexyNotary"
```

### **Проверка нотаризации:**
```bash
# Нотарификация
xcrun notarytool submit dist/Nexy.app --keychain-profile "$APPLE_NOTARY_PROFILE" --wait
xcrun notarytool submit Nexy.pkg --keychain-profile "$APPLE_NOTARY_PROFILE" --wait
xcrun notarytool submit Nexy.dmg --keychain-profile "$APPLE_NOTARY_PROFILE" --wait

# Stapling
xcrun stapler staple dist/Nexy.app
xcrun stapler staple Nexy.pkg
xcrun stapler staple Nexy.dmg
```

### **📚 Документация по подписи:**
- **Быстрое руководство:** `Docs/CODESIGNING_QUICK_GUIDE.md`
- **Полное руководство:** `Docs/PACKAGING_PLAN.md` (раздел 2)
- **Troubleshooting:** `Docs/TROUBLESHOOTING_CODESIGNING.md`
- **Настройка окружения:** `packaging/setup_env.sh`

---

**🎯 СТАТУС:** ✅ **ГОТОВ К ПРОДАКШЕНУ**  
**📅 ДАТА ПРОВЕРКИ:** ___________  
**👤 ОТВЕТСТВЕННЫЙ:** ___________  
**✅ ПОДПИСЬ:** ___________

---

*Этот чек-лист является обязательным для прохождения перед любым релизом или мержем в main ветку.*