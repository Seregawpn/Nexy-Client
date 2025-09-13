# 🚀 Sparkle Framework - Пошаговое руководство по реализации

## 📋 Обзор

Это руководство описывает полную интеграцию Sparkle Framework в проект Nexy для автоматических обновлений macOS приложения, специально адаптированных для слепых пользователей.

## 🎯 Цели реализации

- ✅ **Полная автоматизация** - никакого вмешательства пользователя
- ✅ **Accessibility** - полная поддержка VoiceOver
- ✅ **Безопасность** - проверка подписей Apple
- ✅ **Интеграция** - работает с существующей системой сборки
- ✅ **Надежность** - стандарт для macOS приложений

## 📅 План реализации (2-3 недели)

### **Неделя 1: Подготовка и интеграция**

#### **День 1-2: Настройка окружения**

1. **Установка Sparkle Framework**
   ```bash
   cd client/
   chmod +x build/pyinstaller/setup_sparkle.sh
   ./build/pyinstaller/setup_sparkle.sh
   ```

2. **Проверка установки**
   ```bash
   ls -la build/pyinstaller/Sparkle.framework/
   ls -la build/pyinstaller/keys/
   ```

#### **День 3-4: Интеграция в код**

1. **Интеграция в систему сборки**
   ```bash
   chmod +x build/pyinstaller/integrate_sparkle.sh
   ./build/pyinstaller/integrate_sparkle.sh
   ```

2. **Добавление модуля обновлений в main.py**
   ```python
   # В client/main.py добавить:
   from update_manager import SparkleUpdateManager
   
   # В StateManager.__init__():
   self.update_manager = SparkleUpdateManager(self.config)
   
   # В main():
   if state_manager.update_manager.sparkle_path:
       await state_manager.start_update_checker()
   ```

3. **Обновление конфигурации**
   ```yaml
   # В client/config/app_config.yaml добавить:
   sparkle:
     enabled: true
     appcast_url: "https://your-server.com/appcast.xml"
     auto_install: true
     check_interval: 3600
   ```

#### **День 5: Тестирование интеграции**

1. **Сборка с Sparkle**
   ```bash
   ./build/pyinstaller/production_build.sh
   ```

2. **Тестирование интеграции**
   ```bash
   ./build/pyinstaller/test_sparkle_integration.sh
   ```

### **Неделя 2: Серверная часть**

#### **День 1-2: Настройка сервера**

1. **Настройка серверной части**
   ```bash
   cd server/
   chmod +x setup_update_server.sh
   ./setup_update_server.sh
   ```

2. **Обновление main.py сервера**
   ```python
   # Добавить в server/main.py:
   from update_service import setup_update_routes
   setup_update_routes(app)
   ```

#### **День 3-4: Настройка хостинга**

1. **Настройка домена и SSL**
2. **Загрузка DMG файлов**
3. **Обновление AppCast с правильными URL**

#### **День 5: Тестирование сервера**

1. **Тестирование endpoints**
   ```bash
   curl https://your-server.com/appcast.xml
   curl https://your-server.com/api/update/check?current=1.70.0
   ```

### **Неделя 3: Тестирование и отладка**

#### **День 1-3: Локальное тестирование**

1. **Тестирование на локальной машине**
2. **Проверка accessibility функций**
3. **Отладка проблем**

#### **День 4-5: Продакшн тестирование**

1. **Тестирование с реальными пользователями**
2. **Мониторинг логов**
3. **Финальная отладка**

## 🔧 Детальные инструкции

### **Шаг 1: Установка Sparkle Framework**

```bash
# Переходим в директорию клиента
cd client/

# Запускаем скрипт установки
chmod +x build/pyinstaller/setup_sparkle.sh
./build/pyinstaller/setup_sparkle.sh
```

**Что происходит:**
- Скачивается Sparkle Framework v2.5.0
- Генерируются ED25519 ключи для подписи
- Создается шаблон AppCast файла
- Создается скрипт для подписи обновлений

### **Шаг 2: Интеграция в код**

```bash
# Интегрируем Sparkle в систему сборки
chmod +x build/pyinstaller/integrate_sparkle.sh
./build/pyinstaller/integrate_sparkle.sh
```

**Что происходит:**
- Sparkle Framework добавляется в app.spec
- Настройки Sparkle добавляются в Info.plist
- Конфигурация обновляется
- Создается тестовый скрипт

### **Шаг 3: Модификация main.py**

Добавить в `client/main.py`:

```python
# Импорт модуля обновлений
from update_manager import SparkleUpdateManager

class StateManager:
    def __init__(self):
        # ... существующий код ...
        
        # Инициализация Sparkle Update Manager
        self.update_manager = SparkleUpdateManager(self.config)
        self.update_task = None
    
    async def start_update_checker(self):
        """Запуск проверки обновлений в фоне"""
        if self.update_task is None:
            self.update_task = asyncio.create_task(
                self.update_manager.start_update_checker()
            )
            logger.info("🔄 Sparkle Update Checker запущен")

# В функции main() добавить:
async def main():
    # ... существующий код ...
    
    # Запуск системы обновлений
    if state_manager.update_manager.sparkle_path:
        await state_manager.start_update_checker()
        logger.info("✅ Система автообновлений активирована")
    else:
        logger.warning("⚠️ Sparkle Framework не найден, автообновления отключены")
```

### **Шаг 4: Настройка сервера**

```bash
# Переходим в директорию сервера
cd server/

# Настраиваем сервер обновлений
chmod +x setup_update_server.sh
./setup_update_server.sh
```

**Что происходит:**
- Создается AppCast XML файл
- Создается Update Service для API
- Обновляется main.py сервера
- Создается скрипт для загрузки обновлений

### **Шаг 5: Сборка и тестирование**

```bash
# Собираем приложение с Sparkle
cd client/
./build/pyinstaller/production_build.sh

# Тестируем интеграцию
./build/pyinstaller/test_sparkle_integration.sh
```

## 🔐 Безопасность

### **Подписи обновлений**

1. **ED25519 ключи** - для подписи обновлений
2. **Apple Developer ID** - для подписи DMG файлов
3. **Проверка целостности** - автоматическая проверка подписей

### **Процесс подписи**

```bash
# Подписание DMG файла
./build/pyinstaller/sign_update.sh path/to/file.dmg

# Получение подписи для AppCast
openssl dgst -sha256 -sign keys/ed25519_private.pem file.dmg | base64
```

## 📱 Accessibility для слепых пользователей

### **Автоматические функции**

- ✅ **Автоматическая проверка** - каждые 60 минут
- ✅ **Автоматическое скачивание** - в фоне
- ✅ **Автоматическая установка** - без подтверждения
- ✅ **Озвучивание процесса** - через VoiceOver
- ✅ **Автоматический перезапуск** - после установки

### **Голосовые уведомления**

```python
# Озвучивание доступности обновления
announcement = f"Доступно обновление {title}. Начинаю установку."
subprocess.Popen(['say', announcement])
```

## 🧪 Тестирование

### **Локальное тестирование**

1. **Проверка интеграции**
   ```bash
   ./build/pyinstaller/test_sparkle_integration.sh
   ```

2. **Проверка AppCast**
   ```bash
   curl http://localhost:50051/appcast.xml
   ```

3. **Проверка API**
   ```bash
   curl "http://localhost:50051/api/update/check?current=1.70.0"
   ```

### **Продакшн тестирование**

1. **Загрузка обновления**
   ```bash
   ./server/upload_update.sh 1.71.0 /path/to/Nexy_1.71.0.dmg
   ```

2. **Проверка на клиенте**
   - Запуск приложения
   - Ожидание проверки обновлений
   - Проверка автоматической установки

## 📊 Мониторинг

### **Логи клиента**

```bash
# Просмотр логов обновлений
tail -f ~/Library/Logs/Nexy/app.log | grep -i sparkle
```

### **Логи сервера**

```bash
# Просмотр логов сервера
tail -f server.log | grep -i update
```

## 🚨 Устранение неполадок

### **Частые проблемы**

1. **Sparkle Framework не найден**
   ```bash
   # Проверяем установку
   ls -la build/pyinstaller/Sparkle.framework/
   ```

2. **Ошибки подписи**
   ```bash
   # Проверяем ключи
   ls -la build/pyinstaller/keys/
   ```

3. **Ошибки AppCast**
   ```bash
   # Проверяем XML
   curl https://your-server.com/appcast.xml
   ```

### **Отладка**

```python
# Включение debug логов
logging.getLogger('update_manager').setLevel(logging.DEBUG)
```

## 📈 Метрики успеха

### **Технические метрики**

- ✅ Sparkle Framework интегрирован
- ✅ AppCast работает корректно
- ✅ Подписи проверяются
- ✅ Обновления устанавливаются автоматически

### **Пользовательские метрики**

- ✅ Слепые пользователи получают обновления без вмешательства
- ✅ Процесс обновления озвучивается
- ✅ Нет прерывания работы приложения
- ✅ Быстрая установка обновлений

## 🎯 Следующие шаги

После завершения реализации:

1. **Мониторинг** - отслеживание успешности обновлений
2. **Оптимизация** - улучшение скорости и надежности
3. **Расширение** - добавление дополнительных функций
4. **Документация** - создание руководств для пользователей

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи приложения
2. Убедитесь в корректности конфигурации
3. Проверьте доступность сервера обновлений
4. Обратитесь к документации Sparkle Framework

---

**Статус:** ✅ Готово к реализации  
**Время:** 2-3 недели  
**Сложность:** Средняя  
**Приоритет:** Высокий

