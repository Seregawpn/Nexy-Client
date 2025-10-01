# 🚀 РУКОВОДСТВО ПО ДЕПЛОЮ СЕРВЕРА НА AZURE

**Дата создания:** 1 октября 2025  
**Версия:** 1.0  
**Статус:** ✅ Активно используется

---

## 📋 **ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ**

### **🔐 GitHub Secrets (КРИТИЧНО):**
Должны быть настроены в `https://github.com/Seregawpn/Nexy_server/settings/secrets/actions`:
- `AZURE_CREDENTIALS` - Service Principal JSON
- `AZURE_SUBSCRIPTION_ID` - ID подписки Azure
- `AZURE_TENANT_ID` - ID тенанта Azure

### **📁 Структура файлов (ОБЯЗАТЕЛЬНО):**
```
nexy_new/server/          ← Исходный код
├── main.py              ← Основной файл сервера
├── modules/             ← Все модули (9 штук)
├── integrations/        ← Все интеграции
├── config/              ← Конфигурация
├── requirements.txt     ← Зависимости Python
├── .github/workflows/   ← GitHub Actions
└── Docs/                ← Документация
```

---

## 🔄 **ПОШАГОВАЯ ИНСТРУКЦИЯ ДЕПЛОЯ**

### **ШАГ 1: ПОДГОТОВКА (1-2 минуты)**

**1.1. Убедитесь, что изменения готовы:**
```bash
# Проверьте, что все изменения сохранены
cd /Users/sergiyzasorin/Library/Mobile\ Documents/com~apple~CloudDocs/Development/Nexy/server
git status
```

**1.2. Создайте временную директорию:**
```bash
cd /tmp
rm -rf nexy_server_temp  # Очистить, если существует
```

### **ШАГ 2: КЛОНИРОВАНИЕ РЕПОЗИТОРИЯ (30 секунд)**

```bash
# Клонируем серверный репозиторий
git clone https://github.com/Seregawpn/Nexy_server.git nexy_server_temp
cd nexy_server_temp
```

### **ШАГ 3: ОЧИСТКА И КОПИРОВАНИЕ (1 минута)**

```bash
# ОБЯЗАТЕЛЬНО: Очистить все старые файлы
rm -rf * .* 2>/dev/null || true

# ОБЯЗАТЕЛЬНО: Скопировать все файлы сервера
cp -r /Users/sergiyzasorin/Library/Mobile\ Documents/com~apple~CloudDocs/Development/Nexy/server/* .
cp -r /Users/sergiyzasorin/Library/Mobile\ Documents/com~apple~CloudDocs/Development/Nexy/server/.* . 2>/dev/null || true
```

### **ШАГ 4: НАСТРОЙКА GIT (30 секунд)**

```bash
# ОБЯЗАТЕЛЬНО: Инициализировать git
git init

# ОБЯЗАТЕЛЬНО: Добавить remote
git remote add origin https://github.com/Seregawpn/Nexy_server.git
```

### **ШАГ 5: COMMIT И PUSH (1 минута)**

```bash
# ОБЯЗАТЕЛЬНО: Добавить все файлы
git add .

# ОБЯЗАТЕЛЬНО: Commit с описательным сообщением
git commit -m "🚀 Обновление сервера: [ОПИСАНИЕ ИЗМЕНЕНИЙ]

- Дата: $(date '+%d.%m.%Y %H:%M')
- Изменения: [краткое описание]
- Модули: [список затронутых модулей]"

# ОБЯЗАТЕЛЬНО: Force push
git push origin main --force
```

### **ШАГ 6: ОЧИСТКА (10 секунд)**

```bash
# ОБЯЗАТЕЛЬНО: Очистить временную директорию
cd /tmp
rm -rf nexy_server_temp
```

---

## ⏱️ **АВТОМАТИЧЕСКИЙ ДЕПЛОЙ (2-3 минуты)**

После push в GitHub автоматически запускается:

### **🤖 GitHub Actions процесс:**
1. **Триггер:** Push в main ветку
2. **Аутентификация:** GitHub Secrets + Azure Service Principal
3. **Команда:** `az vm run-command invoke` → `/home/azureuser/update-server.sh`
4. **Обновление:** `git pull` + `pip install` + `systemctl restart`
5. **Проверка:** Health checks

### **📊 Мониторинг деплоя:**
- **GitHub Actions:** `https://github.com/Seregawpn/Nexy_server/actions`
- **Health check:** `http://20.151.51.172/health`
- **Status API:** `http://20.151.51.172/status`

---

## ✅ **ПРОВЕРКА УСПЕШНОГО ДЕПЛОЯ**

### **1. Health Check:**
```bash
curl http://20.151.51.172/health
# Ожидаемый результат: "OK"
```

### **2. Status API:**
```bash
curl http://20.151.51.172/status
# Ожидаемый результат: JSON с информацией о сервисе
```

### **3. Проверка на сервере:**
```bash
# Проверить, что изменения применились
az vm run-command invoke \
  --resource-group Nexy \
  --name nexy-regular \
  --command-id RunShellScript \
  --scripts "
    cd /home/azureuser/voice-assistant
    git log --oneline -1
  "
```

---

## ⚠️ **КРИТИЧЕСКИЕ МОМЕНТЫ**

### **🚨 НЕ ДЕЛАЙТЕ:**
- ❌ Не клонируйте в существующую директорию
- ❌ Не забывайте очищать старые файлы
- ❌ Не используйте обычный push (только --force)
- ❌ Не оставляйте временные директории

### **✅ ОБЯЗАТЕЛЬНО:**
- ✅ Всегда используйте `/tmp` для временных файлов
- ✅ Всегда очищайте старые файлы перед копированием
- ✅ Всегда используйте описательные commit сообщения
- ✅ Всегда проверяйте health endpoint после деплоя

---

## 🔧 **УСТРАНЕНИЕ ПРОБЛЕМ**

### **Проблема: GitHub Actions не запускается**
**Решение:**
1. Проверить GitHub Secrets в настройках репозитория
2. Убедиться, что workflow файл в `.github/workflows/`
3. Проверить триггеры в workflow

### **Проблема: Деплой не завершается**
**Решение:**
1. Проверить логи GitHub Actions
2. Запустить обновление вручную на сервере:
```bash
az vm run-command invoke \
  --resource-group Nexy \
  --name nexy-regular \
  --command-id RunShellScript \
  --scripts "/home/azureuser/update-server.sh"
```

### **Проблема: Health check не проходит**
**Решение:**
1. Проверить статус сервиса на сервере
2. Посмотреть логи сервиса
3. Перезапустить сервис вручную

---

## 📊 **ВРЕМЕННЫЕ РАМКИ**

| Этап | Время | Описание |
|------|-------|----------|
| Подготовка | 1-2 мин | Проверка изменений |
| Клонирование | 30 сек | Скачивание репозитория |
| Копирование | 1 мин | Синхронизация файлов |
| Git операции | 1 мин | Commit и push |
| Очистка | 10 сек | Удаление временных файлов |
| **Автоматический деплой** | **2-3 мин** | **GitHub Actions → Azure** |
| **ИТОГО** | **5-7 мин** | **Полный цикл** |

---

## 🎯 **ПРИМЕРЫ COMMIT СООБЩЕНИЙ**

### **✅ ХОРОШИЕ ПРИМЕРЫ:**
```bash
git commit -m "🚀 Обновление сервера: исправление text_processing

- Дата: 01.10.2025 16:45
- Изменения: исправлена обработка длинных текстов
- Модули: text_processing, integrations"

git commit -m "🚀 Обновление сервера: добавление нового провайдера

- Дата: 01.10.2025 17:20
- Изменения: добавлен Azure TTS провайдер
- Модули: audio_generation, providers"
```

### **❌ ПЛОХИЕ ПРИМЕРЫ:**
```bash
git commit -m "update"
git commit -m "fix"
git commit -m "changes"
```

---

## 🚀 **ГОТОВО К ИСПОЛЬЗОВАНИЮ**

**Следуйте этой инструкции для каждого обновления сервера.**

**При возникновении проблем - обращайтесь к разделу "Устранение проблем".**

---

**📞 Поддержка:** Документация в `Docs/` папке  
**🔗 Репозиторий:** `https://github.com/Seregawpn/Nexy_server`  
**🌐 Сервер:** `http://20.151.51.172`
