# 🧪 Тесты Nexy Client

Директория содержит тестовые скрипты для проверки критических компонентов перед упаковкой приложения.

## 📋 Список тестов

### 🚀 **test_all_before_packaging.py** (Главный тест)
Комплексное тестирование всех компонентов перед упаковкой.

**Запускает:**
- ✅ PyObjC Fix тест
- ✅ Resource Paths тест
- ✅ Packaged Simulation тест
- ✅ FFmpeg availability тест
- ✅ Welcome Player integration тест

**Запуск:**
```bash
cd /Users/sergiyzasorin/Development/Nexy/client
python tests/test_all_before_packaging.py
```

---

### 🔧 **test_pyobjc_fix.py**
Проверяет работу фикса NSMakeRect для PyObjC/rumps.

**Что проверяет:**
- Foundation/AppKit импорты
- Наличие NSMakeRect символов
- Совместимость с rumps

**Запуск:**
```bash
python tests/test_pyobjc_fix.py
```

---

### 📦 **test_packaged_simulation.py**
Симулирует различные режимы PyInstaller без полной пересборки.

**Тестирует:**
- Development режим (baseline)
- PyInstaller onefile режим
- PyInstaller bundle (.app) режим

**Запуск:**
```bash
python tests/test_packaged_simulation.py
```

---

### 🔍 **test_resource_path.py**
Диагностика путей к ресурсам в различных режимах.

**Проверяет:**
- Определение базового пути
- Существование ресурсов
- WelcomeConfig настройки

**Запуск:**
```bash
python tests/test_resource_path.py
```

---

## 🎯 Рекомендуемый workflow

### Перед упаковкой приложения:

1. **Запустите главный тест:**
   ```bash
   python tests/test_all_before_packaging.py
   ```

2. **Убедитесь, что все тесты прошли (✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!)**

3. **Выполните упаковку:**
   ```bash
   ./packaging/build_final.sh
   ```

4. **Проверьте установленное приложение:**
   - Приложение запускается без ошибок
   - Звук приветствия воспроизводится
   - Проверьте логи: `tail -f ~/Library/Logs/Nexy/nexy.log`

---

## ⚠️ Важные замечания

- **Все тесты настроены для запуска из корня проекта**
- **CLIENT_ROOT автоматически определяется как parent директория**
- **Тесты НЕ требуют установки дополнительных зависимостей**
- **При изменении структуры проекта обновите пути в тестах**

---

## 🐛 Устранение проблем

### Тест не находит модули
```bash
# Убедитесь, что запускаете из корня проекта
cd /Users/sergiyzasorin/Development/Nexy/client
python tests/test_all_before_packaging.py
```

### FFmpeg тест падает
```bash
# Проверьте наличие ffmpeg
ls -lh resources/ffmpeg/ffmpeg
```

### PyObjC тест падает
```bash
# Переустановите PyObjC
pip install --upgrade pyobjc-core pyobjc-framework-Cocoa
```

---

## 📝 Добавление новых тестов

При добавлении новых тестов:

1. Создайте файл `test_<название>.py` в этой директории
2. Используйте стандартную структуру путей:
   ```python
   CLIENT_ROOT = Path(__file__).parent.parent
   sys.path.insert(0, str(CLIENT_ROOT))
   ```
3. Добавьте тест в `test_all_before_packaging.py`
4. Обновите этот README

---

**Последнее обновление:** Октябрь 2025  
**Статус:** ✅ Все тесты актуальны и работают

