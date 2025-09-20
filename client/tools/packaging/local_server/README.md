# 🚀 Локальный сервер для Sparkle AppCast

Этот каталог содержит локальный HTTP сервер для тестирования системы автообновлений Sparkle.

## 📁 Структура

```
local_server/
├── start_server.py          # HTTP сервер для AppCast
├── updates/
│   └── appcast.xml         # XML файл с информацией об обновлениях
└── README.md               # Эта документация
```

## 🚀 Быстрый старт

### 1. Запуск сервера

```bash
# Из директории packaging
./start_local_server.sh

# Или напрямую
cd local_server
python3 start_server.py
```

### 2. Проверка работы

```bash
# Проверка AppCast
curl http://localhost:8080/updates/appcast.xml

# Проверка доступности сервера
curl http://localhost:8080/
```

## 📋 Настройка

### AppCast XML

Файл `updates/appcast.xml` содержит информацию об обновлениях:

- **URL обновления**: `http://localhost:8080/updates/Nexy-2.5.0.pkg`
- **Версия**: `2.5.0` (build `20500`)
- **Описание**: HTML описание изменений

### PKG файлы

Сервер автоматически ищет PKG файлы в родительской директории:
- `Nexy-2.5.0.pkg`
- `Nexy-2.5.0-signed.pkg`

## 🔧 Интеграция с приложением

### В Nexy.spec

```python
'SUFeedURL': 'http://localhost:8080/updates/appcast.xml'
```

### В Makefile

```makefile
# Для разработки используйте локальный сервер
# Для продакшена замените на реальный URL
```

## 📝 Обновление AppCast

При создании нового PKG файла:

1. Обновите `appcast.xml`:
   - Измените версию
   - Обновите описание
   - Укажите правильное имя файла

2. Перезапустите сервер

3. Протестируйте обновление в приложении

## 🔄 Переключение на продакшен

Когда готовы к продакшену:

1. Замените URL в `Nexy.spec`:
   ```python
   'SUFeedURL': 'https://api.yourdomain.com/updates/appcast.xml'
   ```

2. Загрузите PKG и appcast.xml на ваш сервер

3. Убедитесь, что HTTPS работает корректно

## 🐛 Отладка

### Проверка логов сервера

Сервер выводит все запросы в консоль:
```
📥 GET запрос: /updates/appcast.xml
✅ Отправлен appcast.xml
```

### Проверка AppCast

```bash
# Проверка XML
curl -s http://localhost:8080/updates/appcast.xml | xmllint --format -

# Проверка доступности PKG
curl -I http://localhost:8080/updates/Nexy-2.5.0.pkg
```

### Проблемы

- **Порт занят**: Измените PORT в `start_server.py`
- **PKG не найден**: Убедитесь, что файл находится в правильной директории
- **XML ошибки**: Проверьте синтаксис в `appcast.xml`

## 🔗 Полезные ссылки

- [Sparkle Documentation](https://sparkle-project.org/documentation/)
- [AppCast XML Format](https://sparkle-project.org/documentation/publishing/#appcast)
- [macOS Code Signing](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
