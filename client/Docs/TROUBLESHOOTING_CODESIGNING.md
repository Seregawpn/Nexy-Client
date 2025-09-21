# 🔧 Troubleshooting Codesigning для Nexy

**Дата:** 20 сентября 2025  
**Статус:** ✅ Актуально

---

## 🚨 Критические ошибки

### 1. "resource fork, Finder information, or similar detritus not allowed"

**Причина:** Файлы содержат запрещенные xattrs (FinderInfo, ResourceFork)

**Решение:**
```bash
# Очистка всех xattrs
xattr -cr dist/Nexy.app

# Удаление конкретных проблемных атрибутов
xattr -dr com.apple.FinderInfo dist/Nexy.app
xattr -dr com.apple.ResourceFork dist/Nexy.app

# Переподпись
make sign-app
```

**Профилактика:** Используйте staging pipeline (`make all`)

---

### 2. "unsealed contents present in the bundle root"

**Причина:** В корне .app bundle есть лишние файлы

**Решение:**
```bash
# Проверка содержимого корня
ls -la dist/Nexy.app/

# Удаление лишних файлов
rm -rf dist/Nexy.app/Nexy.app  # вложенный .app
rm -rf dist/Nexy.app/*.txt     # текстовые файлы
rm -rf dist/Nexy.app/*.md      # markdown файлы

# Переподпись
make sign-app
```

**Профилактика:** Используйте staging pipeline

---

### 3. "a sealed resource is missing or invalid"

**Причина:** Файлы были изменены после подписи или повреждены

**Решение:**
```bash
# Полная пересборка
make clean
make sanitize-dist setup-staging app restage-app-root sign-nested sign-app stage-to-dist
```

---

### 4. "code signing failed with exit code 1"

**Причина:** Проблемы с сертификатом или правами доступа

**Решение:**
```bash
# Проверка сертификатов
security find-identity -v -p codesigning

# Проверка прав на файл
ls -la dist/Nexy.app/Contents/MacOS/Nexy

# Установка прав на выполнение
chmod +x dist/Nexy.app/Contents/MacOS/Nexy

# Проверка переменных окружения
echo $DEVELOPER_ID_APP
echo $DEVELOPER_ID_INSTALLER
```

---

## ⚠️ Предупреждения и ошибки

### 1. "replacing existing signature"

**Статус:** ✅ Нормально - это означает, что подпись обновляется

### 2. "unsealed contents present in the bundle root"

**Статус:** ❌ Ошибка - нужно удалить лишние файлы

### 3. "source=Unnotarized Developer ID"

**Статус:** ⚠️ Предупреждение - приложение не нотаризовано (нормально для разработки)

---

## 🔍 Диагностика проблем

### Проверка сертификатов:
```bash
# Список всех сертификатов
security find-identity -v -p codesigning

# Проверка конкретного сертификата
security find-certificate -c "Developer ID Application" -p | openssl x509 -text
```

### Проверка файлов:
```bash
# Тип файла
file dist/Nexy.app/Contents/MacOS/Nexy

# Права доступа
ls -la dist/Nexy.app/Contents/MacOS/Nexy

# xattrs
xattr -l dist/Nexy.app/Contents/MacOS/Nexy
```

### Проверка подписи:
```bash
# Детальная информация о подписи
codesign -dv --verbose=4 dist/Nexy.app

# Проверка entitlements
codesign -d --entitlements - dist/Nexy.app

# Проверка цепочки сертификатов
codesign -dv --verbose=4 dist/Nexy.app 2>&1 | grep -A 10 "Authority"
```

---

## 🛠️ Инструменты диагностики

### 1. Проверка готовности системы:
```bash
make doctor
```

### 2. Проверка staging pipeline:
```bash
make sanitize-dist setup-staging
ls -la /tmp/nexy-stage/
```

### 3. Проверка подписи поэтапно:
```bash
# Только вложения
make sign-nested

# Только основной .app
make sign-app

# Проверка каждого этапа
codesign --verify --deep --strict --verbose=2 /tmp/nexy-stage/Nexy.app
```

---

## 🔄 Восстановление после ошибок

### Полная пересборка:
```bash
# Очистка всего
make clean

# Полный пайплайн
make all
```

### Частичное восстановление:
```bash
# Только подпись
make sign-nested sign-app stage-to-dist

# Только нотаризация
make notarize-app notarize-pkg notarize-dmg staple-all
```

---

## 📋 Чек-лист диагностики

### Перед подписью:
- [ ] Переменные окружения установлены
- [ ] Сертификаты доступны в Keychain
- [ ] notarytool профиль настроен
- [ ] staging директория чистая

### После подписи:
- [ ] `codesign --verify --deep --strict` проходит
- [ ] `spctl --assess` проходит (после нотаризации)
- [ ] Приложение запускается
- [ ] Все артефакты подписаны

### При проблемах:
- [ ] Проверить логи ошибок
- [ ] Проверить права доступа
- [ ] Проверить xattrs
- [ ] Проверить сертификаты
- [ ] Пересобрать в staging

---

## 🆘 Экстренные решения

### Если ничего не помогает:
```bash
# Полная очистка и пересборка
make clean
rm -rf /tmp/nexy-stage
rm -rf dist/
make all
```

### Если проблемы с сертификатами:
```bash
# Переустановка сертификатов
# 1. Удалить из Keychain
# 2. Скачать заново из Apple Developer Portal
# 3. Установить в Keychain
# 4. Проверить: security find-identity -v -p codesigning
```

### Если проблемы с notarytool:
```bash
# Пересоздание профиля
xcrun notarytool store-credentials "NexyNotary" \
  --apple-id "your-apple-id@example.com" \
  --team-id "5NKLL2CLB9" \
  --password "your-app-specific-password"
```

---

## 📞 Получение помощи

1. **Проверьте логи:** Все команды выводят подробную информацию об ошибках
2. **Используйте verbose режим:** Добавляйте `--verbose=2` к командам codesign
3. **Проверьте документацию:** `Docs/PACKAGING_PLAN.md` (раздел 2)
4. **Используйте staging pipeline:** `make all` решает большинство проблем

---

**💡 Помните:** Staging pipeline (`make all`) решает 95% проблем с подписью автоматически!

