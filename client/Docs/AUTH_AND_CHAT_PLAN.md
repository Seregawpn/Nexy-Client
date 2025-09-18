# 🔐 Login/Auth + Client Chat — Plan

Дата: 18 сентября 2025
Статус: Draft → Ready for Impl

## Цель
- Добавить авторизацию пользователя (token‑based) и клиентский текстовый чат (CLI/минимальный UI) поверх существующего gRPC‑потока.

## Требования
- Хранение токена безопасно (macOS Keychain).
- Добавление `authorization: Bearer <token>` в metadata всех gRPC запросов.
- CLI чат: ввод текста, показ потоковых `text_chunk`, воспроизведение `audio_chunk` через текущий плеер.
- Состояние: активная сессия, история сообщений в памяти (N сообщений), сброс/логаут.
- Грейсфул при оффлайне: сообщения в очередь, повтор при восстановлении.

## Архитектура/интеграции
- `modules/grpc_client/core/grpc_client.py` — добавить поддержку `metadata` (dict → список пар) для StreamAudio; прокинуть извне.
- `integration/integrations/grpc_client_integration.py` — принимать токен, формировать metadata; публиковать события об ошибках авторизации.
- Keychain helper (новый модуль): `client/modules/auth/keychain.py` (get_token/set_token/delete_token) через `keyring`/Security.
- CLI чат: `client/tools/chat_cli.py` (минимум) — читает токен, предлагает логин, затем REPL.

## Сценарии
1) Login: пользователь вводит токен → сохранение в Keychain → проверка при первом запросе (ответ 401/403 → ошибка/повтор).
2) Chat: ввод текста → захват скриншота (опционально) → gRPC StreamAudio(prompt, screenshot, hwid, metadata) → отображение текста/аудио.
3) Logout: удаление токена → очистка состояния.

## Точки изменений
- gRPC: `GrpcClient.stream_audio()` добавить параметр `metadata: Optional[Dict[str,str]] = None` и проброс в `StreamingServiceStub(...).StreamAudio(request, timeout=..., metadata=metadata_list)`.
- Integration: хранить актуальный токен, обновлять по событию `auth.token_updated`.
- CLI: команды `/login <token>`, `/logout`, `/send <text>`, `/quit`.

## Обработка ошибок
- Нет токена → предупреждение и предложение `/login`.
- 401/403 → ошибка авторизации, предложение перелогиниться.
- Сетевые ошибки → retry через существующий RetryManager.

## Acceptance Criteria
- Токен сохраняется/читается из Keychain.
- gRPC вызовы содержат `authorization` metadata.
- CLI чат принимает ввод и отображает потоковый текст; аудио воспроизводится через текущий плеер.
- Логаут удаляет токен и блокирует отправку до повторного логина.

## Далее
- (Опционально) Обновить трэй‑меню: пункт Login/Logout, индикация авторизации.
- (Опционально) История чата в файл (локально), с ротацией.

