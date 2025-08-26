# 🚀 **ИНТЕГРАЦИЯ GEMINI LIVE API В TEXT_PROCESSOR**

## 🎯 **ОПИСАНИЕ**

Успешно интегрирован **Google Gemini Live API** в `text_processor.py` с сохранением **LangChain как fallback**. Система автоматически выбирает между Live API и LangChain в зависимости от доступности.

## 🔧 **ЧТО ДОБАВЛЕНО**

### **1. Новые импорты**
```python
# 🚀 НОВЫЙ: Gemini Live API (основной)
from google import genai
from google.genai import types

# 🔄 FALLBACK: LangChain + Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
```

### **2. Гибридная инициализация**
- **Основной**: Gemini Live API с Google Search инструментами
- **Fallback**: LangChain для случаев недоступности Live API
- **Автоматическая проверка** доступности API

### **3. Новые методы**
- `generate_response_stream_live_api()` - работа через Live API
- `generate_response_stream_hybrid()` - автоматический выбор API
- `generate_response_stream()` - сохранен для обратной совместимости

## 🚀 **КАК ИСПОЛЬЗОВАТЬ**

### **Автоматический выбор API (рекомендуется)**
```python
# Автоматически выбирает между Live API и LangChain
async for chunk in processor.generate_response_stream_hybrid(
    prompt="Ваш запрос",
    hardware_id="user_id",
    screenshot_base64="base64_string"  # опционально
):
    print(chunk, end="", flush=True)
```

### **Принудительное использование Live API**
```python
# Только Live API (если доступен)
async for chunk in processor.generate_response_stream_live_api(
    prompt="Ваш запрос",
    hardware_id="user_id",
    screenshot_data=screenshot_dict  # новый формат
):
    print(chunk, end="", flush=True)
```

### **Fallback на LangChain**
```python
# Только LangChain (fallback)
async for chunk in processor.generate_response_stream(
    prompt="Ваш запрос",
    hardware_id="user_id",
    screenshot_base64="base64_string"  # старый формат
):
    print(chunk, end="", flush=True)
```

## 📸 **ПОДДЕРЖКА ИЗОБРАЖЕНИЙ**

### **Новый формат для Live API**
```python
screenshot_data = {
    "mime_type": "image/jpeg",  # JPEG предпочтительнее
    "data": "base64_string",
    "raw_bytes": b"binary_data",
    "width": 1024,
    "height": 768,
    "size_bytes": 12345
}
```

### **Старый формат для LangChain**
```python
screenshot_base64 = "base64_string"  # WebP или JPEG
```

### **Автоматическая конвертация**
Гибридный метод автоматически конвертирует старый формат в новый для Live API.

## 🔍 **GOOGLE SEARCH ИНТЕГРАЦИЯ**

### **Автоматическая активация**
Live API автоматически использует Google Search для:
- Новостей и актуальной информации
- Поиска фактов и данных
- Обновленной информации

### **Конфигурация инструментов**
```python
self.live_config = types.LiveConnectConfig(
    tools=[
        types.Tool(
            google_search=types.GoogleSearch()
        )
    ]
)
```

## 📊 **СИСТЕМА ПАМЯТИ**

### **Совместимость**
- **Краткосрочная память** - текущая сессия
- **Долгосрочная память** - пользовательские данные
- **Автоматическое обновление** после каждого ответа

### **Фоновое обновление**
```python
# Память обновляется автоматически в фоне
asyncio.create_task(
    self._update_memory_background(hardware_id, prompt, full_response)
)
```

## 🧪 **ТЕСТИРОВАНИЕ**

### **Запуск тестов**
```bash
cd server
export GEMINI_API_KEY="your_api_key"
python test_live_api.py
```

### **Что тестируется**
1. ✅ Инициализация TextProcessor
2. ✅ Доступность Live API и LangChain
3. ✅ Текстовые запросы
4. ✅ Запросы с изображениями
5. ✅ Автоматический fallback

## 📋 **ТРЕБОВАНИЯ**

### **Зависимости**
```bash
pip install google-genai>=0.3.0
pip install langchain-google-genai>=0.0.5
pip install langchain-core>=0.1.0
```

### **Переменные окружения**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

## 🔄 **ЛОГИКА РАБОТЫ**

### **Приоритет API**
1. **🚀 Gemini Live API** - основной (с Google Search)
2. **🔄 LangChain** - fallback (базовая функциональность)

### **Автоматическое переключение**
- Live API недоступен → автоматически LangChain
- Live API ошибка → автоматически LangChain
- Оба недоступны → ошибка инициализации

### **Формат изображений**
- **Live API**: JPEG (предпочтительно) + raw_bytes
- **LangChain**: WebP/JPEG + base64
- **Автоконвертация**: старый → новый формат

## 🎯 **ПРЕИМУЩЕСТВА ИНТЕГРАЦИИ**

### **🚀 Live API**
- ✅ Google Search инструменты
- ✅ Лучшая производительность
- ✅ Поддержка инструментов
- ✅ Оптимизированный стриминг

### **🔄 LangChain Fallback**
- ✅ Надежность
- ✅ Обратная совместимость
- ✅ Простота использования
- ✅ Стабильность

### **🎯 Гибридный подход**
- ✅ Автоматический выбор
- ✅ Максимальная доступность
- ✅ Гибкость использования
- ✅ Простота миграции

## 🚨 **ВАЖНЫЕ ЗАМЕЧАНИЯ**

### **Формат изображений**
- **JPEG предпочтительнее** для Live API
- **WebP поддерживается** для обратной совместимости
- **Автоматическая конвертация** в гибридном режиме

### **API ключи**
- **Один ключ** для обоих API
- **Автоматическая проверка** доступности
- **Graceful fallback** при ошибках

### **Память**
- **Совместима** с обоими API
- **Автоматическое обновление** после ответов
- **Фоновая обработка** для производительности

## 🎉 **ГОТОВО К ИСПОЛЬЗОВАНИЮ!**

Ваш `text_processor.py` теперь поддерживает:
- ✅ **Gemini Live API** с Google Search
- ✅ **LangChain fallback** для надежности
- ✅ **Автоматический выбор** API
- ✅ **Поддержку изображений** в обоих форматах
- ✅ **Систему памяти** для персонализации
- ✅ **Стриминг ответов** в реальном времени

**Используйте `generate_response_stream_hybrid()` для максимальной совместимости и производительности!**
