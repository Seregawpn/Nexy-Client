# Этап 1: Аудит бинарников и ресурсов

**Дата аудита:** 2025-10-09
**Дата обновления:** 2025-10-10
**Статус:** ✅ COMPLETED - Все бинарники обновлены и подписаны

## 1. Найденные бинарники

### 1.1 FFmpeg
**Расположение:** [`resources/ffmpeg/ffmpeg`](resources/ffmpeg/ffmpeg)

```bash
Тип:         Mach-O 64-bit executable arm64
Архитектура: arm64 (non-fat, single arch)
Размер:      39 MB
Подпись:     adhoc (linker-signed)
Identifier:  ffmpeg
```

**Динамические зависимости:**
- ✅ Только системные фреймворки (VideoToolbox, AudioToolbox, CoreAudio, AVFoundation, etc.)
- ✅ Нет внешних библиотек, требующих упаковки

**Extended Attributes:**
```
com.apple.provenance: (пустой)
```

**Проблемы:**
- ⚠️ **adhoc подпись** — будет перезаписана при упаковке
- ⚠️ **single arch (arm64)** — для Intel Mac потребуется отдельная версия или universal binary

---

### 1.2 SwitchAudioSource
**Расположение:** [`resources/audio/SwitchAudioSource`](resources/audio/SwitchAudioSource)

```bash
Тип:         Mach-O 64-bit executable arm64
Архитектура: arm64 (non-fat, single arch)
Размер:      55 KB
Подпись:     adhoc
Identifier:  SwitchAudioSource-555549440e5346ed505639e3b076424d2d05b173
```

**Динамические зависимости:**
- ✅ Только системные фреймворки (CoreServices, CoreAudio, CoreFoundation)
- ✅ Минимальные зависимости

**Extended Attributes:**
```
com.apple.provenance: (пустой)
```

**Проблемы:**
- ⚠️ **adhoc подпись** — будет перезаписана при упаковке
- ⚠️ **single arch (arm64)** — для Intel Mac потребуется отдельная версия

---

### 1.3 FLAC
**Статус:** ✅ ДОБАВЛЕН

**Расположение:** [`resources/audio/flac`](resources/audio/flac)

```bash
Тип:         Mach-O 64-bit executable arm64
Архитектура: arm64 (non-fat, single arch)
Размер:      452 KB
Подпись:     adhoc → Developer ID Application
Версия:      1.5.0 (обновлено с устаревшего x86_64 v1.0)
```

**Источник:** `~/Downloads/flac-1.5.0/src/flac/flac`

**Обновление:** Заменил устаревший `speech_recognition/flac-mac` (x86_64, SDK 10.6) на современный FLAC 1.5.0 arm64.

**Подробности:** См. [04_FLAC_UPGRADE.md](04_FLAC_UPGRADE.md)

---

## 2. Структура ресурсов

```
resources/
├── audio/
│   ├── SwitchAudioSource (55 KB, arm64)
│   └── flac (452 KB, arm64, v1.5.0) ← НОВОЕ
└── ffmpeg/
    └── ffmpeg (39 MB, arm64)
```

✅ **Чисто:** AppleDouble файлы (._*) не обнаружены
✅ **Чисто:** Скрытые файлы (.DS_Store и др.) отсутствуют

---

## 3. PyInstaller Spec

**Статус:** ✅ СОЗДАН

**Файл:** [`packaging/Nexy.spec`](packaging/Nexy.spec)

**Включает:**
- ✅ `datas` для resources/ffmpeg/ffmpeg
- ✅ `datas` для resources/audio/SwitchAudioSource
- ✅ `datas` для resources/audio/flac (FLAC 1.5.0)
- ✅ 50+ hiddenimports (gRPC, PyObjC, rumps, pynput, все модули)
- ✅ Фильтр устаревшего flac-mac из speech_recognition
- ✅ Info.plist с всеми permissions
- ✅ Entitlements reference

**Подробности:** См. [02_SPEC_CREATION.md](02_SPEC_CREATION.md)

---

## 4. Критичные находки

### 🔴 БЛОКЕРЫ

1. **Отсутствует Nexy.spec**
   - Без него `build_final.sh` упадёт на строке 136
   - Требуется создание spec-файла

### ⚠️ ПРЕДУПРЕЖДЕНИЯ

2. **Архитектура arm64-only**
   - FFmpeg: только arm64
   - SwitchAudioSource: только arm64
   - **Риск:** приложение не запустится на Intel Mac
   - **Решение:** либо создать universal binary, либо явно указать в документации "Apple Silicon only"

3. **adhoc подписи бинарников**
   - Обе бинарники подписаны adhoc
   - **Риск:** при упаковке в .app могут возникнуть конфликты подписей
   - **Решение:** `build_final.sh` уже содержит правильную последовательность подписи (строки 176-204)

4. **Extended attributes**
   - Обнаружен `com.apple.provenance` (пустой)
   - **Риск:** может вызвать проблемы при notarization
   - **Решение:** `build_final.sh` уже содержит агрессивную очистку (строки 39-80)

---

## 5. Рекомендации

### Приоритет 1 (СРОЧНО)
- [ ] **Создать `packaging/Nexy.spec`** с правильной конфигурацией PyInstaller
- [ ] Убедиться, что все ресурсы (ffmpeg, SwitchAudioSource) включены в spec

### Приоритет 2 (ВАЖНО)
- [ ] Решить вопрос с архитектурой: либо добавить x86_64 версии бинарников, либо явно документировать "arm64-only"
- [ ] Протестировать подпись вложенных бинарников в процессе сборки

### Приоритет 3 (ОПЦИОНАЛЬНО)
- [ ] Рассмотреть добавление FLAC, если требуется для функционала
- [ ] Оптимизировать размер FFmpeg (39 MB — можно ли уменьшить через --disable-unused-codecs?)

---

## 6. Следующий шаг

**НЕ МОЖЕМ** перейти к Этапу 2 без создания `Nexy.spec`.

**Требуется:**
1. Создать spec-файл на основе структуры проекта
2. Провести тестовую сборку с `pyinstaller packaging/Nexy.spec`
3. Проверить, что бинарники корректно включены

---
**Подготовлено:** Claude Code
**Версия документа:** 1.0
