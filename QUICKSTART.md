# 🚀 Быстрый старт

## Установка и запуск за 5 минут

### 1. Подготовка окружения
```bash
# Создаем виртуальное окружение
python -m venv venv

# Активируем (Linux/Mac)
source venv/bin/activate

# Активируем (Windows)
venv\Scripts\activate
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка API ключа
```bash
# Копируем пример конфигурации
cp env_example.txt .env

# Редактируем файл .env
# Заменяем your_google_api_key_here на реальный ключ
```

**Получить API ключ:** https://makersuite.google.com/app/apikey

### 4. Тестирование системы
```bash
# Запускаем тесты
python test_system.py

# Запускаем демонстрацию
python demo.py
```

### 5. Первый запуск
```bash
# Простой промпт
python main.py --prompt "Расскажи короткую историю"

# С выбором голоса
python main.py --prompt "Hello world" --voice en

# Интерактивный режим
python main.py --interactive
```

## 🎯 Примеры использования

### Создание аудиокниги
```bash
python main.py --prompt "Напиши сказку о приключениях" --voice ru --rate "-10%"
```

### Генерация подкаста
```bash
python main.py --prompt "Создай подкаст о технологиях" --voice en-male --volume "+15%"
```

### Интерактивная сессия
```bash
python main.py --interactive
> prompt: Расскажи анекдот
> status
> voices
> quit
```

## 🔧 Устранение проблем

### Ошибка API ключа
```
ValueError: GOOGLE_API_KEY не установлен
```
**Решение:** Проверьте файл `.env` и правильность API ключа

### Проблемы с голосами
```
Голос недоступен, используем fallback
```
**Решение:** Система автоматически переключится на доступный голос

### Ошибки воспроизведения
```
Ошибка воспроизведения: No such file or directory
```
**Решение:** Проверьте права доступа к временной директории

## 📁 Структура файлов

- `main.py` - основное приложение
- `test_system.py` - тестирование компонентов
- `demo.py` - демонстрация работы
- `config.py` - конфигурация
- `text_processor.py` - обработка текста
- `audio_generator.py` - генерация аудио
- `audio_player.py` - воспроизведение
- `requirements.txt` - зависимости
- `.env` - API ключи (создать из env_example.txt)

## 🎵 Доступные голоса

- `ru` - русский женский
- `en` - английский женский  
- `ru-male` - русский мужской
- `en-male` - английский мужской

## ⚡ Параметры аудио

- `--rate` - скорость речи (+20%, -10%)
- `--volume` - громкость (+15%, -5%)
- `--voice` - выбор голоса

## 🆘 Поддержка

При проблемах:
1. Запустите `python test_system.py`
2. Проверьте логи в `streaming_system.log`
3. Убедитесь в правильности API ключа
4. Проверьте доступность интернета

**Готово! Система работает! 🎉**
