#!/usr/bin/env python3
"""
Интерактивный тест Audio Device Manager в реальном времени
Мгновенное обнаружение подключения/отключения наушников
"""

import asyncio
import time
import signal
import sys
from typing import Optional, List
from datetime import datetime

# Импортируем модуль
try:
    from audio_device_manager import (
        AudioDeviceManager, 
        AudioDevice, 
        DeviceType, 
        DeviceStatus,
        DeviceChange,
        DevicePriority
    )
    print("✅ Модуль audio_device_manager импортирован успешно")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

class LiveInteractiveTester:
    def __init__(self):
        self.manager: Optional[AudioDeviceManager] = None
        self.running = False
        self.device_changes = []
        self.last_devices: List[AudioDevice] = []
        self.start_time = None
        
    async def setup_manager(self):
        """Настройка менеджера устройств"""
        print("�� Настройка AudioDeviceManager...")
        
        try:
            # Создаем менеджер с настройками для быстрого мониторинга
            config = {
                'auto_switch_enabled': True,
                'monitoring_interval': 0.5,  # Проверяем каждые 500мс для мгновенности
                'device_priorities': {
                    'bluetooth_headphones': 1,
                    'wired_headphones': 2,
                    'external_speakers': 3,
                    'builtin_speakers': 4
                }
            }
            
            self.manager = AudioDeviceManager(config)
            
            # Регистрируем колбэки
            self.manager.set_device_changed_callback(self.on_device_changed)
            self.manager.set_device_switched_callback(self.on_device_switched)
            
            print("✅ AudioDeviceManager настроен")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка настройки: {e}")
            return False
    
    def on_device_changed(self, change: DeviceChange):
        """Обработчик изменения устройств - мгновенный отклик"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Миллисекунды
        event_type = "ПОДКЛЮЧЕНО" if change.is_connected else "ОТКЛЮЧЕНО"
        
        # Определяем тип устройства
        device_type_icon = "🎧" if change.device.channels == 2 else "🔊"
        if change.device.type.value == "input":
            device_type_icon = "🎤"
        
        print(f"\n{'='*60}")
        print(f"🔔 [{timestamp}] УСТРОЙСТВО {event_type}!")
        print(f"{device_type_icon} {change.device.name}")
        print(f"   Тип: {change.device.type.value}")
        print(f"   Каналы: {change.device.channels} ({'наушники' if change.device.channels == 2 else 'встроенные'})")
        print(f"   Приоритет: {change.device.priority.value}")
        print(f"   Статус: {change.device.status.value}")
        print(f"{'='*60}")
        
        # Сохраняем событие
        self.device_changes.append({
            'timestamp': timestamp,
            'device_name': change.device.name,
            'event_type': event_type,
            'device_type': change.device.type.value,
            'channels': change.device.channels,
            'is_connected': change.is_connected
        })
        
        # Специальные уведомления для наушников
        if change.device.channels == 2 and change.device.type.value == "output":
            if change.is_connected:
                print("🎧 НАУШНИКИ ПОДКЛЮЧЕНЫ! Система переключится автоматически.")
            else:
                print("🎧 НАУШНИКИ ОТКЛЮЧЕНЫ! Переключение на встроенные динамики.")
    
    def on_device_switched(self, from_device: AudioDevice, to_device: AudioDevice):
        """Обработчик переключения устройств"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        print(f"\n🔄 [{timestamp}] АВТОМАТИЧЕСКОЕ ПЕРЕКЛЮЧЕНИЕ:")
        print(f"   С: {from_device.name if from_device else 'Неизвестно'}")
        print(f"   На: {to_device.name}")
        print(f"   Каналы: {to_device.channels} ({'наушники' if to_device.channels == 2 else 'встроенные'})")
        print(f"   Приоритет: {to_device.priority.value}")
        
        self.device_changes.append({
            'timestamp': timestamp,
            'action': 'device_switched',
            'from_device': from_device.name if from_device else 'Unknown',
            'to_device': to_device.name,
            'channels': to_device.channels
        })
    
    async def start_monitoring(self):
        """Запуск мониторинга"""
        print("🚀 Запуск мгновенного мониторинга...")
        
        try:
            # Запускаем мониторинг
            await self.manager.start()
            self.running = True
            self.start_time = time.time()
            
            print("✅ Мгновенный мониторинг запущен")
            print("\n" + "="*70)
            print("🎧 ИНТЕРАКТИВНЫЙ ТЕСТ НАУШНИКОВ В РЕАЛЬНОМ ВРЕМЕНИ")
            print("="*70)
            print("�� ИНСТРУКЦИИ:")
            print("   1. 🎧 Подключите наушники (Bluetooth или проводные)")
            print("   2. 🎧 Отключите наушники")
            print("   3. 🎧 Подключите снова")
            print("   4. 🔄 Попробуйте разные устройства")
            print("   5. ⏹️  Нажмите Ctrl+C для остановки")
            print("="*70)
            print("⚡ СИСТЕМА БУДЕТ МГНОВЕННО ОБНАРУЖИВАТЬ ИЗМЕНЕНИЯ!")
            print("="*70)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска мониторинга: {e}")
            return False
    
    async def show_current_devices(self):
        """Показать текущие устройства"""
        try:
            devices = await self.manager.get_available_devices()
            self.last_devices = devices
            
            print(f"\n📱 ТЕКУЩИЕ УСТРОЙСТВА ({len(devices)}):")
            print("-" * 50)
            
            for i, device in enumerate(devices, 1):
                status_icon = "🟢" if device.is_available else "🔴"
                default_icon = "⭐" if device.is_default else "  "
                channels_icon = "🎧" if device.channels == 2 else "🔊"
                if device.type.value == "input":
                    channels_icon = "🎤"
                
                print(f"   {i}. {status_icon} {default_icon} {channels_icon} {device.name}")
                print(f"      Тип: {device.type.value} | Каналы: {device.channels} | Приоритет: {device.priority.value}")
            
        except Exception as e:
            print(f"❌ Ошибка получения устройств: {e}")
    
    async def show_live_stats(self):
        """Показать статистику в реальном времени"""
        try:
            metrics = self.manager.get_metrics()
            runtime = time.time() - self.start_time if self.start_time else 0
            
            print(f"\n📊 СТАТИСТИКА В РЕАЛЬНОМ ВРЕМЕНИ:")
            print(f"   ⏱️  Время работы: {runtime:.1f}с")
            print(f"   📱 Всего устройств: {metrics.total_devices}")
            print(f"   🟢 Доступных: {metrics.available_devices}")
            print(f"   🔄 Переключений: {metrics.total_switches}")
            print(f"   📝 Событий: {len(self.device_changes)}")
            
        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
    
    async def show_events_summary(self):
        """Показать сводку событий"""
        if not self.device_changes:
            print("\n📝 События не обнаружены")
            return
        
        print(f"\n📝 СВОДКА СОБЫТИЙ ({len(self.device_changes)}):")
        print("-" * 60)
        
        for event in self.device_changes[-10:]:  # Последние 10 событий
            if 'action' in event and event['action'] == 'device_switched':
                print(f"   [{event['timestamp']}] 🔄 ПЕРЕКЛЮЧЕНИЕ: {event['from_device']} → {event['to_device']}")
            else:
                event_icon = "🎧" if event.get('channels', 1) == 2 else "🔊"
                print(f"   [{event['timestamp']}] {event_icon} {event['event_type']}: {event['device_name']}")
        
        # Статистика по наушникам
        headphone_events = [e for e in self.device_changes if e.get('channels') == 2]
        if headphone_events:
            print(f"\n🎧 СОБЫТИЯ НАУШНИКОВ ({len(headphone_events)}):")
            for event in headphone_events:
                event_icon = "🎧" if event['event_type'] == "ПОДКЛЮЧЕНО" else "❌"
                print(f"   [{event['timestamp']}] {event_icon} {event['event_type']}: {event['device_name']}")
    
    async def stop_monitoring(self):
        """Остановка мониторинга"""
        if self.manager and self.running:
            print("\n🛑 Остановка мониторинга...")
            try:
                await self.manager.stop()
                self.running = False
                print("✅ Мониторинг остановлен")
            except Exception as e:
                print(f"❌ Ошибка остановки: {e}")
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов"""
        print(f"\n\n🛑 Получен сигнал {signum}, остановка...")
        asyncio.create_task(self.stop_monitoring())
        sys.exit(0)

async def main():
    """Основная функция"""
    print("🧪 ИНТЕРАКТИВНЫЙ ТЕСТ AUDIO DEVICE MANAGER")
    print("⚡ МГНОВЕННОЕ ОБНАРУЖЕНИЕ ИЗМЕНЕНИЙ")
    print("=" * 50)
    
    tester = LiveInteractiveTester()
    
    # Настройка обработчика сигналов
    signal.signal(signal.SIGINT, tester.signal_handler)
    signal.signal(signal.SIGTERM, tester.signal_handler)
    
    try:
        # Настройка менеджера
        if not await tester.setup_manager():
            return
        
        # Показать текущие устройства
        await tester.show_current_devices()
        
        # Запуск мониторинга
        if not await tester.start_monitoring():
            return
        
        # Основной цикл мониторинга
        last_stats_time = time.time()
        
        while tester.running:
            await asyncio.sleep(0.1)  # Очень быстрый цикл для мгновенности
            
            # Каждые 5 секунд показываем статистику
            if time.time() - last_stats_time >= 5:
                await tester.show_live_stats()
                last_stats_time = time.time()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Тест прерван пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        # Остановка и сводка
        await tester.stop_monitoring()
        await tester.show_events_summary()
        print("\n🎉 Интерактивный тест завершен!")

if __name__ == "__main__":
    asyncio.run(main())
