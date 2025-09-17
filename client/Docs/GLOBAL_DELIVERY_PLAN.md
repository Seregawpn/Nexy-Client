# 🚀 GLOBAL DELIVERY PLAN — Nexy AI Assistant (macOS)

## 🎯 Цель
Единый план движения и реализации концепта с тремя режимами (SLEEPING / LISTENING / PROCESSING), упаковкой в подписанный и нотарифицированный PKG, автообновлениями (Sparkle) и переносом серверной части на Azure (без Docker/CI).

- Архитектурные принципы: EventBus, тонкие интеграции (без дублирования логики модулей), координатор лишь координирует.
- Режимы: только 3 (S/L/P). Воспроизведение — подэтап внутри PROCESSING.
- Дистрибуция: финальный артефакт — подписанный/нотарифицированный PKG + `appcast.xml` на Azure.

---

## 🧭 Обзор этапов
1) Этап 1 — Клиент: интеграции и UX (S/L/P)
2) Этап 2 — Поставка: PKG + подпись/нотаризация + Sparkle
3) Этап 3 — Сервер: Azure (без Docker/CI) + хостинг AppCast/PKG

Каждый этап разбит на мини‑циклы с целью, действиями и тест‑гейтом (критерием готовности).

---

## 1) Клиент: интеграции и UX (S/L/P)
**Цель**: стабильный UX и полный пользовательский цикл S→L→P→S.

- 1.1 Tray стабилизация
  - Действия: подписка на `app.mode_changed` и `voice.mic_opened/closed`; индикация S/L/P; текст статуса; позже — `network.status_changed`.
  - Тест‑гейт: смена режима мгновенно меняет статус в трее.

- 1.2 Permissions стабилизация
  - Действия: проверка на старте; публикация `permission.*`; инструкции/открытие настроек при отказе.
  - Тест‑гейт: без разрешений — видны инструкции; с разрешениями — событие `permission.all_granted`.

- 1.3 InputProcessing стабилизация
  - Действия: `long_press`→LISTENING; `release`→PROCESSING; `short_press`/ошибка→SLEEPING; дебаунс/анти‑дребезг.
  - Тест‑гейт: надёжные переходы без гонок.

- 1.4 Update Manager (тихий режим)
  - Действия: фоновая проверка; без UI‑диалогов; лог статуса.
  - Тест‑гейт: при запуске фиксируется проверка; без всплывающих окон.

- 1.5 NetworkManagerIntegration
  - Действия: минимальный `NetworkManager` (TCP/53), интеграция, снапшот на `app.startup`; tray tooltip сети.
  - Тест‑гейт: off/on сети → события `network.status_changed`, tray отражает.

- 1.6 AudioDeviceIntegration
  - Действия: выбор/мониторинг устройств (без открытия записи). Физический захват микрофона выполняет VoiceRecognitionIntegration.
  - Тест‑гейт: корректный снапшот/переключения устройств; отсутствие «already running».

- 1.7 InterruptManagementIntegration
  - Действия: `short_press`/ошибка/timeout → безопасный возврат в SLEEPING; останов активных потоков.
  - Тест‑гейт: прерывание из LISTENING/PROCESSING всегда завершает корректно.

- 1.8 VoiceRecognitionIntegration (LISTENING)
  - Действия: PRESS → `voice.recording_start` → реальное `start_listening()`; RELEASE → мгновенный `voice.mic_closed` (UI), затем результат (`voice.recognition_completed/failed`).
  - Тест‑гейт: реальное распознавание работает; события приходят в правильном порядке; нет дублей.

- 1.9 ScreenshotCaptureIntegration (PROCESSING)
  - Действия: захват скриншота при входе в PROCESSING; обработка ошибок разрешения.
  - Тест‑гейт: скрин получен; отказ — событие ошибки.

- 1.10 GrpcClientIntegration (PROCESSING)
  - Действия: отправка (текст+скрин) на Azure; ретраи/backoff зависят от `network`.
  - Тест‑гейт: успешный ответ; при `DISCONNECTED` — не спамит и восстанавливается.

- 1.11 SpeechPlaybackIntegration (внутри PROCESSING)
  - Действия: воспроизведение ответа; по окончании публикует `processing.complete`.
  - Тест‑гейт: аудио доигрывается; завершение переводит в SLEEPING.

- 1.12 FSM + Workflows (3 файла)
  - Действия: формализовать переходы/таймауты/анти‑гонки; внедрить `sleeping_workflow.py`, `listening_workflow.py`, `processing_workflow.py` (подэтапы: capture→grpc→playback).
  - Тест‑гейт: нет гонок; сценарии с прерыванием/таймаутами стабильны.

**Exit‑критерий Этапа 1**: Полный цикл S→L→P→S проходит стабильно; логика через EventBus; интеграции тонкие; логи без PII.

---

## 2) Поставка: PKG + подпись/нотаризация + Sparkle
**Цель**: установка из PKG и автообновления с Azure.

- 2.1 Сборка .app
  - Действия: py2app (рекомендовано для rumps) → `.app`; `entitlements.plist` (Mic, Screen Recording, Notifications, Accessibility).
  - Тест‑гейт: `.app` запускается локально.

- 2.2 Подпись .app
  - Действия: `codesign` (Developer ID Application, hardened runtime, entitlements).
  - Тест‑гейт: `codesign --verify --deep --strict` OK.

- 2.3 Сборка и подпись PKG
  - Действия: `productbuild` → `.pkg`; `productsign` (Developer ID Installer).
  - Тест‑гейт: локальная установка PKG проходит.

- 2.4 Нотарификация и staple
  - Действия: `notarytool submit --wait` для `.pkg`; `stapler staple`.
  - Тест‑гейт: установка PKG на чистого пользователя без Gatekeeper предупреждений.

- 2.5 Публикация и Sparkle
  - Действия: загрузить `.pkg` и `appcast.xml` в Azure Blob Static Website или App Service; обновить `appcast_url` в клиенте; silent‑режим.
  - Тест‑гейт: клиент видит и ставит обновление с Azure без диалогов.

**Exit‑критерий Этапа 2**: PKG подписан/нотарифицирован/степлен; доступен по HTTPS; Sparkle обновляет приложение.

---

## 3) Сервер: Azure (без Docker/CI) + AppCast/PKG хостинг
**Цель**: gRPC endpoint (TLS/HTTP2) и хостинг артефактов.

- 3.1 Деплой сервера
  - Действия: Azure App Service (Python) или VM (Ubuntu); доставка кода ZIP/из GitHub; `pip install -r requirements.txt`; запуск `grpc_server.py` (HTTP/2, TLS); переменные из `config.env` → App Settings.
  - Тест‑гейт: `/health`/gRPC health “Serving”.

- 3.2 Домен и HTTPS
  - Действия: `api.<domain>`; включить HTTPS и HTTP/2; валидный сертификат.
  - Тест‑гейт: TLS проверка OK, h2 активен.

- 3.3 Хостинг AppCast/PKG
  - Действия: `appcast.xml` и `.pkg` доступны по HTTPS; корректные ссылки/версии.
  - Тест‑гейт: Sparkle читает `appcast.xml` и скачивает PKG.

- 3.4 E2E с клиентом
  - Действия: прописать `grpc_host/port` в клиенте; выполнить реальный PROCESSING цикл.
  - Тест‑гейт: клиент получает ответ от Azure, воспроизводит, возвращается в SLEEPING.

**Exit‑критерий Этапа 3**: Продовый сервер доступен; клиент работает end‑to‑end; обновления распределяются с Azure.

---

## 🔁 Зависимости и порядок
- Этап 1 → Этап 2 → Этап 3. Этап 2 можно готовить к концу Этапа 1 (скрипты подписи/нотаризации). Этап 3 можно поднимать параллельно 1.9–1.11.

## ⚙️ Конфиг, логи, безопасность
- Конфиги клиента: `client/config/*.yaml` — `grpc_host`, `grpc_port`, `appcast_url`, таймауты, ретраи, backoff.
- Логи: единый формат, уровни по компонентам; без PII; ключевые события (режимы/сеть/обновления).
- Разрешения/Entitlements: Mic, Screen Recording, Notifications, Accessibility, Network — согласованы с `permissions`.
- Секреты: Apple (подпись/нотаризация) — локально/в защищенном хранилище; Azure — App Settings/Key Vault.

---

## ✅ Текущий статус (сводно)
- Готово: архитектурный каркас; интеграции tray/permissions/input/update (тихий режим).
- В работе: закрепление UX‑индикации; планирование сети/PKG/Azure.
- Далее: NetworkManagerIntegration → Audio/Interrupts → голосовой контур → PKG → Azure.

---

## 📌 Мини‑контрольные списки (пример)
- Клиент/Сеть: off/on → `network.status_changed`, tray отражает.
- Голосовой цикл: S→L→P→S — без гонок; ресурсы освобождены.
- PKG: `codesign`/`productbuild`/`productsign`/`notarytool`/`stapler` — все OK.
- Azure: health “Serving”; TLS/HTTP2 включены; `appcast.xml`/PKG по HTTPS.

---

## 🗂 Связанные документы
- `client/Docs/INTEGRATION_MASTER_PLAN.md` — подробный план интеграции.
- `client/Docs/PRODUCT_CONCEPT.md` — UX и сценарии.
- `client/PACKAGING_README.md`, `PACKAGING_README.md`, `PRODUCTION_BUILD_GUIDE.md` — упаковка.
- `AZURE_SETUP.md` — заметки по Azure (при необходимости дополнить).

---

## ☁️ Azure VM — параметры и чек‑лист переноса

### Текущие параметры (из портала Azure)
- **Resource group**: Nexy
- **Region**: Canada Central
- **VM OS**: Linux
- **Size**: Standard D2s v3 (2 vCPUs, 8 GiB)
- **Public IP (primary NIC)**: 20.151.51.172
- **VNet/Subnet**: nexy-vnet/default
- **DNS name**: Not configured (настроить ниже)
- **Subscription**: Azure subscription 1
- **Subscription ID**: 6d225f4c-756c-41ff-b361-62f248a60a2d
- **Status**: Stopped (deallocated) — перед переносом запустить

### План действий для переноса без Docker/CI
1) Сетевые настройки и безопасность
   - Закрепить Public IP как Static.
   - Настроить DNS‑имя для IP (например, `api.yourdomain.com`).
   - Открыть порты: 22 (временно под ваш IP), 80 (HTTP, для certbot), 443 (HTTPS, HTTP/2).
   - Включить UFW/NSG правила, после деплоя ограничить/закрыть 22.
2) Подготовка системы
   - Создать пользователя `nexy`; обновить систему пакетов.
   - Установить: `python3.11`, `python3.11-venv`, `nginx`, `certbot`, `python3-certbot-nginx`.
3) Доставка кода сервера (`server/`)
   - Вариант A: `scp` архива с локальной машины → `~nexy/app/server/`.
   - Вариант B: `curl -L -o release.zip` из GitHub Releases → распаковать.
   - Заполнить `config.env` по `server/config.env.example`.
   - Создать venv и установить зависимости: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
4) Сервис gRPC
   - systemd unit `nexy-grpc.service` (слушает `127.0.0.1:50051`, HTTP/2):
     - ExecStart: `/home/nexy/app/server/.venv/bin/python grpc_server.py --host 127.0.0.1 --port 50051`
     - Restart=always, WantedBy=multi-user.target
5) Nginx + TLS + статические файлы обновлений
   - Выдать сертификат: `sudo certbot --nginx -d api.yourdomain.com`.
   - Nginx 443: `listen 443 ssl http2;` и прокси `grpc_pass grpc://127.0.0.1:50051;`.
   - Папка для AppCast/PKG: `/var/www/nexy/appcast/`.
   - Раздача обновлений по `https://api.yourdomain.com/updates/` (alias на папку выше).
6) AppCast/PKG
   - Разместить `appcast.xml` и `Nexy-x.y.z.pkg` в `/var/www/nexy/appcast/`.
   - Проверить доступность: `https://api.yourdomain.com/updates/appcast.xml`.
7) Клиентские конфиги
   - `client/config/app_config.yaml` / `network_config.yaml`:
     - `grpc_host: api.yourdomain.com`, `grpc_port: 443`, `use_tls: true`.
     - `appcast_url: https://api.yourdomain.com/updates/appcast.xml`.
8) Проверки
   - `systemctl status nexy-grpc` — активен; `nginx -t` — OK; certbot — валидный cert.
   - Клиентский сценарий S→L→P→S работает; Sparkle тянет апдейт с `appcast.xml`.

### Плейсхолдеры для заполнения
- Домен (A/AAAA к 20.151.51.172): `api.yourdomain.com`
- Email для Certbot: `admin@yourdomain.com`
- Пути публикации AppCast/PKG: `/var/www/nexy/appcast/`
- Версии релизов и ссылки внутри `appcast.xml`

---

## 🔐 Подпись и нотарификация — параметры и безопасное хранение

### Данные (несекретные — фиксируем в плане)
- Apple ID (email): seregawpn@gmail.com
- Team ID (App ID Prefix): 5NKLL2CLB9
- Bundle ID (explicit): com.nexy.assistant
- Платформы: iOS, iPadOS, macOS, tvOS, watchOS, visionOS
- Название проекта: Nexy

> Примечание: App‑Specific Password передается и хранится ТОЛЬКО локально в Keychain, не коммитится в репозиторий.

### Сертификаты (плейсхолдеры — подставить точные имена из Keychain)
- Developer ID Application: "Developer ID Application: <Your Name> (5NKLL2CLB9)"
- Developer ID Installer:  "Developer ID Installer: <Your Name> (5NKLL2CLB9)"

Проверка наличия сертификатов:
```bash
security find-identity -p codesigning -v | cat
```

### Настройка notarytool (безопасное хранение App‑Specific Password)
Сохранить учетные данные в Keychain под профилем `nexy-notary` (пароль вводится локально и не попадает в git):
```bash
xcrun notarytool store-credentials nexy-notary \
  --apple-id seregawpn@gmail.com \
  --team-id 5NKLL2CLB9 \
  --keychain-profile nexy-notary
```

Нотарификация с использованием профиля:
```bash
xcrun notarytool submit Nexy-signed.pkg --keychain-profile nexy-notary --wait
xcrun stapler staple Nexy-signed.pkg
```

### Подпись .app и .pkg (шаблон команд)
```bash
# Подпись приложения (.app)
codesign --deep --force --options runtime \
  --entitlements client/entitlements.plist \
  --sign "Developer ID Application: <Your Name> (5NKLL2CLB9)" Nexy.app

# Сборка и подпись инсталлятора (.pkg)
productbuild --component Nexy.app /Applications Nexy.pkg
productsign --sign "Developer ID Installer: <Your Name> (5NKLL2CLB9)" Nexy.pkg Nexy-signed.pkg

# Нотарификация и степлинг
xcrun notarytool submit Nexy-signed.pkg --keychain-profile nexy-notary --wait
xcrun stapler staple Nexy-signed.pkg
```

### Sparkle (обновления)
- Ключи Sparkle (EdDSA): хранить приватный ключ локально/в secret‑хранилище; публичный ключ можно хранить в репозитории.
- `appcast.xml`: размещаем на Azure (см. раздел Azure VM). Ссылки на `.pkg` по HTTPS.

### Конфиги клиента (привязка к подписанному релизу)
- `client/config/app_config.yaml`:
  - `appcast_url: https://api.<domain>.com/updates/appcast.xml`
- `client/config/network_config.yaml`:
  - `grpc_host: api.<domain>.com`, `grpc_port: 443`, `use_tls: true`

### Политика безопасности
- Не коммитить App‑Specific Password, .p12 и приватные ключи Sparkle в git.
- Использовать macOS Keychain и ограниченный доступ к секретам.
- При необходимости — отдельный пользователь macOS для сборки и подписи.

---

## ⚠️ Конфиденциальные данные (временно сохранены по запросу)

> ВНИМАНИЕ: хранение секретов в репозитории небезопасно. Рекомендуется перенести в macOS Keychain/секрет‑хранилище и сменить пароль после переноса.

- Apple ID (email): seregawpn@gmail.com
- Team ID: 5NKLL2CLB9
- Bundle ID: com.nexy.assistant
- App‑Specific Password: qtiv-kabm-idno-qmbl

> После завершения настройки notarytool/CI рекомендуется: 
> 1) РОТИРОВАТЬ App‑Specific Password в Apple ID.
> 2) Удалить этот раздел из репозитория.
