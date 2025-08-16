# MVP 1: Детальный план разработки
## "Голосовой ассистент для незрячих с управлением пробелом"

---

## Обзор проекта

### **Цель MVP 1:**
Создать работающий голосовой ассистент для незрячих пользователей с управлением через пробел, который может анализировать экран и отвечать голосом.

### **Временные рамки:** 3 недели
### **Архитектура:** Клиент-серверная (gRPC)
### **Целевая платформа:** macOS

---

## Концепция управления

### **Принцип работы:**
```
🎯 Долгое нажатие пробела (600мс) → Активирует ассистента (читает экран)
🎯 Короткий пробел → Перебивает ассистента (слушает вопрос)
🎯 Долгое нажатие (когда активен) → Выключает ассистента полностью
```

### **Логика состояний:**
```
🔄 inactive → Долгое нажатие → active (активируется)
🔄 active → Короткий пробел → interrupted (перебит)
🔄 active → Долгое нажатие → inactive (выключение)
🔄 interrupted → Короткий пробел → listening (слушает)
🔄 listening → Короткий пробел → processing (обрабатывает)
```

### **Умная защита от конфликтов:**
- **В текстовых полях** → пробел работает как обычно (набор текста)
- **Вне текстовых полей** → пробел запускает ассистента
- **Определение контекста** → через macOS Accessibility API
- **VoiceOver совместимость** → не мешает, не конфликтует

---

## Техническая архитектура

### **1. Клиентская часть (macOS App)**

#### **Компоненты:**
```python
class AssistantClient:
    def __init__(self):
        # 1. Управление пробелом (Event Tap)
        self.space_controller = SpaceController()
        
        # 2. Edge TTS (высокое качество, бесплатно)
        self.edge_tts = EdgeTTSEngine()
        
        # 3. Локальное распознавание речи (STT)
        self.speech_recognition = LocalSpeechRecognition()
        
        # 4. Кэш изображений (для офлайн работы)
        self.image_cache = ImageCache()
        
        # 5. gRPC клиент для связи с сервером
        self.grpc_client = AssistantGrpcClient()
        
        # 6. Очередь задач (для стабильности)
        self.task_queue = TaskQueue()
```

#### **Функциональность:**
- **Захват экрана** - PyObjC + Core Graphics
- **Управление пробелом** - Event Tap + Accessibility API
- **Edge TTS** - Microsoft нейронные голоса (бесплатно)
- **Локальный STT** - SpeechRecognition + Google Speech API
- **Кэширование** - локальное хранение результатов
- **gRPC связь** - с сервером только для LLM анализа

### **2. Серверная часть (Backend)**

#### **Компоненты:**
```python
class AssistantServer:
    def __init__(self):
        # 1. LLM анализ (Gemini, GPT)
        self.llm_service = LLMService()
        
        # 2. Качественный TTS (Azure, Google) - опционально
        self.tts_service = TTSService()
        
        # 3. Анализ изображений (OpenCV, ML)
        self.image_analyzer = ImageAnalyzer()
        
        # 4. База данных (пользователи, кэш)
        self.database = Database()
        
        # 5. gRPC сервер
        self.grpc_server = AssistantGrpcServer()
```

#### **Функциональность:**
- **LLM анализ** - Gemini 1.5 Flash для анализа экранов
- **TTS** - Качественный синтез речи (опционально)
- **Обработка изображений** - анализ и оптимизация
- **Хранение данных** - пользователи, аналитика, кэш

### **3. Локальное распознавание речи (STT)**

#### **Компоненты:**
```python
import speech_recognition as sr

class LocalSpeechRecognition:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Настройки для лучшего качества
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
    def listen_for_command(self):
        """Слушает команду пользователя"""
        
        try:
            with self.microphone as source:
                # Подстраиваемся под шум
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Слушаем аудио
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                
                # Распознаём через Google Speech API (бесплатно)
                text = self.recognizer.recognize_google(audio, language='ru-RU')
                
                return text
                
        except sr.WaitTimeoutError:
            return "Таймаут ожидания речи"
        except sr.UnknownValueError:
            return "Речь не распознана"
        except sr.RequestError as e:
            return f"Ошибка распознавания: {e}"
```

#### **Функциональность:**
- **SpeechRecognition** - основная библиотека
- **Google Speech API** - бесплатное распознавание
- **Локальная обработка** - нет задержки сети
- **Поддержка RU/EN** - многоязычность
- **Fallback механизм** - обработка ошибок

---

## Детальный план по неделям

---

### **Неделя 1: Базовая система**

#### **День 1-2: Фоновая система управления пробелом**
```python
# Фоновый режим работы
- Ассистент работает всегда в фоне
- Долгое нажатие пробела → активация ассистента
- Короткий пробел → перебивание ассистента
- Долгое нажатие (когда активен) → выключение
- Защита текстовых полей → пробел работает как обычно
- Определение контекста через Accessibility API
```

**Технические задачи:**
- [ ] Настройка Event Tap для перехвата пробела
- [ ] Реализация логики долгого/короткого нажатия
- [ ] Интеграция с Accessibility API для определения контекста
- [ ] Защита текстовых полей от перехвата
- [ ] Тестирование различных сценариев нажатия

**Результат:** Фоновая система управления через пробел без конфликтов

#### **День 3-4: Захват экрана + Система аналитики**
```python
# Система захвата экрана
- PyObjC + Core Graphics
- Только активное окно
- Сжатие до 1024px, WebP формат
- Метаданные: приложение, заголовок окна
- Оптимизация размера (≤2MB)

# Система аналитики и идентификации
- Идентификация пользователя по железу (MAC, Serial, UUID)
- Логирование всех ключевых событий
- Отправка метрик производительности на сервер
- Отслеживание ошибок и проблем
- Анонимная статистика использования
```

**Технические задачи:**
- [ ] Интеграция PyObjC + Core Graphics
- [ ] Получение списка активных окон
- [ ] Захват изображения активного окна
- [ ] Сжатие и оптимизация изображения
- [ ] Извлечение метаданных окна
- [ ] **Создание системы идентификации пользователя**
- [ ] **Реализация логирования событий**
- [ ] **Настройка отправки метрик на сервер**
- [ ] Тестирование на разных приложениях

**Результат:** Можно захватывать экран, получать информацию об окне И собирать аналитику работы системы

#### **День 5-7: Локальное распознавание речи + Аналитика событий**
```python
# Локальное распознавание речи
- SpeechRecognition для STT
- PyAudio для записи аудио
- 16kHz, моно, float32
- Распознавание через Google Speech API (бесплатно)
- Обработка команд и вопросов
- Fallback при ошибках распознавания

# Система аналитики событий
- Логирование всех взаимодействий с ассистентом
- Отслеживание качества распознавания речи
- Метрики производительности STT
- Статистика использования команд
- Анализ паттернов взаимодействия
```

**Технические задачи:**
- [ ] Установка SpeechRecognition + PyAudio
- [ ] Настройка микрофона и параметров аудио
- [ ] Интеграция с Google Speech API
- [ ] Обработка команд: "что на экране", "повтори", "стоп"
- [ ] Fallback механизм при ошибках
- [ ] **Интеграция аналитики с STT**
- [ ] **Логирование качества распознавания**
- [ ] **Отслеживание метрик производительности**
- [ ] Тестирование качества распознавания

**Результат:** Локальное распознавание речи работает быстро и бесплатно + собирается аналитика всех взаимодействий

---

### **Неделя 2: LLM и анализ**

#### **День 1-3: Интеграция с Gemini**
```python
# LLM клиент
- Google Generative AI
- Простой промпт для анализа экрана
- JSON ответ: описание + действия
- Обработка ошибок API
- Кэширование результатов
```

**Технические задачи:**
- [ ] Настройка Google Generative AI
- [ ] Создание промпта для анализа экранов
- [ ] Парсинг JSON ответов
- [ ] Обработка ошибок и таймаутов
- [ ] Система кэширования результатов
- [ ] Тестирование различных типов экранов

**Результат:** LLM анализирует скриншоты и даёт осмысленные ответы

#### **День 4-5: TTS система**
```python
# Синтез речи
- Microsoft Edge TTS (бесплатно, высокое качество)
- Нейронные голоса для RU/EN
- Настраиваемая скорость и стиль
- Остановка речи по команде
- Локальный fallback при ошибках сети
- Интеграция с локальным STT
```

**Технические задачи:**
- [ ] Установка и настройка edge-tts
- [ ] Выбор оптимальных голосов для RU/EN
- [ ] Управление скоростью и стилем речи
- [ ] Остановка речи по команде
- [ ] Интеграция с локальным STT
- [ ] Fallback механизм при ошибках сети
- [ ] Тестирование качества нейронных голосов

**Результат:** Ассистент может озвучивать ответы и понимать команды

#### **День 6-7: Интеграция компонентов + Аналитика производительности**
```python
# Связываем всё вместе
- Долгое нажатие пробела → активация ассистента
- Короткий пробел → перебивание ассистента
- Долгое нажатие (когда активен) → выключение
- Автоматическая обработка → анализ экрана → LLM → TTS
- Локальное распознавание команд и вопросов
- Обработка ошибок на каждом этапе

# Комплексная аналитика производительности
- Отслеживание времени каждого этапа обработки
- Метрики производительности LLM анализа
- Статистика успешности операций
- Анализ паттернов использования
- Выявление узких мест в системе
```

**Технические задачи:**
- [ ] Интеграция всех компонентов
- [ ] Создание основного цикла работы
- [ ] Интеграция локального STT с основным циклом
- [ ] Обработка команд: "что на экране", "повтори", "стоп"
- [ ] Обработка ошибок на каждом этапе
- [ ] **Интеграция аналитики во все компоненты**
- [ ] **Создание дашборда производительности**
- [ ] **Настройка автоматической отправки метрик**
- [ ] Тестирование полного цикла
- [ ] Оптимизация производительности

**Результат:** Полный цикл работы ассистента с локальным STT, правильным управлением пробелом И полной аналитикой производительности

---

### **Неделя 3: Качество и тестирование**

#### **День 1-3: Улучшение качества + Аналитика качества**
```python
# Оптимизация
- Качество изображения (WebP 80%)
- Скорость TTS (настраиваемая)
- Обработка ошибок сети
- Логирование всех действий
- Система мониторинга

# Аналитика качества и стабильности
- Отслеживание качества изображений
- Метрики стабильности работы
- Анализ частоты ошибок
- Мониторинг производительности в реальном времени
- Автоматические уведомления о проблемах
```

**Технические задачи:**
- [ ] Оптимизация качества WebP
- [ ] Настройка скорости TTS
- [ ] Улучшение обработки ошибок
- [ ] **Создание системы мониторинга качества**
- [ ] **Настройка автоматических уведомлений**
- [ ] **Анализ паттернов ошибок**
- [ ] Мониторинг производительности
- [ ] Оптимизация памяти

**Результат:** Стабильная работа, хорошее качество + полный мониторинг качества системы

#### **День 4-7: Тестирование и отладка**
```python
# Тестирование
- Тест на разных приложениях
- Тест с разными размерами окон
- Тест стабильности (100+ циклов)
- Тест с VoiceOver
- Подготовка к демонстрации
```

**Технические задачи:**
- [ ] Тестирование на различных приложениях
- [ ] Проверка работы с VoiceOver
- [ ] Стресс-тестирование (100+ циклов)
- [ ] Тест на разных размерах окон
- [ ] Финальная отладка
- [ ] Подготовка к демонстрации

**Результат:** MVP 1 готов к показу пользователям

---

## Технические детали

---

### **1. Protocol Buffers схема**

```protobuf
// assistant.proto
syntax = "proto3";

package assistant;

service AssistantService {
  // Основные методы
  rpc AnalyzeScreen(ScreenRequest) returns (AnalysisResponse);
  rpc ProcessVoice(VoiceRequest) returns (VoiceResponse);
  rpc GetStatus(StatusRequest) returns (StatusResponse);
  
  // Стриминг для реального времени
  rpc StreamAnalysis(stream ScreenRequest) returns (stream AnalysisResponse);
}

message ScreenRequest {
  bytes screenshot = 1;           // WebP изображение
  string app_name = 2;            // Название приложения
  string window_title = 3;        // Заголовок окна
  int64 timestamp = 4;            // Временная метка
  string user_id = 5;             // ID пользователя
}

message AnalysisResponse {
  string summary = 1;             // Описание экрана
  repeated string actions = 2;     // Список действий
  float confidence = 3;            // Уверенность
  string audio_url = 4;            // URL аудио ответа
  int32 processing_time_ms = 5;    // Время обработки
}

message VoiceRequest {
  bytes audio_data = 1;           // WAV аудио
  string language = 2;             // Язык
  string user_id = 3;             // ID пользователя
}

message VoiceResponse {
  string transcribed_text = 1;     // Распознанный текст
  string answer = 2;               // Ответ ассистента
  string audio_url = 3;            // URL аудио ответа
}
```

### **2. gRPC клиент (macOS)**

```python
import grpc
import assistant_pb2
import assistant_pb2_grpc
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AssistantGrpcClient:
    def __init__(self):
        # gRPC канал с оптимизациями
        self.channel = grpc.aio.insecure_channel(
            'localhost:50051',
            options=[
                ('grpc.max_send_message_length', 10 * 1024 * 1024),  # 10MB
                ('grpc.max_receive_message_length', 10 * 1024 * 1024),
                ('grpc.keepalive_time_ms', 30000),  # 30 сек
                ('grpc.keepalive_timeout_ms', 5000),  # 5 сек
                ('grpc.keepalive_permit_without_calls', True),
                ('grpc.http2.max_pings_without_data', 0),
                ('grpc.http2.min_time_between_pings_ms', 10000),
            ]
        )
        
        # Создаём stub
        self.stub = assistant_pb2_grpc.AssistantServiceStub(self.channel)
        
        # Пул потоков для асинхронности
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def analyze_screen(self, screenshot, metadata):
        """Анализирует экран через gRPC"""
        
        # Создаём запрос
        request = assistant_pb2.ScreenRequest(
            screenshot=screenshot,
            app_name=metadata['app_name'],
            window_title=metadata['window_title'],
            timestamp=int(time.time() * 1000),
            user_id=self.user_id
        )
        
        try:
            # Отправляем запрос с таймаутом
            response = await asyncio.wait_for(
                self.stub.AnalyzeScreen(request),
                timeout=5.0  # 5 секунд таймаут
            )
            
            return {
                'summary': response.summary,
                'actions': list(response.actions),
                'confidence': response.confidence,
                'audio_url': response.audio_url,
                'processing_time': response.processing_time_ms
            }
            
        except asyncio.TimeoutError:
            # Таймаут - используем локальный fallback
            return self.local_fallback_analysis(screenshot, metadata)
            
        except grpc.RpcError as e:
            # Ошибка gRPC - логируем и используем fallback
            print(f"gRPC ошибка: {e}")
            return self.local_fallback_analysis(screenshot, metadata)
```

### **3. gRPC сервер (Backend)**

```python
import grpc
import asyncio
from concurrent.futures import ThreadPoolExecutor
import assistant_pb2
import assistant_pb2_grpc

class AssistantGrpcServer(assistant_pb2_grpc.AssistantServiceServicer):
    def __init__(self):
        # Сервисы
        self.llm_service = LLMService()
        self.tts_service = TTSService()
        self.stt_service = STTService()
        
        # Пул потоков для тяжёлых операций
        self.executor = ThreadPoolExecutor(max_workers=20)
        
    async def AnalyzeScreen(self, request, context):
        """Анализирует экран"""
        
        start_time = time.time()
        
        try:
            # Анализируем изображение через LLM
            analysis = await self.llm_service.analyze(
                request.screenshot,
                {
                    'app_name': request.app_name,
                    'window_title': request.window_title
                }
            )
            
            # Синтезируем речь
            audio_url = await self.tts_service.synthesize(
                analysis['summary'],
                language='ru'
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return assistant_pb2.AnalysisResponse(
                summary=analysis['summary'],
                actions=analysis['actions'],
                confidence=analysis['confidence'],
                audio_url=audio_url,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            # Обрабатываем ошибки
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Ошибка анализа: {str(e)}")
            return assistant_pb2.AnalysisResponse()

def serve():
    """Запускает gRPC сервер"""
    
    server = grpc.aio.server(
        ThreadPoolExecutor(max_workers=20),
        options=[
            ('grpc.max_send_message_length', 10 * 1024 * 1024),
            ('grpc.max_receive_message_length', 10 * 1024 * 1024),
            ('grpc.keepalive_time_ms', 30000),
            ('grpc.keepalive_timeout_ms', 5000),
        ]
    )
    
    # Регистрируем сервис
    assistant_pb2_grpc.add_AssistantServiceServicer_to_server(
        AssistantGrpcServer(), server
    )
    
    # Запускаем на порту 50051
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())
```

---

## Конфигурация системы

### **config.json (клиент):**
```json
{
  "server": {
    "grpc_url": "localhost:50051",
    "timeout": 5000,
    "retry_attempts": 3
  },
  
  "space_control": {
    "long_press_threshold": 600,
    "short_press_threshold": 300,
    "text_field_protection": true
  },
  
  "screen_capture": {
    "max_width": 1024,
    "format": "webp",
    "quality": 80,
    "cache_enabled": true,
    "cache_size": 100
  },
  
  "tts": {
    "language": "ru",
    "rate": 0.5,
    "voice": "ru-RU-SvetlanaNeural",
    "style": "friendly",
    "edge_tts": true
  },
  
  "logging": {
    "level": "INFO",
    "file": "assistant.log",
    "max_size": "10MB"
  }
}
```

### **config.json (сервер):**
```json
{
  "llm": {
    "provider": "gemini",
    "model": "gemini-1.5-flash",
    "api_key": "env:GEMINI_API_KEY",
    "timeout": 10000,
    "max_tokens": 500
  },
  
  "stt": {
    "provider": "openai",
    "model": "whisper-1",
    "api_key": "env:OPENAI_API_KEY",
    "language": "ru",
    "timeout": 15000
  },
  
  "tts": {
    "provider": "azure",
    "api_key": "env:AZURE_TTS_KEY",
    "region": "eastus",
    "voice": "ru-RU-SvetlanaNeural",
    "rate": 1.0
  },
  
  "grpc": {
    "port": 50051,
    "max_workers": 20,
    "max_message_size": "10MB",
    "keepalive_time": 30000
  },
  
  "database": {
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "assistant_db",
    "user": "env:DB_USER",
    "password": "env:DB_PASSWORD"
  }
}
```

---

## Зависимости

### **requirements.txt (клиент):**
```txt
SpeechRecognition==3.10.0
PyAudio==0.2.11
edge-tts==6.1.9
grpcio==1.59.0
grpcio-tools==1.59.0
protobuf==4.24.4
Pillow==10.0.0
pyobjc-framework-Quartz==9.2
pyobjc-framework-Cocoa==9.2
keyboard==0.13.5
pygame==2.5.0
numpy==1.24.0
asyncio==3.4.3
```

### **requirements.txt (сервер):**
```txt
grpcio==1.59.0
grpcio-tools==1.59.0
protobuf==4.24.4
google-generativeai==0.3.2
Pillow==10.0.0
opencv-python==4.8.1.78
psycopg2-binary==2.9.7
fastapi==0.104.1
uvicorn==0.24.0
redis==5.0.1
```

---

## Метрики производительности

### **Целевые показатели:**
```python
# Целевые метрики
TARGET_METRICS = {
    'screen_analysis': {
        'latency_p95': 2000,      # 95% запросов < 2 сек
        'latency_p99': 5000,      # 99% запросов < 5 сек
        'throughput': 100         # 100 запросов/сек
    },
    
    'voice_processing': {
        'stt_latency_p95': 1000,  # 95% STT < 1 сек (локально)
        'stt_latency_p99': 2000,  # 99% STT < 2 сек (локально)
        'tts_latency_p95': 800,   # 95% TTS < 0.8 сек (Edge TTS)
        'tts_latency_p99': 1500,  # 99% TTS < 1.5 сек (Edge TTS)
        'stt_accuracy': 0.95      # 95% точность распознавания
    },
    
    'grpc_connection': {
        'connection_time': 100,    # Подключение < 100мс
        'keepalive_interval': 30, # Keepalive каждые 30 сек
        'reconnect_time': 500     # Переподключение < 500мс
    },
    
    'space_control': {
        'response_time': 50,       # Реакция на пробел < 50мс
        'false_positive': 0.01,   # < 1% ложных срабатываний
        'text_field_protection': 1.0  # 100% защита текстовых полей
    }
}
```

---

## Что получаем в MVP 1

✅ **Рабочий ассистент** в фоновом режиме
✅ **Управление одним пробелом** - долгий = активация/выключение, короткий = перебивание
✅ **Анализ экрана** через LLM (Gemini 1.5 Flash)
✅ **Голосовые ответы** на основе экрана (Edge TTS - нейронные голоса)
✅ **Локальное распознавание речи** - быстро, бесплатно, надёжно
✅ **Быстрое перебивание** речи одним нажатием
✅ **Умная защита** от конфликтов с текстом
✅ **gRPC архитектура** для быстрой и надёжной связи (только LLM)
✅ **Кэширование** для офлайн работы
✅ **Полная система аналитики** - отслеживание производительности, ошибок, паттернов использования
✅ **Идентификация пользователей** - уникальный ID для каждого устройства
✅ **Готов к тестированию** с незрячими пользователями

---

## Примеры использования

### **Сценарий 1: Активация и чтение экрана**
```
1. Пользователь долго держит пробел
   → Ассистент активируется
   → Читает что на экране
   → Состояние: "active"
```

### **Сценарий 2: Перебивание речи и команды**
```
2. Пользователь нажимает короткий пробел во время речи
   → Ассистент замолкает
   → Начинает слушать команду/вопрос
   → Пользователь говорит: "Что на экране?"
   → Ассистент распознаёт команду локально
   → Анализирует экран и отвечает
   → Состояние: "active"
```

### **Сценарий 3: Полное выключение**
```
3. Пользователь долго держит пробел (когда ассистент активен)
   → Ассистент полностью выключается
   → Состояние: "inactive"
```

### **Сценарий 4: Локальные команды**
```
4. Пользователь говорит: "Повтори"
   → Ассистент повторяет последний ответ
   
5. Пользователь говорит: "Стоп"
   → Ассистент останавливается
   
6. Пользователь говорит: "Что на экране?"
   → Ассистент анализирует экран и отвечает
```

---

## Следующие шаги после MVP 1

### **MVP 2 (4 недели):**
1. **Эхоподавление и шумоподавление** - WebRTC AEC + NS
2. **Голосовое прерывание** - VAD + STT
3. **Диалоговая система** - контекстный LLM
4. **Качество и тестирование** - продакшен-уровень

### **Долгосрочные планы:**
1. **Мобильная версия** - iOS/Android
2. **Облачная синхронизация** - настройки пользователей
3. **Машинное обучение** - персонализация ответов
4. **Интеграции** - с другими приложениями

---

## Преимущества новой архитектуры

### **✅ Локальный STT:**
- **Быстро** - нет задержки сети
- **Бесплатно** - Google Speech API
- **Надёжно** - работает без интернета
- **Просто** - меньше компонентов

### **✅ Оптимизированная архитектура:**
- **gRPC только для LLM** - минимум сетевых вызовов
- **Локальные функции** - STT, управление
- **Edge TTS** - высокое качество, бесплатно
- **Быстрый отклик** - всё работает мгновенно
- **Экономия ресурсов** - меньше серверной нагрузки

---

## Система аналитики и мониторинга

### **🎯 Цель аналитики в MVP 1:**
Получить полное понимание работы системы, выявить проблемы и оптимизировать производительность для MVP 2.

### **🔍 Что отслеживаем:**

#### **1. Идентификация пользователей:**
```python
# Уникальный ID для каждого устройства
def generate_user_id():
    # Комбинация: MAC адрес + Serial Number + Volume UUID
    mac = get_mac_address()
    serial = get_system_serial()
    volume_uuid = get_volume_uuid()
    
    # Хешируем для анонимности
    combined = f"{mac}:{serial}:{volume_uuid}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]
```

#### **2. Ключевые метрики производительности:**
```python
# Время каждого этапа обработки
analytics.log_performance('screen_capture', duration_ms)
analytics.log_performance('image_processing', duration_ms)
analytics.log_performance('llm_analysis', duration_ms)
analytics.log_performance('tts_synthesis', duration_ms)
analytics.log_performance('total_response', duration_ms)
```

#### **3. События взаимодействия:**
```python
# Все действия пользователя
analytics.log_event('assistant_activated')
analytics.log_event('user_interrupted')
analytics.log_event('command_recognized', {'command': 'what_on_screen'})
analytics.log_event('error_occurred', {'error_type': 'network_timeout'})
```

#### **4. Качество работы:**
```python
# Статистика успешности
analytics.log_quality('stt_accuracy', accuracy_percentage)
analytics.log_quality('llm_response_quality', confidence_score)
analytics.log_quality('image_capture_success', success_rate)
```

### **📊 Отправка данных на сервер:**

#### **Схема данных:**
```json
{
  "user_id": "a1b2c3d4e5f6g7h8",
  "session_id": "session_123",
  "timestamp": "2024-01-15T10:30:00Z",
  "events": [
    {
      "event_type": "assistant_activated",
      "timestamp": "2024-01-15T10:30:05Z",
      "data": {}
    },
    {
      "event_type": "performance_metric",
      "timestamp": "2024-01-15T10:30:08Z",
      "data": {
        "operation": "total_response",
        "duration_ms": 2300
      }
    }
  ]
}
```

#### **Политика отправки:**
- **Буферизация** - отправляем каждые 50 событий или каждый час
- **Сжатие** - gzip для экономии трафика
- **Retry логика** - повторные попытки при ошибках
- **Fallback** - локальное хранение при недоступности сервера

### **🛡️ Безопасность и приватность:**

#### **Принципы:**
- **Анонимность** - никаких личных данных
- **Локальность** - скриншоты не покидают устройство
- **Шифрование** - HTTPS для передачи метрик
- **Контроль** - пользователь может отключить аналитику

#### **Что НЕ собираем:**
- ❌ Содержимое экранов
- ❌ Личные сообщения
- ❌ Имена файлов
- ❌ Контакты или пароли

#### **Что собираем:**
- ✅ Время работы функций
- ✅ Частота использования
- ✅ Типы ошибок
- ✅ Производительность системы

### **📈 Аналитика для MVP 2:**

#### **Ключевые инсайты:**
- **Где пользователи застревают** - медленные функции
- **Какие ошибки частые** - проблемы стабильности
- **Паттерны использования** - популярные команды
- **Производительность** - узкие места системы

#### **Автоматические уведомления:**
```python
# Уведомления о проблемах
if error_rate > 0.1:  # >10% ошибок
    send_alert('high_error_rate', {'rate': error_rate})

if avg_response_time > 5000:  # >5 секунд
    send_alert('slow_response_time', {'avg_time': avg_response_time})
```

---

## Заключение

**MVP 1 даёт нам:**

🚀 **Быстрый результат** - 3 недели до работающего продукта
🎯 **Простое управление** - один пробел для всего
✅ **Надёжную архитектуру** - gRPC + клиент-сервер
🔒 **Безопасность** - API ключи на сервере
🎤 **Локальное распознавание** - быстро, бесплатно, надёжно
🔊 **Edge TTS** - нейронные голоса Microsoft (бесплатно)
📊 **Полную аналитику** - понимание работы системы
📱 **Готовность к тестированию** - можно показывать пользователям

**Это идеальная основа для дальнейшего развития голосового ассистента для незрячих!** 🎉
