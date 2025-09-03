# 🎯 **Руководство по настройке переключения устройств SoundDevice**

## **📋 Что это дает:**

✅ **Автоматическое переключение** между аудио устройствами  
✅ **Умное определение** Bluetooth профилей (HFP/A2DP)  
✅ **Адаптивные параметры** для каждого устройства  
✅ **Безопасное восстановление** после ошибок  
✅ **Мониторинг в реальном времени** изменений устройств  

---

## **🚀 Быстрый старт:**

### **1. Запуск демонстрации:**
```bash
python3 test_device_switching_demo.py
```

### **2. Тестирование автоматического переключения:**
- Подключите/отключите наушники
- Измените системное устройство по умолчанию
- Наблюдайте за автоматическим переключением

---

## **⚙️ Основные настройки:**

### **Инициализация AudioPlayer:**
```python
from audio_player import AudioPlayer

# Создание с автоматическим мониторингом
player = AudioPlayer(
    sample_rate=48000,    # Частота дискретизации
    channels=2,           # Количество каналов
    dtype='int16'         # Тип данных
)

# Мониторинг запускается автоматически!
```

### **Параметры мониторинга:**
```python
# В __init__ класса AudioPlayer:
self.device_check_interval = 2.0      # Проверка каждые 2 секунды
self.device_switch_threshold = 1.0    # Минимальный интервал между переключениями
```

---

## **🔄 Методы переключения устройств:**

### **1. Автоматическое переключение:**
```python
# Работает автоматически при изменении системного устройства
# Ничего делать не нужно!
```

### **2. Принудительное переключение:**
```python
# По имени устройства
player.switch_to_device("AirPods Pro")

# По индексу устройства
player.switch_to_device(device_index=2)

# По части имени
player.switch_to_device("AirPods")  # Найдет "AirPods Pro", "AirPods Max"
```

### **3. Принудительное обновление:**
```python
# Обновляет информацию об устройствах
player.force_device_refresh()
```

---

## **📱 Работа с устройствами:**

### **Получение списка устройств:**
```python
devices = player.list_available_devices()

for device in devices:
    print(f"📱 {device['name']}")
    print(f"   Индекс: {device['index']}")
    print(f"   Каналы: {device['max_channels']}")
    print(f"   Частота: {device['default_samplerate']} Hz")
    print(f"   По умолчанию: {'⭐' if device['is_default'] else '  '}")
```

### **Информация о текущем устройстве:**
```python
current_info = player.get_current_device_info()

if current_info:
    print(f"🎯 Текущее устройство: {current_info['name']}")
    print(f"   Каналы: {current_info['max_channels']}")
    print(f"   Частота: {current_info['default_samplerate']} Hz")
```

---

## **🎧 Bluetooth профили:**

### **Автоматическое определение:**
```python
# HFP (Hands-Free Profile) - гарнитура
# Автоматически используется низкое качество:
# - 1 канал, 8-22 kHz, для звонков

# A2DP (Advanced Audio Distribution Profile) - качество
# Автоматически используется высокое качество:
# - 2 канала, 44-48 kHz, для музыки
```

### **Ручная настройка профиля:**
```python
# В audio_player.py можно изменить параметры:
def _detect_bluetooth_profile(self, device_info):
    # Настройте под ваши нужды
    if 'airpods' in device_name.lower():
        # Специальные настройки для AirPods
        return 'a2dp', [
            {'channels': 2, 'samplerate': 48000, 'dtype': 'int16'},
            {'channels': 2, 'samplerate': 44100, 'dtype': 'int16'},
        ]
```

---

## **⚡ Оптимизация производительности:**

### **Быстрое реагирование (наушники):**
```python
self.device_check_interval = 1.0      # Проверка каждую секунду
self.device_switch_threshold = 0.5    # Минимальный интервал между переключениями
```

### **Стабильность (домашняя система):**
```python
self.device_check_interval = 3.0      # Проверка каждые 3 секунды
self.device_switch_threshold = 2.0    # Более длительный интервал
```

### **Экономия ресурсов (ноутбук):**
```python
self.device_check_interval = 5.0      # Проверка каждые 5 секунд
self.device_switch_threshold = 3.0    # Стабильный интервал
```

---

## **🛠️ Устранение проблем:**

### **Устройство не переключается:**
```python
# 1. Проверьте логи
logger.info("🔄 Переключение устройств...")

# 2. Принудительно обновите
player.force_device_refresh()

# 3. Проверьте список устройств
devices = player.list_available_devices()
```

### **Ошибки инициализации:**
```python
# В audio_player.py есть fallback механизм:
def _safe_init_stream(self):
    try:
        # Попытка с основными параметрами
        return self._init_stream_with_params()
    except Exception as e:
        logger.warning(f"⚠️ Основная инициализация не удалась: {e}")
        # Fallback на универсальные параметры
        return self._init_stream_fallback()
```

### **Проблемы с Bluetooth:**
```python
# Проверьте профиль устройства:
profile, params = player._detect_bluetooth_profile(device_info)
logger.info(f"🎧 Профиль: {profile}, параметры: {params}")

# Принудительно переключитесь:
player.switch_to_device("AirPods Pro")
```

---

## **📊 Мониторинг и логирование:**

### **Включение подробных логов:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# В логах вы увидите:
# 🔄 Мониторинг устройств запущен
# 📱 Изменение устройства: MacBook Speakers → AirPods Pro
# 🎧 Определен профиль: A2DP (качество)
# ✅ Поток перезапущен: ch=2, sr=48000
```

### **Отслеживание производительности:**
```python
# Время переключения устройств
start_time = time.time()
player.switch_to_device("AirPods Pro")
switch_time = time.time() - start_time
logger.info(f"⚡ Переключение заняло: {switch_time:.3f} сек")
```

---

## **🎯 Лучшие практики:**

### **1. Всегда используйте try-catch:**
```python
try:
    success = player.switch_to_device("AirPods Pro")
    if success:
        logger.info("✅ Переключение успешно")
    else:
        logger.warning("⚠️ Переключение не удалось")
except Exception as e:
    logger.error(f"❌ Ошибка переключения: {e}")
```

### **2. Проверяйте состояние перед переключением:**
```python
if player.is_playing:
    logger.info("🔄 Воспроизведение активно, перезапускаю поток...")
    # Сохраните состояние и восстановите после переключения
```

### **3. Используйте адаптивные параметры:**
```python
# Не жестко задавайте параметры:
# ❌ Плохо: channels=2, samplerate=48000
# ✅ Хорошо: используйте _get_adaptive_configs()
```

---

## **🚀 Готово к использованию!**

Теперь ваше приложение будет:
- ✅ **Автоматически переключаться** между устройствами
- ✅ **Умно адаптироваться** к Bluetooth профилям  
- ✅ **Безопасно восстанавливаться** после ошибок
- ✅ **Эффективно использовать** ресурсы системы

**Запустите демонстрацию и убедитесь в работе!** 🎵
