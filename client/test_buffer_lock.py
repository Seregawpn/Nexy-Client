#!/usr/bin/env python3
"""
Тест временной блокировки буфера AudioPlayer
Проверяет, что после прерывания новые чанки не добавляются в течение заданного времени
"""

import time
import numpy as np
from audio_player import AudioPlayer

def test_buffer_lock():
    """Тестирует временную блокировку буфера после прерывания."""
    print("🧪 Тест временной блокировки буфера AudioPlayer")
    print("=" * 60)
    
    # Создаем AudioPlayer
    audio_player = AudioPlayer()
    print("✅ AudioPlayer создан")
    
    # Создаем тестовый аудио чанк
    test_chunk = np.random.randint(-32768, 32767, 1000, dtype=np.int16)
    print(f"✅ Тестовый чанк создан: {len(test_chunk)} сэмплов")
    
    # Проверяем начальное состояние
    print(f"📊 Начальное состояние: queue={audio_player.audio_queue.qsize()}, buffer_locked={audio_player.is_buffer_locked()}")
    
    # Добавляем первый чанк (должен добавиться)
    print("\n🔍 Тест 1: Добавление чанка ДО прерывания")
    audio_player.add_chunk(test_chunk)
    print(f"📊 После добавления: queue={audio_player.audio_queue.qsize()}")
    
    # Симулируем прерывание
    print("\n🔍 Тест 2: Симуляция прерывания")
    start_time = time.time()
    audio_player.clear_all_audio_data()
    clear_time = (time.time() - start_time) * 1000
    print(f"⏱️ Время очистки: {clear_time:.1f}ms")
    print(f"📊 После очистки: queue={audio_player.audio_queue.qsize()}")
    print(f"🔒 Буфер заблокирован: {audio_player.is_buffer_locked()}")
    
    # Пытаемся добавить чанк сразу после прерывания
    print("\n🔍 Тест 3: Попытка добавления чанка сразу после прерывания")
    audio_player.add_chunk(test_chunk)
    print(f"📊 После попытки добавления: queue={audio_player.audio_queue.qsize()}")
    
    # Ждем немного и проверяем состояние блокировки
    print("\n🔍 Тест 4: Проверка состояния блокировки через 0.1 секунды")
    time.sleep(0.1)
    print(f"🔒 Буфер заблокирован: {audio_player.is_buffer_locked()}")
    
    # Пытаемся добавить чанк через 0.1 секунды
    print("\n🔍 Тест 5: Попытка добавления чанка через 0.1 секунды")
    audio_player.add_chunk(test_chunk)
    print(f"📊 После попытки добавления: queue={audio_player.audio_queue.qsize()}")
    
    # Ждем окончания блокировки
    print("\n🔍 Тест 6: Ожидание окончания блокировки")
    while audio_player.is_buffer_locked():
        time.sleep(0.01)
        print(f"⏳ Ожидание... {audio_player.buffer_lock_until - time.time():.2f}s осталось")
    
    print("✅ Блокировка снята!")
    
    # Пытаемся добавить чанк после снятия блокировки
    print("\n🔍 Тест 7: Добавление чанка после снятия блокировки")
    audio_player.add_chunk(test_chunk)
    print(f"📊 После добавления: queue={audio_player.audio_queue.qsize()}")
    
    # Финальная проверка
    print("\n🔍 Финальная проверка:")
    print(f"📊 Очередь: {audio_player.audio_queue.qsize()}")
    print(f"🔒 Буфер заблокирован: {audio_player.is_buffer_locked()}")
    
    if audio_player.audio_queue.qsize() == 1:
        print("✅ ТЕСТ ПРОЙДЕН: Временная блокировка работает корректно!")
    else:
        print("❌ ТЕСТ ПРОВАЛЕН: Временная блокировка не работает!")
    
    print("=" * 60)

if __name__ == "__main__":
    test_buffer_lock()
