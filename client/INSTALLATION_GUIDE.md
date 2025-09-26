# 🚀 РУКОВОДСТВО ПО УСТАНОВКЕ NEXY AI ASSISTANT

## 📍 Где устанавливается приложение

**Приложение Nexy устанавливается в:**
```
~/Applications/Nexy.app
```

## 🔧 Способы установки

### 1. Автоматическая установка (Рекомендуется)
```bash
cd /Users/sergiyzasorin/Desktop/Development/Nexy/client
./install_nexy.sh
```

### 2. Установка через PKG
```bash
open dist/Nexy-signed.pkg
```

### 3. Ручная установка
```bash
# Создаем папку Applications если её нет
mkdir -p ~/Applications

# Копируем приложение
cp -R /tmp/NexyCleanFinal.app ~/Applications/Nexy.app

# Запускаем
open ~/Applications/Nexy.app
```

## ✅ Проверка установки

### Проверить, что приложение установлено:
```bash
ls -la ~/Applications/Nexy.app
```

### Проверить, что приложение запущено:
```bash
ps aux | grep -i nexy | grep -v grep
```

### Проверить подпись:
```bash
codesign --verify --deep --strict ~/Applications/Nexy.app
```

## 🎯 Ожидаемое поведение

После установки в меню-баре должен появиться значок Nexy:

- **SLEEPING режим** (серый кружок) - по умолчанию
- **LISTENING режим** (синий пульсирующий) - при долгом нажатии пробела
- **PROCESSING режим** (желтый вращающийся) - при обработке команды

## 🔄 Обновление приложения

Для обновления приложения:

1. Остановите текущее приложение:
   ```bash
   pkill -f Nexy
   ```

2. Запустите установку заново:
   ```bash
   ./install_nexy.sh
   ```

## 🚨 Устранение проблем

### Если приложение не запускается:
```bash
# Проверьте подпись
codesign --verify --deep --strict ~/Applications/Nexy.app

# Проверьте разрешения
ls -la ~/Applications/Nexy.app
```

### Если PKG не устанавливается:
```bash
# Удалите старый пакет
sudo pkgutil --forget com.nexy.assistant.pkg

# Установите заново
open dist/Nexy-signed.pkg
```

## 📋 Технические детали

- **Bundle ID:** com.nexy.assistant
- **Версия:** 1.0.0
- **Архитектура:** arm64 (Apple Silicon)
- **Требования:** macOS 11.0+ (Big Sur и новее)
- **Размер:** ~103MB

## 🎉 Готово!

Приложение готово к использованию! 🚀
