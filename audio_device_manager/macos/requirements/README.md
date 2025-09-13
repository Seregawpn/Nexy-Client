# 📋 ТРЕБОВАНИЯ ДЛЯ MACOS УПАКОВКИ

Эта папка содержит все необходимые требования и спецификации для упаковки, подписания и нотаризации модуля `audio_device_manager` на macOS.

## 📁 СТРУКТУРА ФАЙЛОВ

### 📖 `packaging_requirements.md`
**Полное руководство по упаковке** - содержит детальные требования для:
- Упаковки приложения
- Подписания кода (Code Signing)
- Сертификации (Hardened Runtime)
- Нотаризации (Notarization)
- PKG упаковки

### ⚡ `quick_checklist.md`
**Быстрый чеклист** - краткий список основных требований для быстрой проверки:
- Основные зависимости
- Критические точки
- Команды для проверки

### 🔧 `technical_specs.md`
**Технические спецификации** - детальные технические требования:
- Системные требования
- Конфигурация PyInstaller
- Entitlements спецификация
- PKG спецификация
- Процесс нотаризации

## 🚀 БЫСТРЫЙ СТАРТ

1. **Прочитайте** `quick_checklist.md` для понимания основных требований
2. **Изучите** `packaging_requirements.md` для детального понимания процесса
3. **Используйте** `technical_specs.md` для технической реализации

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

- Все требования актуальны для **macOS 10.15+**
- Требуется **Apple Developer Account** для подписания и нотаризации
- **SwitchAudioSource** должен быть установлен в системе
- Модуль требует специальных **entitlements** для работы с аудио устройствами

## 🔗 СВЯЗАННЫЕ ДОКУМЕНТЫ

- [Apple Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)
- [Hardened Runtime Documentation](https://developer.apple.com/documentation/security/hardened_runtime)
- [Notarization Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)

---

*Версия: 1.0.0 | Дата: $(date) | Автор: Nexy Development Team*
