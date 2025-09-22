# 📦 PACKAGING - Упаковка Nexy AI Assistant

> **Обновлено:** 22.09.2025 | **Статус:** Готово к продакшену

---

## 📁 СТРУКТУРА ПАПКИ

```
packaging/
├── Nexy.spec              # PyInstaller конфигурация (с PIL исправлениями)
├── entitlements.plist     # macOS разрешения (минимальные)
├── distribution.xml       # PKG конфигурация
├── LaunchAgent/           # Автозапуск
│   └── com.nexy.assistant.plist
├── build_all.sh          # 🚀 ГЛАВНЫЙ СКРИПТ СБОРКИ
├── verify_all.sh         # 🔍 ПРОВЕРКА АРТЕФАКТОВ
├── generate_manifest.py  # 📋 ГЕНЕРАТОР МАНИФЕСТА
└── README.md             # Эта документация
```

---

## 🚀 БЫСТРЫЙ СТАРТ

### **Полная сборка (одна команда)**
```bash
cd /Users/sergiyzasorin/Desktop/Development/Nexy/client
chmod +x packaging/*.sh
./packaging/build_all.sh
```

### **Проверка результата**
```bash
./packaging/verify_all.sh
```

### **Тестовая установка**
```bash
sudo installer -pkg dist/Nexy-signed.pkg -target /
```

---

## 🔧 КЛЮЧЕВЫЕ ИСПРАВЛЕНИЯ

### **1. PIL для иконок (КРИТИЧНО)**
**Проблема:** Иконки не отображались в меню-баре  
**Решение:** Добавлены в `Nexy.spec`:
```python
hiddenimports=[
    'PIL', 'PIL.Image', 'PIL.ImageDraw', 'Pillow',
    # ...
]
```

### **2. Hardened Runtime (ОТКЛЮЧЕН)**
**Проблема:** `Library Validation failed: Team ID conflict`  
**Решение:** Подпись БЕЗ `--options runtime`:
```bash
codesign --force --timestamp \
  --entitlements entitlements.plist \
  --sign "Developer ID Application: ..." \
  app.app
```

### **3. Сборка в /tmp**
**Проблема:** macOS атрибуты ломают подпись  
**Решение:** Сборка в временной папке `/tmp/nexy_*`

### **4. Импорты интеграций**
**Проблема:** `No module named 'integrations'`  
**Решение:** Добавлен путь в `Nexy.spec`:
```python
pathex=[str(client_dir), str(client_dir / 'integration')],
```

---

## 📦 АРТЕФАКТЫ

### **После успешной сборки:**

| Файл | Размер | Назначение | Статус |
|------|--------|------------|--------|
| `dist/Nexy-signed.pkg` | ~13KB | Первичная установка | ✅ Подписан |
| `dist/Nexy.dmg` | ~58MB | Автообновления | ✅ Нотаризован |
| `dist/manifest.json` | ~1KB | Манифест обновлений | ✅ С подписями |
| `dist/Nexy-final.app` | ~65MB | Готовое приложение | ✅ С иконками |

---

## 🧪 ТЕСТИРОВАНИЕ

### **Проверка иконок**
```bash
# Запуск на 30 секунд
dist/Nexy-final.app/Contents/MacOS/Nexy &
APP_PID=$!
sleep 30
kill $APP_PID

# Должна появиться цветная круглая иконка в меню-баре (Pillow)!
```

### **Проверка установки PKG**
```bash
# Установка
sudo installer -pkg dist/Nexy-signed.pkg -target /

# Проверка результата
ls -la ~/Applications/Nexy.app
ls -la ~/Library/LaunchAgents/com.nexy.assistant.plist

# Автозапуск
launchctl list | grep com.nexy.assistant
```

### **Проверка DMG**
```bash
# Монтирование
open dist/Nexy.dmg

# Нотаризация
xcrun stapler validate dist/Nexy.dmg
```

---

## ⚠️ УСТРАНЕНИЕ ПРОБЛЕМ

### **Иконки не появляются**
1. Проверить PIL в spec: `grep "PIL.Image" packaging/Nexy.spec`
2. Пересобрать: `./packaging/build_all.sh`
3. Переустановить PKG
4. Иконка рисуется программно (PIL) — убедитесь, что hiddenimports для `PIL`, `PIL.Image`, `PIL.ImageDraw` присутствуют в `Nexy.spec`

### **Скриншоты и формат**
1. Захват экрана выполняется через CoreGraphics (PyObjC) → JPEG кодирование (AppKit)
2. Формат фиксирован: JPEG (перекодировок в WEBP/PNG нет)
3. Для Screen Recording требуется разрешение в «Конфиденциальность и безопасность»

### **Зависимости PyObjC**
1. Убедитесь, что установлены: `pyobjc-core`, `pyobjc-framework-Quartz`, `pyobjc-framework-Cocoa`
2. В `Nexy.spec` добавлены hiddenimports: `Quartz`, `AppKit`, `Cocoa`, `Foundation`

### **Updater в dev-среде**
1. Манифест по умолчанию: `http://localhost:8080/manifest.json`
2. Если локальный сервер не запущен — временно отключите проверку на старте:
   - В `config/unified_config.yaml`: `integrations.updater.check_on_startup: false`

### **Приложение не запускается**
1. Проверить подпись: `codesign --verify --strict --deep dist/Nexy-final.app`
2. Проверить логи: `log show --predicate 'process == "Nexy"' --last 1m`
3. Проверить разрешения в Системных настройках

### **PKG не устанавливается**
1. Проверить подпись: `pkgutil --check-signature dist/Nexy-signed.pkg`
2. Установка с отладкой: `sudo installer -pkg dist/Nexy-signed.pkg -target / -verbose`

### **DMG не нотаризуется**
1. Проверить профиль: `xcrun notarytool history --keychain-profile nexy-notary`
2. Проверить размер DMG (не более 2GB)
3. Повторить нотаризацию

---

## 📞 КОНТАКТЫ И НАСТРОЙКИ

- **Team ID:** 5NKLL2CLB9
- **Bundle ID:** com.nexy.assistant
- **Apple ID:** seregawpn@gmail.com
- **Notarytool профиль:** nexy-notary
- **Версия:** 1.71.0

---

## 🎯 КРИТЕРИИ УСПЕХА

**✅ Готовность к релизу:**
- [ ] Все скрипты выполняются без ошибок
- [ ] `verify_all.sh` проходит все проверки
- [ ] Приложение запускается и показывает цветные иконки
- [ ] PKG устанавливается без пароля в ~/Applications
- [ ] DMG нотаризован и проходит проверку
- [ ] Манифест содержит корректные подписи

**🎯 После установки PKG:**
- [ ] Приложение автоматически запускается
- [ ] В меню-баре появляется цветная иконка
- [ ] Меню работает при клике на иконку
- [ ] LaunchAgent настроен корректно

---

**📋 Полная документация:** `Docs/PACKAGING_MASTER_GUIDE.md`