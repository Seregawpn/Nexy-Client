#!/usr/bin/env python3
"""
🚀 БЫСТРЫЙ ТЕСТ ПРЕРЫВАНИЯ РЕЧИ
Запускает ассистента для тестирования прерывания
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь для импорта
sys.path.append(str(Path(__file__).parent.parent))

async def quick_interrupt_test():
    """Быстрый тест прерывания речи"""
    print("🚀 БЫСТРЫЙ ТЕСТ ПРЕРЫВАНИЯ РЕЧИ")
    print("=" * 50)
    
    print("📋 Инструкции:")
    print("1. Убедитесь, что сервер запущен в ОТДЕЛЬНОМ терминале:")
    print("   cd server && python grpc_server.py")
    print("")
    print("2. Этот скрипт запустит ассистента для тестирования")
    print("")
    print("3. Тест прерывания:")
    print("   • Скажите длинную команду")
    print("   • Дождитесь начала речи")
    print("   • НАЖМИТЕ ПРОБЕЛ для прерывания")
    print("   • Проверьте мгновенную остановку")
    print("")
    print("4. Критерии успеха:")
    print("   ✅ Время обработки прерывания < 50ms")
    print("   ✅ Речь остановилась МГНОВЕННО")
    print("   ✅ Состояние стало IDLE")
    print("   ✅ Буферы очищены")
    print("")
    
    # Проверяем доступность компонентов
    try:
        from main import main as run_assistant
        print("✅ Все компоненты доступны")
        print("🚀 Запускаю ассистента для тестирования...")
        print("")
        print("💡 НАЖМИТЕ ПРОБЕЛ ВО ВРЕМЯ РЕЧИ ДЛЯ ТЕСТИРОВАНИЯ!")
        print("")
        
        # Запускаем ассистента
        await run_assistant()
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Убедитесь, что вы находитесь в папке client")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(quick_interrupt_test())
    except KeyboardInterrupt:
        print("\n👋 Тест прерван пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        print("💡 Проверьте логи для диагностики")
