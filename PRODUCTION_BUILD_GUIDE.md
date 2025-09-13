# 🏗️ Руководство по производственной сборке Nexy

## 📋 Обзор

Это руководство описывает правильный процесс сборки, подписания и нотаризации приложения Nexy AI Voice Assistant для macOS.

## 🔧 Предварительные требования

### 1. Сертификаты Apple Developer
- ✅ **Developer ID Application** - для подписания .app bundle
- ✅ **Developer ID Installer** - для подписания PKG
- ✅ **Apple ID** с app-specific password для нотаризации

### 2. Зависимости
```bash
# PyInstaller
pip install pyinstaller

# macOS инструменты (уже установлены)
codesign, productsign, xcrun
```

### 3. Конфигурация
- ✅ `nexy.spec` - настроен с правильными параметрами подписания
- ✅ `entitlements_app.plist` - содержит все необходимые разрешения
- ✅ `entitlements_pkg.plist` - минимальные разрешения для PKG

## 🚀 Процесс сборки

### 1. Проверка готовности
```bash
./check_ready.sh
```

### 2. Производственная сборка
```bash
./build_production.sh
```

### 3. Быстрая сборка (для разработки)
```bash
./build_quick.sh
```

## 📁 Структура файлов

```
Nexy/
├── build_production.sh          # Главный скрипт сборки
├── build_quick.sh               # Быстрая сборка
├── check_ready.sh               # Проверка готовности
├── nexy.spec                    # PyInstaller конфигурация
├── entitlements_app.plist       # Разрешения для .app
├── entitlements_pkg.plist       # Разрешения для PKG
├── build/scripts/
│   ├── sign_app_production.sh   # Подписание .app
│   ├── sign_pkg_production.sh   # Подписание PKG
│   └── notarize_production.sh   # Нотаризация
└── dist/
    └── Nexy.app                 # Собранное приложение
```

## ⚙️ Ключевые настройки

### nexy.spec
```python
# EXE секция
codesign_identity="Developer ID Application: Sergiy Zasorin (5NKLL2CLB9)",
entitlements_file='entitlements_app.plist',
codesign_options=['runtime', 'timestamp'],

# BUNDLE секция
codesign_identity="Developer ID Application: Sergiy Zasorin (5NKLL2CLB9)",
entitlements_file='entitlements_app.plist',
codesign_options=['runtime', 'timestamp'],
```

### entitlements_app.plist
- ✅ Hardened Runtime разрешения
- ✅ Аудио устройства
- ✅ Сетевые соединения
- ✅ Файловая система
- ✅ Автоматизация Apple Events

## 🔐 Процесс подписания

### 1. Автоматическое подписание (PyInstaller)
- Все исполняемые файлы подписываются автоматически
- Hardened Runtime включается автоматически
- Entitlements применяются автоматически
- Timestamp добавляется автоматически

### 2. Проверка подписи
```bash
# Проверка .app bundle
codesign -dv dist/Nexy.app/Contents/MacOS/Nexy
codesign -d --entitlements - dist/Nexy.app/Contents/MacOS/Nexy

# Проверка PKG
pkgutil --check-signature Nexy_1.71.0_signed.pkg
```

## 📤 Процесс нотаризации

### 1. Отправка на нотаризацию
```bash
xcrun notarytool submit Nexy_1.71.0_signed.pkg \
    --apple-id seregawpn@gmail.com \
    --password qtiv-kabm-idno-qmbl \
    --team-id 5NKLL2CLB9 \
    --wait
```

### 2. Склеивание тикета
```bash
xcrun stapler staple Nexy_1.71.0_signed.pkg
```

### 3. Проверка статуса
```bash
xcrun stapler validate Nexy_1.71.0_signed.pkg
```

## ✅ Критерии успеха

### .app bundle
- ✅ Hardened Runtime включен (`flags=0x10000(runtime)`)
- ✅ Entitlements применены
- ✅ Timestamp добавлен
- ✅ Подпись валидна

### PKG
- ✅ Подписан Developer ID Installer
- ✅ Timestamp добавлен
- ✅ Нотаризация прошла (Accepted)
- ✅ Тикет склеен

## 🐛 Решение проблем

### Hardened Runtime не включен
- Проверить `codesign_options=['runtime', 'timestamp']` в nexy.spec
- Проверить `entitlements_file` в nexy.spec

### xattr ошибки
- Очистить xattr атрибуты: `find . -name "*.py" -exec xattr -c {} \;`

### Нотаризация не проходит
- Проверить подпись всех исполняемых файлов
- Проверить Hardened Runtime
- Проверить entitlements

## 📦 Результат

После успешной сборки получаем:
- **Nexy_1.71.0_signed.pkg** - готовый к распространению PKG
- **dist/Nexy.app** - подписанный .app bundle
- **Все проверки пройдены** - готов к установке на macOS

## 🚀 Распространение

PKG можно распространять через:
- Веб-сайт
- Email
- USB-накопители
- Любые другие способы

macOS автоматически проверит подпись и нотаризацию при установке.

