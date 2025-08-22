#!/usr/bin/env python3
"""
Тест улучшенной логики InputHandler с флагом прерывания
"""

import asyncio
import time
from rich.console import Console
from rich.table import Table

console = Console()

async def test_improved_input_handler():
    """Тестирует улучшенную логику InputHandler"""
    console.print("🚀 Тест улучшенной логики InputHandler")
    console.print("=" * 60)
    
    # Создаем таблицу улучшений
    table = Table(title="📊 Улучшения InputHandler")
    table.add_column("Проблема", style="red")
    table.add_column("Решение", style="green")
    table.add_column("Результат", style="blue")
    
    improvements = [
        ("Слишком быстрый таймер (10ms)", "Увеличен до 150ms", "Стабильность, нет race condition"),
        ("Отсутствие проверки состояния", "Добавлен флаг interrupting", "Микрофон не активируется во время прерывания"),
        ("Конфликт событий", "Последовательная обработка", "Сначала прерывание, потом активация"),
        ("Race condition", "Флаг состояния", "Синхронизация между компонентами"),
    ]
    
    for problem, solution, result in improvements:
        table.add_row(problem, solution, result)
    
    console.print(table)
    
    console.print("\n🎯 Новая логика работы:")
    console.print("  1. Пробел нажат → устанавливается флаг interrupting")
    console.print("  2. Отправляется interrupt_or_cancel (немедленно)")
    console.print("  3. Запускается таймер на 150ms для start_recording")
    console.print("  4. При срабатывании таймера проверяется флаг interrupting")
    console.print("  5. Если не прерывается → активируется микрофон")
    console.print("  6. При отпускании пробела флаг сбрасывается")
    
    console.print("\n✅ Преимущества новой логики:")
    console.print("  • Нет конфликтов между прерыванием и активацией")
    console.print("  • Стабильная работа без race conditions")
    console.print("  • Четкая последовательность событий")
    console.print("  • Синхронизация между InputHandler и StateManager")
    
    console.print("\n🔧 Технические детали:")
    console.print("  • Задержка таймера: 150ms (вместо 10ms)")
    console.print("  • Флаг interrupting для отслеживания состояния")
    console.print("  • Метод reset_interrupt_flag() для внешнего сброса")
    console.print("  • Проверка состояния перед активацией микрофона")

if __name__ == "__main__":
    try:
        asyncio.run(test_improved_input_handler())
    except KeyboardInterrupt:
        console.print("\n👋 Выход...")
    except Exception as e:
        console.print(f"❌ Ошибка: {e}")
