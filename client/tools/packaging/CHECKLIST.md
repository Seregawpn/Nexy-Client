# 📋 Чек-лист сборки PKG с нотарификацией

## ✅ Предпосылки (один раз на машину)

- [ ] Xcode + Command Line Tools установлен
- [ ] В связке ключей есть сертификаты:
  - [ ] **Developer ID Application: Sergiy Zasorin (5NKLL2CLB9)**
  - [ ] **Developer ID Installer: Sergiy Zasorin (5NKLL2CLB9)**
- [ ] Создан профиль для notarytool:
  ```bash
  xcrun notarytool store-credentials "nexy-notary" \
    --apple-id "sergiyzasorin@gmail.com" \
    --team-id "5NKLL2CLB9" \
    --password "qtiv-kabm-idno-qmbl"
  ```

## ✅ Sparkle (ключи и интеграция)

- [ ] Ed25519 ключи сгенерированы: `./generate_sparkle_keys.sh`
- [ ] Sparkle.framework находится в текущей директории
- [ ] В Nexy.spec есть:
  - [ ] `Tree(SPARKLE_FRAMEWORK, prefix='Frameworks')`
  - [ ] `SUFeedURL` и `SUPublicEDKey` в info_plist

## ✅ Entitlements (релизная версия)

- [ ] Удалены все `temporary-exception.*` ключи
- [ ] Удален `cs.debugger`
- [ ] Оставлены только необходимые разрешения

## ✅ Spec-файл (PyInstaller)

- [ ] `codesign_identity=CODESIGN_ID` в EXE()
- [ ] `entitlements_file=ENTITLEMENTS_FILE` в EXE()
- [ ] `Tree(..., prefix='Frameworks')` для Sparkle
- [ ] В info_plist есть:
  - [ ] `CFBundleIdentifier`
  - [ ] `SUFeedURL`
  - [ ] `SUPublicEDKey`
  - [ ] TCC-ключи (микрофон/камера)

## ✅ Сборка и тестирование

- [ ] Запущена сборка: `./build_pkg.sh`
- [ ] .app подписан корректно
- [ ] PKG подписан корректно
- [ ] PKG нотаризирован успешно
- [ ] Нотаризация скреплена
- [ ] PKG прошел финальную проверку

## ✅ Тестирование на чистой машине

- [ ] Удалены старые версии
- [ ] Скачан PKG с сервера
- [ ] Установка прошла без диалогов об «испорченном ПО»
- [ ] Приложение запускается
- [ ] Система запросила разрешения для микрофона/камеры

## ✅ Appcast для обновлений

- [ ] appcast.xml обновлен с новым PKG
- [ ] Добавлен `sparkle:installationType="package"`
- [ ] Подписана appcast.xml: `./sign_appcast.sh local_server/updates/appcast.xml`

## 🚨 Частые ошибки и быстрые фиксы

- **`resource fork / Finder info …` при codesign** → `xattr -rc` по всему дереву
- **Добавили файлы в .app после подписи** → подпись сломана; всё складываем до сборки
- **Sparkle не видит обновления** → проверь `SUFeedURL`/`SUPublicEDKey` в Info.plist
- **PKG не ставится из Sparkle** → добавь `sparkle:installationType="package"`
- **Нотарификация падает** → проверь entitlements и TCC-ключи

## 📞 Контакты для поддержки

- **Email:** sergiyzasorin@gmail.com
- **Team ID:** 5NKLL2CLB9
- **Bundle ID:** com.nexy.assistant
