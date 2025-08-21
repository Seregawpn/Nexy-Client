#!/usr/bin/env python3
"""
Тест реального gRPC стрима для диагностики проблемы прерывания
"""

import asyncio
import time
import numpy as np
import sys
import os

# Добавляем путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from audio_player import AudioPlayer
from grpc_client import GrpcClient
from utils.hardware_id import get_hardware_id

async def test_real_grpc_interruption():
    """Тестируем прерывание реального gRPC стрима"""
    
    print("🌐 ТЕСТ РЕАЛЬНОГО GPRC СТРИМА")
    print("=" * 60)
    
    # 1. Проверка сервера
    print("\n1️⃣ ПРОВЕРКА СЕРВЕРА:")
    print("   🔍 Убедитесь, что сервер запущен: python grpc_server.py")
    print("   🔍 Сервер должен быть доступен на localhost:50051")
    
    # 2. Инициализация компонентов
    print("\n2️⃣ ИНИЦИАЛИЗАЦИЯ КОМПОНЕНТОВ:")
    audio_player = AudioPlayer()
    grpc_client = GrpcClient()
    print("   ✅ AudioPlayer создан")
    print("   ✅ GrpcClient создан")
    
    # 3. Подключение к серверу
    print("\n3️⃣ ПОДКЛЮЧЕНИЕ К СЕРВЕРУ:")
    try:
        await grpc_client.connect()
        print("   ✅ Подключение к серверу установлено")
    except Exception as e:
        print(f"   ❌ Ошибка подключения: {e}")
        print("   🔧 Запустите сервер: cd ../server && python grpc_server.py")
        return
    
    # 4. Создание тестового запроса
    print("\n4️⃣ СОЗДАНИЕ ТЕСТОВОГО ЗАПРОСА:")
    test_command = "Скажи короткую фразу для тестирования прерывания"
    print(f"   📝 Команда: {test_command}")
    
    # 5. Запуск gRPC стрима
    print("\n5️⃣ 🚀 ЗАПУСК GPRC СТРИМА:")
    print("   🔇 Ассистент начнет говорить...")
    print("   🔇 НАЖМИТЕ ПРОБЕЛ для прерывания!")
    
    # Получаем Hardware ID
    hardware_id = get_hardware_id()
    print(f"   🆔 Hardware ID: {hardware_id[:20]}...")
    
    # Устанавливаем hardware_id в GrpcClient
    grpc_client.hardware_id = hardware_id
    
    # Создаем задачу для gRPC стрима
    # stream_audio не принимает audio_player - использует внутренний
    streaming_task = asyncio.create_task(
        grpc_client.stream_audio(test_command, hardware_id=hardware_id).__anext__()
    )
    
    # Ждем немного для начала стрима
    await asyncio.sleep(2.0)
    
    # 6. ПРЕРЫВАНИЕ
    print("\n6️⃣ 🚨 ПРЕРЫВАНИЕ GPRC СТРИМА:")
    print("   🔇 Вызываю прерывание...")
    
    interrupt_start = time.time()
    
    # Прерываем аудио
    audio_player.clear_all_audio_data()
    
    # Отменяем gRPC задачу
    streaming_task.cancel()
    
    # Отправляем команду прерывания на сервер
    grpc_client.force_interrupt_server()
    
    interrupt_time = (time.time() - interrupt_start) * 1000
    print(f"   ⏱️ Время прерывания: {interrupt_time:.1f}ms")
    
    # 7. Проверка состояния
    print("\n7️⃣ ПРОВЕРКА СОСТОЯНИЯ ПОСЛЕ ПРЕРЫВАНИЯ:")
    
    # Проверяем размер очереди
    queue_size = audio_player.audio_queue.qsize()
    print(f"   📊 Размер очереди: {queue_size}")
    
    # Проверяем флаг прерывания
    interrupt_flag = audio_player.interrupt_flag.is_set()
    print(f"   🚨 Флаг прерывания: {interrupt_flag}")
    
    # Проверяем активный поток
    stream_active = audio_player.stream is not None
    print(f"   🔌 Активный поток: {stream_active}")
    
    # 8. Дополнительное ожидание
    print("\n8️⃣ ДОПОЛНИТЕЛЬНОЕ ОЖИДАНИЕ:")
    print("   ⏰ Ждем 3 секунды для проверки...")
    await asyncio.sleep(3.0)
    
    # 9. Финальная проверка
    print("\n9️⃣ ФИНАЛЬНАЯ ПРОВЕРКА:")
    
    # Проверяем, не пришли ли новые аудио чанки
    final_queue_size = audio_player.audio_queue.qsize()
    print(f"   📊 Финальный размер очереди: {final_queue_size}")
    
    # Проверяем, не продолжает ли ассистент говорить
    if final_queue_size > 0:
        print("   ❌ АССИСТЕНТ ПРОДОЛЖАЕТ ГОВОРИТЬ!")
        print("   🔍 Проблема: новые аудио чанки продолжают поступать")
    else:
        print("   ✅ АССИСТЕНТ ЗАМОЛЧАЛ!")
        print("   ✅ Прерывание работает корректно")
    
    # 10. Завершение
    print("\n🔟 ЗАВЕРШЕНИЕ:")
    print("   🧹 Очистка ресурсов...")
    
    try:
        await grpc_client.disconnect()
        print("   ✅ gRPC соединение закрыто")
    except:
        pass
    
    audio_player.force_stop_immediately()
    print("   ✅ AudioPlayer остановлен")
    
    print("\n" + "=" * 60)
    print("🎯 ТЕСТ РЕАЛЬНОГО GPRC СТРИМА ЗАВЕРШЕН!")
    
    # Анализ результатов
    if interrupt_time < 100:  # Меньше 100ms
        print("✅ ПРЕРЫВАНИЕ РАБОТАЕТ БЫСТРО!")
    else:
        print("⚠️ ПРЕРЫВАНИЕ МЕДЛЕННОЕ!")
        
    if final_queue_size == 0:
        print("✅ АССИСТЕНТ ПОЛНОСТЬЮ ЗАМОЛЧАЛ!")
    else:
        print("❌ АССИСТЕНТ ПРОДОЛЖАЕТ ГОВОРИТЬ!")
        print("🔍 ПРОБЛЕМА: gRPC стрим не прерывается на сервере!")

async def test_interrupt_during_playback():
    """Тестируем прерывание во время воспроизведения"""
    
    print("\n🎵 ТЕСТ ПРЕРЫВАНИЯ ВО ВРЕМЯ ВОСПРОИЗВЕДЕНИЯ:")
    print("=" * 60)
    
    # 1. Создание AudioPlayer
    audio_player = AudioPlayer()
    
    # 2. Создание тестового аудио
    sample_rate = 44100
    duration = 5  # 5 секунд
    test_audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, sample_rate * duration))
    test_audio = (test_audio * 0.3).astype(np.float32)
    
    # 3. Добавление аудио
    chunk_size = 44100  # 1 секунда
    for i in range(0, len(test_audio), chunk_size):
        chunk = test_audio[i:i+chunk_size]
        audio_player.add_chunk(chunk)
    
    print(f"   📦 Добавлено {len(test_audio)//chunk_size} чанков")
    print(f"   📊 Размер очереди: {audio_player.audio_queue.qsize()}")
    
    # 4. Ждем начала воспроизведения
    print("   ⏰ Ждем начала воспроизведения...")
    await asyncio.sleep(1.0)
    
    # 5. Прерывание
    print("   🚨 ПРЕРЫВАНИЕ ВО ВРЕМЯ ВОСПРОИЗВЕДЕНИЯ!")
    interrupt_start = time.time()
    
    audio_player.clear_all_audio_data()
    
    interrupt_time = (time.time() - interrupt_start) * 1000
    print(f"   ⏱️ Время прерывания: {interrupt_time:.1f}ms")
    
    # 6. Проверка
    await asyncio.sleep(2.0)
    final_queue_size = audio_player.audio_queue.qsize()
    
    print(f"   📊 Финальный размер очереди: {final_queue_size}")
    
    if final_queue_size == 0:
        print("   ✅ ПРЕРЫВАНИЕ ВО ВРЕМЯ ВОСПРОИЗВЕДЕНИЯ РАБОТАЕТ!")
    else:
        print("   ❌ ПРЕРЫВАНИЕ ВО ВРЕМЯ ВОСПРОИЗВЕДЕНИЯ НЕ РАБОТАЕТ!")
    
    # Очистка
    audio_player.force_stop_immediately()

if __name__ == "__main__":
    print("🚀 Запуск теста реального gRPC стрима...")
    
    # Сначала тестируем изолированное прерывание
    asyncio.run(test_interrupt_during_playback())
    
    print("\n" + "=" * 60)
    print("🌐 ПЕРЕХОД К ТЕСТУ GPRC СТРИМА...")
    print("🔧 УБЕДИТЕСЬ, ЧТО СЕРВЕР ЗАПУЩЕН!")
    print("=" * 60)
    
    # Затем тестируем gRPC стрим
    asyncio.run(test_real_grpc_interruption())
