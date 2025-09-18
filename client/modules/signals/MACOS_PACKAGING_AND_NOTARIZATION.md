# 📦 macOS: Упаковка, Подпись и Нотаризация (Signals Module)

Этот документ описывает, что нужно учесть при упаковке, подписи, сертификации и нотарификации приложения macOS при наличии модуля `signals`.

Ключевая мысль: текущая реализация модуля `signals` не добавляет новых прав (entitlements), новых нативных библиотек или приватных API. Она безопасна для PKG‑упаковки, подписи (Developer ID) и нотарификации без дополнительных изменений.

---

## 🔎 Что делает модуль Signals
- Короткие подсказки (audio/visual cues) в ключевые моменты.
- Аудио‑сигналы генерируются в чистом Python как PCM (s16le mono, 48 kHz) и передаются в существующий аудио‑плеер (CoreAudio) через адаптер.
- Визуальные сигналы (опционально) реализуются через тонкий адаптер к трею.

Следствие: нет новых потоков CoreAudio, нет новых фреймворков, нет зависимостей на PyObjC/AVFoundation (в первой версии).

---

## ✅ Entitlements и разрешения (TCC)
- Новых entitlements не требуется.
- Используются уже имеющиеся разрешения приложения:
  - Microphone: для VoiceRecognition (не меняется)
  - Screen Recording: для захвата скриншота (не меняется)
  - Accessibility: для CGEventTap (клавиатура; не меняется)
- Signals не инициирует новые запросы TCC и не требует дополнительных ключей в `entitlements.plist`.

Если когда‑нибудь будет добавлен NSSound/AVFoundation (через PyObjC):
- Потребуется аудит зависимостей и возможные корректировки подписи/пакета. Сейчас это не используется.

---

## 📦 Зависимости
- По умолчанию — чистый Python. Дополнительные библиотеки не обязательны.
- `numpy` может использоваться как ускоритель генерации тона (опционально). Для поставки это не критично: колесо универсально для arm64; код подписывается в составе .app.
- Не добавляются .dylib/.framework — значит, process код‑подписи и нотарификации остаются неизменными.

---

## 🧾 Подпись и нотарификация (шпаргалка)
Ниже — краткая последовательность. Подробнее см. общие руководства в корне репозитория.

1) Сборка .app
- Соберите приложение (например, py2app/pyinstaller, согласно вашему пайплайну);
- Убедитесь, что `entitlements.plist` содержит только нужные права (mic/screen/accessibility, если они уже используются проектом).

2) Подпись .app (Developer ID Application)
```
codesign \
  --deep --force --options runtime \
  --entitlements entitlements.plist \
  -s "Developer ID Application: <Your Name> (<TEAM_ID>)" \
  "/path/to/Nexy.app"

codesign --verify --deep --strict "/path/to/Nexy.app"
spctl --assess --type execute "/path/to/Nexy.app"
```

3) Подпись и сборка PKG
```
productbuild \
  --component "/path/to/Nexy.app" "/Applications" \
  "/path/to/Nexy.pkg"

productsign \
  --sign "Developer ID Installer: <Your Name> (<TEAM_ID>)" \
  "/path/to/Nexy.pkg" "/path/to/Nexy-signed.pkg"
```

4) Нотарификация PKG (notarytool)
```
# Рекомендуется один раз сохранить учётку в Keychain:
# xcrun notarytool store-credentials nexy-notary \
#   --apple-id <APPLE_ID_EMAIL> --team-id <TEAM_ID> --keychain-profile nexy-notary

xcrun notarytool submit "/path/to/Nexy-signed.pkg" \
  --keychain-profile nexy-notary --wait

xcrun stapler staple "/path/to/Nexy-signed.pkg"
```

5) Проверки
```
spctl --assess --type install "/path/to/Nexy-signed.pkg"
```

---

## 🛡️ Hardened Runtime
- Включён флаг `--options runtime` при `codesign`.
- Signals не требует исключений для загрузки кода/плагинов/JIT — дополнительные флаги не нужны.

---

## 🧪 Что проверить локально
- Приложение устанавливается из PKG без предупреждений Gatekeeper.
- При первом запуске появляются только ожидаемые запросы TCC (микрофон/скрин) — ровно как до добавления Signals.
- Аудио‑сигналы проигрываются на текущем устройстве вывода (тот же путь, что и основной плеер).
- Никаких дополнительных диалогов разрешений для Signals нет.

---

## ❗ Частые вопросы
- Нужна ли PyObjC/AVFoundation для сигналов? — Нет, в текущей версии. Если добавить, потребуется пересмотреть подпись/зависимости.
- Нужно ли что‑то менять в entitlements из‑за Signals? — Нет.
- Влияет ли Signals на нотарификацию? — Нет, дополнительных шагов не требуется.

---

## ✅ Чек‑лист соответствия (для ревью)
- [ ] В модуле нет приватных API/нативных либ (только Python)
- [ ] Генерация тона — PCM s16le/48kHz; без новых аудиодрайверов
- [ ] Воспроизведение — через существующий аудиоплеер (один девайс)
- [ ] Нет новых entitlements, Hardened Runtime без исключений
- [ ] Подпись .app (Developer ID Application) и .pkg (Developer ID Installer) выполнены
- [ ] Нотарификация PKG успешна, stapler проставлен

---

## 🔗 Ссылки на общие гайды
- PACKAGING_README.md (в корне)
- PRODUCTION_BUILD_GUIDE.md (в корне)
- client/Docs/GLOBAL_DELIVERY_PLAN.md (этапы поставки, Azure/AppCast)
