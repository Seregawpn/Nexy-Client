# 📦 Nexy Packaging Directory

## 🎯 Структура файлов

```
packaging/
├── Nexy.spec                    # PyInstaller конфигурация с исправленной интеграцией Sparkle
├── entitlements.plist           # macOS разрешения (без debugger, релизная версия)
├── build_pkg.sh                 # Главный скрипт сборки PKG (исправленная версия)
├── generate_sparkle_keys.sh     # Генерация Ed25519 ключей
├── sign_appcast.sh              # Подпись appcast.xml
├── Makefile                     # Альтернативный способ сборки
├── README.md                    # Эта документация
├── Sparkle.framework/           # Sparkle Framework для автообновлений
├── sparkle_keys/                # Ed25519 ключи
│   ├── ed25519_private_key.pem  # Приватный ключ (хранить в безопасности!)
│   └── ed25519_public_key.pem   # Публичный ключ (встроен в приложение)
└── local_server/                # Локальный сервер для тестирования
    ├── start_server.py          # HTTP сервер
    ├── README.md                # Инструкции по серверу
    └── updates/                 # Файлы обновлений
        ├── appcast.xml          # XML с информацией об обновлениях
        └── Nexy-with-Sparkle-2.5.0-signed.pkg  # Тестовый PKG
```

## ✅ Исправления (v2.0)

### Что исправлено:
- **✅ Sparkle Framework:** Используется `Tree()` для правильной интеграции в `Contents/Frameworks`
- **✅ Info.plist:** Добавлены `SUPublicEDKey` и `SUFeedURL` для работы Sparkle
- **✅ Entitlements:** Удален `com.apple.security.cs.debugger` для релизной версии
- **✅ Скрипт сборки:** Исправлен с правильными командами PyInstaller и codesign

### Ключевые изменения в Nexy.spec:
```python
# Правильная интеграция Sparkle
Tree(SPARKLE_FRAMEWORK, prefix='Frameworks/Sparkle.framework'),

# В Info.plist
'SUPublicEDKey': SU_PUBLIC_ED_KEY,
'SUFeedURL': FEED_URL,
```

## 🚀 Быстрый старт

```bash
# 1. Сборка PKG (исправленная версия)
./build_pkg.sh

# 2. Запуск локального сервера для тестирования
python3 local_server/start_server.py
```

## 🔑 Безопасность

- **Приватный ключ** (`sparkle_keys/ed25519_private_key.pem`) - храните в безопасности!
- **Публичный ключ** уже встроен в приложение
- **Не коммитьте приватные ключи** в git!

## 📋 Что делает build_pkg.sh

1. ✅ Собирает .app с встроенной подписью PyInstaller
2. ✅ Интегрирует Sparkle Framework через Tree()
3. ✅ Очищает extended attributes
4. ✅ Проверяет подпись .app
5. ✅ Создает PKG installer
6. ✅ Подписывает PKG
7. ✅ Проверяет подпись PKG

## 🌐 Тестирование обновлений

```bash
# Запуск локального сервера
python3 local_server/start_server.py

# Приложение будет проверять: http://localhost:8080/updates/appcast.xml
```

## ⚠️ Важные замечания

- **Не редактируйте .app после сборки** - это сломает подпись
- **Все изменения только в .spec файле**
- **Приватный ключ только для подписи appcast**
- **PKG файлы можно тестировать через локальный сервер**

## 🔧 Альтернативная сборка

Если нужно собрать только .app без PKG:

```bash
cd /Users/sergiyzasorin/Desktop/Development/Nexy/client
python3 -m PyInstaller --clean -y tools/packaging/Nexy.spec

# Очистка extended attributes
xattr -rc dist/Nexy.app

# Проверка подписи
codesign --verify --deep --strict --verbose=2 dist/Nexy.app
```


