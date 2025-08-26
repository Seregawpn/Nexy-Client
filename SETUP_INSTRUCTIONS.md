# 🚀 Инструкция по установке и настройке

## 📋 Предварительные требования

- Python 3.8+
- pip (менеджер пакетов Python)
- Git

## 🔧 Установка зависимостей

### 1. **Активация виртуального окружения**
```bash
# Если у вас уже есть .venv
source .venv/bin/activate  # macOS/Linux
# или
.venv\Scripts\activate     # Windows
```

### 2. **Установка зависимостей сервера**
```bash
cd server
pip install -r requirements.txt
```

### 3. **Установка зависимостей клиента**
```bash
cd client
pip install -r requirements.txt
```

## 🚨 Решение проблем

### **Ошибка: "No module named 'pydub'"**
```bash
pip install pydub
```

### **Ошибка: "No module named 'grpcio'"**
```bash
pip install grpcio grpcio-tools
```

### **Ошибка: "No module named 'langchain'"**
```bash
pip install langchain langchain-google-genai
```

## 🔑 Настройка API ключей

### 1. **Создайте файл конфигурации**
```bash
cd server
cp config.env.example config.env
```

### 2. **Отредактируйте config.env**
```env
GEMINI_API_KEY=ваш_ключ_google_gemini
```

## 🧪 Проверка установки

### 1. **Проверка protobuf файлов**
```bash
python generate_proto.py
```

### 2. **Проверка импортов сервера**
```bash
cd server
python -c "import streaming_pb2, streaming_pb2_grpc; print('✅ OK')"
```

### 3. **Проверка импортов клиента**
```bash
cd client
python -c "import streaming_pb2, streaming_pb2_grpc; print('✅ OK')"
```

## 🚀 Запуск

### 1. **Запуск сервера**
```bash
cd server
python main.py
```

### 2. **Запуск клиента**
```bash
cd client
python main.py
```

## 📝 Важные замечания

1. **Protobuf файлы** (`*_pb2.py`, `*_pb2_grpc.py`) **НЕ удалять** - они нужны для gRPC
2. **API ключи** должны быть в `server/config.env`
3. **Виртуальное окружение** должно быть активировано
4. **Все зависимости** должны быть установлены

## 🔍 Поиск проблем

Если что-то не работает:

1. Проверьте, что виртуальное окружение активировано
2. Убедитесь, что все зависимости установлены
3. Проверьте наличие API ключей
4. Запустите `python generate_proto.py` для восстановления protobuf файлов

---
*Создано: $(date)*


