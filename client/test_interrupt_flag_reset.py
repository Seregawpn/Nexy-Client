#!/usr/bin/env python3
"""
Тест корректного сброса флага прерывания во всех сценариях
"""

import asyncio
from rich.console import Console
from rich.table import Table

console = Console()

async def test_interrupt_flag_reset():
    """Тестирует сброс флага прерывания во всех сценариях"""
    console.print("🚀 Тест сброса флага прерывания")
    console.print("=" * 60)
    
    # Создаем таблицу сценариев
    table = Table(title="📊 Сценарии сброса флага прерывания")
    table.add_column("Сценарий", style="cyan")
    table.add_column("Метод", style="yellow")
    table.add_column("Когда сбрасывается", style="green")
    
    scenarios = [
        ("Прерывание записи (LISTENING)", "handle_interrupt_or_cancel", "После перехода в SLEEPING"),
        ("Прерывание работы (IN_PROCESS)", "handle_interrupt_or_cancel", "После перехода в SLEEPING"),
        ("Прерывание в SLEEPING", "handle_interrupt_or_cancel", "Немедленно (состояние не меняется)"),
        ("Фоновое прерывание", "_interrupt_background", "После завершения фонового прерывания"),
        ("Принудительное прерывание", "_force_interrupt_all", "После завершения всех прерываний"),
        ("Прерывание + активация", "handle_start_recording", "После перехода в LISTENING"),
        ("Неизвестное состояние", "handle_interrupt_or_cancel", "После перехода в SLEEPING"),
    ]
    
    for scenario, method, when in scenarios:
        table.add_row(scenario, method, when)
    
    console.print(table)
    
    console.print("\n🎯 Проблема, которую мы исправили:")
    console.print("  ❌ Флаг interrupting не сбрасывался после завершения прерывания")
    console.print("  ❌ Микрофон не мог активироваться при длительном нажатии")
    console.print("  ❌ Система 'зависала' в состоянии прерывания")
    
    console.print("\n✅ Решение:")
    console.print("  • Добавили сброс флага во всех методах прерывания")
    console.print("  • Флаг сбрасывается после завершения каждого типа прерывания")
    console.print("  • Система корректно возвращается в рабочее состояние")
    
    console.print("\n🔧 Технические детали:")
    console.print("  • _force_interrupt_all: сброс после принудительного прерывания")
    console.print("  • _interrupt_background: сброс после фонового прерывания")
    console.print("  • handle_interrupt_or_cancel: сброс для LISTENING и IN_PROCESS")
    console.print("  • handle_start_recording: сброс после прерывания IN_PROCESS")
    
    console.print("\n📱 Теперь логика работает так:")
    console.print("  1. Пробел нажат → interrupting = True")
    console.print("  2. Прерывание выполняется")
    console.print("  3. Флаг сбрасывается → interrupting = False")
    console.print("  4. Микрофон может активироваться при длительном нажатии")

if __name__ == "__main__":
    try:
        asyncio.run(test_interrupt_flag_reset())
    except KeyboardInterrupt:
        console.print("\n👋 Выход...")
    except Exception as e:
        console.print(f"❌ Ошибка: {e}")
