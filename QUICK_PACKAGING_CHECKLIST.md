# ⚡ БЫСТРЫЙ ЧЕКЛИСТ УПАКОВКИ NEXY

## 🚀 БЫСТРЫЙ СТАРТ

```bash
cd client/
chmod +x *.sh
./rebuild_and_notarize.sh
```

## ✅ ПРЕДВАРИТЕЛЬНЫЕ ПРОВЕРКИ

### 1. Сертификаты
```bash
# Проверка сертификатов
security find-identity -v -p codesigning | grep "Developer ID"
```

### 2. Зависимости
```bash
# Python модули
pip3 install -r requirements.txt

# Системные зависимости
brew install switchaudio-osx sparkle
```

### 3. Конфигурация
```bash
# Проверка готовности
./verify_packaging.sh
```

## 🔧 ОСНОВНЫЕ СКРИПТЫ

| Скрипт | Назначение |
|--------|------------|
| `./rebuild_and_notarize.sh` | Полная автоматизация |
| `./build_complete.sh` | Основная сборка |
| `./create_pkg.sh` | Создание PKG |
| `./notarize.sh` | Нотаризация |
| `./verify_packaging.sh` | Проверка готовности |

## 📦 РЕЗУЛЬТАТ

**Файл:** `Nexy_AI_Voice_Assistant_v1.71.0.pkg`
- ✅ Подписан Developer ID
- ✅ Нотаризован Apple
- ✅ Включает LaunchAgent
- ✅ Готов к распространению

## 🧪 ТЕСТИРОВАНИЕ

```bash
# Проверка подписи
pkgutil --check-signature Nexy_AI_Voice_Assistant_v1.71.0.pkg

# Проверка нотаризации
xcrun stapler validate Nexy_AI_Voice_Assistant_v1.71.0.pkg

# Тестовая установка
sudo installer -pkg Nexy_AI_Voice_Assistant_v1.71.0.pkg -target /
```

## ❗ ЧАСТЫЕ ПРОБЛЕМЫ

### Ошибка подписания
```bash
xattr -cr dist/Nexy.app
```

### Ошибка нотаризации
- Проверить Apple ID в `notarize_config.sh`
- Создать новый App-Specific Password

### PyInstaller не найден
```bash
python3 -m PyInstaller nexy.spec --clean --noconfirm
```

## 📋 ФАЙЛЫ КОНФИГУРАЦИИ

- `nexy.spec` - Конфигурация PyInstaller
- `entitlements.plist` - Разрешения для подписания
- `notarize_config.sh` - Настройки нотаризации
- `requirements.txt` - Python зависимости

## 🎯 ВРЕМЯ ВЫПОЛНЕНИЯ

- **Быстрая сборка:** 5-10 минут
- **С нотаризацией:** 15-20 минут
- **Полная проверка:** 25-30 минут

---

**📖 Полная документация:** `COMPLETE_PACKAGING_GUIDE.md`

