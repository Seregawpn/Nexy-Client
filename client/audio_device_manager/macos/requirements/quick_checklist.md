# ⚡ БЫСТРЫЙ ЧЕКЛИСТ ДЛЯ MACOS УПАКОВКИ

## 🎯 ОСНОВНЫЕ ТРЕБОВАНИЯ

### Упаковка:
- [ ] PyObjC (Core Audio, Foundation, AppKit)
- [ ] SwitchAudioSource установлен
- [ ] Все core модули включены
- [ ] Скрытые импорты настроены

### Подписание:
- [ ] Developer ID Application сертификат
- [ ] Entitlements файл с аудио разрешениями
- [ ] Hardened Runtime включен
- [ ] Все библиотеки подписаны

### Нотаризация:
- [ ] App-Specific Password настроен
- [ ] Team ID указан
- [ ] Пакет загружен в Apple
- [ ] Тикет прикреплен

### Тестирование:
- [ ] Работа на чистой системе
- [ ] Совместимость с macOS 10.15+
- [ ] Работа с Bluetooth наушниками
- [ ] Корректность после перезагрузки

---

## 🔧 КОМАНДЫ ДЛЯ ПРОВЕРКИ

```bash
# Проверка подписи
codesign -dv --verbose=4 audio_device_manager

# Проверка entitlements
codesign -d --entitlements - audio_device_manager

# Проверка нотаризации
spctl -a -v audio_device_manager

# Проверка зависимостей
otool -L audio_device_manager
```

---

## ⚠️ КРИТИЧЕСКИЕ ТОЧКИ

1. **SwitchAudioSource** должен быть в PATH
2. **Core Audio** требует специальных entitlements
3. **Bluetooth** устройства нуждаются в дополнительных разрешениях
4. **Hardened Runtime** должен быть включен для нотаризации

---

*Версия: 1.0.0 | Дата: $(date)*
