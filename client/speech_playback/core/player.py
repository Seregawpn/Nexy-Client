"""
Sequential Speech Player - Основной плеер для последовательного воспроизведения

ОСНОВНЫЕ ПРИНЦИПЫ:
1. Последовательное воспроизведение - один чанк за раз
2. Без лимитов размера - накопление всех данных
3. Thread-safety - безопасная работа в многопоточной среде
4. macOS совместимость - для PKG упаковки
5. Простота и надежность - минимальная сложность
"""

import logging
import threading
import time
import asyncio
import sounddevice as sd
import numpy as np
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

from .state import StateManager, PlaybackState, ChunkState
from .buffer import ChunkBuffer, ChunkInfo
from ..utils.audio_utils import resample_audio, convert_channels
from ..utils.device_utils import get_best_audio_device
from ..macos.core_audio import CoreAudioManager
from ..macos.performance import PerformanceMonitor

logger = logging.getLogger(__name__)

@dataclass
class PlayerConfig:
    """Конфигурация плеера"""
    sample_rate: int = 44100
    channels: int = 2
    dtype: str = 'int16'
    buffer_size: int = 512
    max_memory_mb: int = 1024
    device_id: Optional[int] = None
    auto_device_selection: bool = True

class SequentialSpeechPlayer:
    """Плеер для последовательного воспроизведения речи"""
    
    def __init__(self, config: Optional[PlayerConfig] = None):
        """
        Инициализация плеера
        
        Args:
            config: Конфигурация плеера
        """
        self.config = config or PlayerConfig()
        self.state_manager = StateManager()
        self.chunk_buffer = ChunkBuffer(max_memory_mb=self.config.max_memory_mb)
        
        # Потоки и синхронизация
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Начинаем с разблокированной паузы
        
        # Аудио поток
        self._audio_stream: Optional[sd.OutputStream] = None
        self._stream_lock = threading.RLock()
        
        # macOS компоненты
        self._core_audio_manager = CoreAudioManager()
        self._performance_monitor = PerformanceMonitor()
        
        # Callbacks
        self._on_chunk_started: Optional[Callable[[ChunkInfo], None]] = None
        self._on_chunk_completed: Optional[Callable[[ChunkInfo], None]] = None
        self._on_playback_completed: Optional[Callable[[], None]] = None
        self._on_error: Optional[Callable[[Exception], None]] = None
        
        logger.info("🔧 SequentialSpeechPlayer инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация плеера"""
        try:
            # Инициализация macOS компонентов
            if not self._core_audio_manager.initialize():
                logger.error("❌ Ошибка инициализации Core Audio")
                return False
            
            # Выбор аудио устройства
            if self.config.auto_device_selection:
                device = get_best_audio_device()
                if device:
                    self.config.device_id = device.portaudio_index
                    logger.info(f"🎵 Выбрано устройство: {device.name}")
                else:
                    logger.warning("⚠️ Не удалось выбрать аудио устройство")
            
            # Инициализация мониторинга производительности
            self._performance_monitor.start()
            
            logger.info("✅ Плеер инициализирован успешно")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации плеера: {e}")
            self.state_manager.set_state(PlaybackState.ERROR)
            return False
    
    def add_audio_data(self, audio_data: np.ndarray, priority: int = 0, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Добавить аудио данные для воспроизведения
        
        Args:
            audio_data: Аудио данные
            priority: Приоритет чанка
            metadata: Дополнительные метаданные
            
        Returns:
            ID чанка
        """
        try:
            # Resampling если необходимо
            if hasattr(audio_data, 'sample_rate') and audio_data.sample_rate != self.config.sample_rate:
                audio_data = resample_audio(audio_data, self.config.sample_rate)
            
            # Конвертация каналов если необходимо
            if len(audio_data.shape) == 1:  # Моно
                audio_data = convert_channels(audio_data, self.config.channels)
            
            # Добавляем в буфер
            chunk_id = self.chunk_buffer.add_chunk(audio_data, priority, metadata)
            
            logger.info(f"✅ Аудио данные добавлены: {chunk_id} (size: {len(audio_data)})")
            
            return chunk_id
            
        except Exception as e:
            logger.error(f"❌ Ошибка добавления аудио данных: {e}")
            self.state_manager.set_state(PlaybackState.ERROR)
            raise
    
    def start_playback(self) -> bool:
        """Запуск воспроизведения"""
        try:
            # Проверяем, что можем запустить воспроизведение
            if self.state_manager.current_state not in [PlaybackState.IDLE, PlaybackState.PAUSED]:
                logger.warning("⚠️ Невозможно запустить воспроизведение в текущем состоянии")
                return False
            
            # Переходим в состояние PLAYING
            self.state_manager.set_state(PlaybackState.PLAYING)
            
            # НЕ очищаем данные - они уже добавлены в буфер
            
            # Запускаем аудио поток
            if not self._start_audio_stream():
                self.state_manager.set_state(PlaybackState.ERROR)
                return False
            
            # Запускаем поток воспроизведения
            self._stop_event.clear()
            self._pause_event.set()
            
            self._playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
            self._playback_thread.start()
            
            logger.info("🎵 Воспроизведение запущено")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска воспроизведения: {e}")
            self.state_manager.set_state(PlaybackState.ERROR)
            return False
    
    def stop_playback(self) -> bool:
        """Остановка воспроизведения"""
        try:
            # Проверяем, что можем остановить воспроизведение
            if self.state_manager.current_state not in [PlaybackState.PLAYING, PlaybackState.PAUSED]:
                logger.warning("⚠️ Невозможно остановить воспроизведение в текущем состоянии")
                return False
            
            # Переходим в состояние STOPPING
            self.state_manager.set_state(PlaybackState.STOPPING)
            
            # Останавливаем поток воспроизведения
            self._stop_event.set()
            
            # Ждем завершения потока
            if self._playback_thread and self._playback_thread.is_alive():
                self._playback_thread.join(timeout=5.0)
            
            # Останавливаем аудио поток
            self._stop_audio_stream()
            
            # Очищаем буферы
            self.chunk_buffer.clear_all()
            
            # Переходим в состояние STOPPED
            self.state_manager.set_state(PlaybackState.IDLE)
            
            logger.info("🛑 Воспроизведение остановлено")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки воспроизведения: {e}")
            self.state_manager.set_state(PlaybackState.ERROR)
            return False
    
    def pause_playback(self) -> bool:
        """Приостановка воспроизведения"""
        try:
            # Проверяем, что можем поставить на паузу
            if self.state_manager.current_state != PlaybackState.PLAYING:
                logger.warning("⚠️ Невозможно приостановить воспроизведение в текущем состоянии")
                return False
            
            self._pause_event.clear()
            self.state_manager.set_state(PlaybackState.PAUSED)
            
            logger.info("⏸️ Воспроизведение приостановлено")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка приостановки воспроизведения: {e}")
            self.state_manager.set_state(PlaybackState.ERROR)
            return False
    
    def resume_playback(self) -> bool:
        """Возобновление воспроизведения"""
        try:
            # Проверяем, что можем возобновить воспроизведение
            if self.state_manager.current_state != PlaybackState.PAUSED:
                logger.warning("⚠️ Невозможно возобновить воспроизведение в текущем состоянии")
                return False
            
            self._pause_event.set()
            self.state_manager.set_state(PlaybackState.PLAYING)
            
            logger.info("▶️ Воспроизведение возобновлено")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка возобновления воспроизведения: {e}")
            self.state_manager.set_state(PlaybackState.ERROR)
            return False
    
    def _start_audio_stream(self) -> bool:
        """Запуск аудио потока"""
        try:
            with self._stream_lock:
                if self._audio_stream is not None:
                    logger.warning("⚠️ Аудио поток уже запущен")
                    return True
                
                # Конфигурация потока
                stream_config = {
                    'device': self.config.device_id,
                    'channels': self.config.channels,
                    'dtype': self.config.dtype,
                    'samplerate': self.config.sample_rate,
                    'blocksize': self.config.buffer_size,
                    'callback': self._audio_callback
                }
                
                # Создаем поток
                self._audio_stream = sd.OutputStream(**stream_config)
                self._audio_stream.start()
                
                logger.info(f"🎵 Аудио поток запущен (device: {self.config.device_id}, channels: {self.config.channels})")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска аудио потока: {e}")
            return False
    
    def _stop_audio_stream(self):
        """Остановка аудио потока"""
        try:
            with self._stream_lock:
                if self._audio_stream is not None:
                    self._audio_stream.stop()
                    self._audio_stream.close()
                    self._audio_stream = None
                    logger.info("🛑 Аудио поток остановлен")
                    
        except Exception as e:
            logger.error(f"❌ Ошибка остановки аудио потока: {e}")
    
    def _audio_callback(self, outdata, frames, time, status):
        """Callback для воспроизведения аудио"""
        try:
            if status:
                logger.warning(f"⚠️ Статус аудио потока: {status}")
            
            # Получаем данные из буфера
            data = self.chunk_buffer.get_playback_data(frames)
            
            # Формируем выходные данные
            if len(data) == 0:
                # Если данных нет, заполняем тишиной
                outdata[:] = np.zeros((frames, self.config.channels), dtype=self.config.dtype)
            else:
                # Убеждаемся, что данные имеют правильную форму
                if len(data.shape) == 1:
                    # 1D данные - дублируем для стерео
                    if self.config.channels == 1:
                        outdata[:] = data.reshape(-1, 1)
                    else:
                        outdata[:] = np.column_stack([data, data])
                else:
                    # 2D данные - используем как есть
                    outdata[:] = data.reshape(-1, self.config.channels)
                
        except Exception as e:
            logger.error(f"❌ Ошибка в audio callback: {e}")
            outdata[:] = np.zeros((frames, self.config.channels), dtype=self.config.dtype)
    
    def _playback_loop(self):
        """Основной цикл воспроизведения - упрощенная версия"""
        try:
            logger.info("🔄 Playback loop запущен")
            
            while not self._stop_event.is_set():
                # Проверяем паузу
                self._pause_event.wait()
                
                # Получаем следующий чанк
                chunk_info = self.chunk_buffer.get_next_chunk(timeout=0.1)
                
                if chunk_info is not None:
                    # Отмечаем начало обработки
                    chunk_info.state = ChunkState.PLAYING
                    
                    # Callback начала чанка
                    if self._on_chunk_started:
                        self._on_chunk_started(chunk_info)
                    
                    # Добавляем в буфер воспроизведения
                    if not self.chunk_buffer.add_to_playback_buffer(chunk_info):
                        logger.error(f"❌ Ошибка добавления чанка {chunk_info.id} в буфер воспроизведения")
                        chunk_info.state = ChunkState.ERROR
                        continue
                    
                    # Ждем завершения воспроизведения этого чанка
                    self._wait_for_chunk_completion(chunk_info)
                    
                    # Отмечаем завершение
                    self.chunk_buffer.mark_chunk_completed(chunk_info)
                    
                    # Callback завершения чанка
                    if self._on_chunk_completed:
                        self._on_chunk_completed(chunk_info)
                    
                    logger.info(f"✅ Чанк обработан: {chunk_info.id}")
                else:
                    # Нет чанков - небольшая задержка
                    time.sleep(0.01)
            
            logger.info("🔄 Playback loop завершен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка в playback loop: {e}")
            self.state_manager.set_state(PlaybackState.ERROR)
    
    def _wait_for_chunk_completion(self, chunk_info: ChunkInfo, timeout: float = 30.0):
        """Ждать завершения воспроизведения чанка"""
        start_time = time.time()
        
        # Ожидаем, пока буфер воспроизведения не будет пустым
        # Это означает, что весь чанк был воспроизведен
        while time.time() - start_time < timeout:
            if not self.chunk_buffer.has_data:
                logger.info(f"✅ Чанк {chunk_info.id} полностью воспроизведен")
                return
            
            time.sleep(0.01)
        
        logger.warning(f"⚠️ Таймаут ожидания завершения чанка {chunk_info.id}")
    
    def wait_for_completion(self, timeout: float = 30.0) -> bool:
        """Ждать завершения воспроизведения всех чанков"""
        return self.chunk_buffer.wait_for_completion(timeout)
    
    def set_callbacks(self, 
                     on_chunk_started: Optional[Callable[[ChunkInfo], None]] = None,
                     on_chunk_completed: Optional[Callable[[ChunkInfo], None]] = None,
                     on_playback_completed: Optional[Callable[[], None]] = None,
                     on_error: Optional[Callable[[Exception], None]] = None):
        """Установить callbacks"""
        self._on_chunk_started = on_chunk_started
        self._on_chunk_completed = on_chunk_completed
        self._on_playback_completed = on_playback_completed
        self._on_error = on_error
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику плеера"""
        return {
            'state': self.state_manager.current_state.value,
            'is_playing': self.state_manager.is_playing,
            'is_paused': self.state_manager.is_paused,
            'has_error': self.state_manager.has_error,
            'buffer_stats': self.chunk_buffer.get_stats(),
            'performance_stats': self._performance_monitor.get_stats()
        }
    
    def shutdown(self):
        """Завершение работы плеера"""
        try:
            # Останавливаем воспроизведение
            self.stop_playback()
            
            # Останавливаем мониторинг производительности
            self._performance_monitor.stop()
            
            # Очищаем буферы
            self.chunk_buffer.clear_all()
            
            logger.info("🛑 Плеер завершил работу")
            
        except Exception as e:
            logger.error(f"❌ Ошибка завершения работы плеера: {e}")












































    def get_status(self) -> Dict[str, Any]:
        """
        Получает статус плеера
        
        Returns:
            Dict с информацией о статусе
        """
        return {
            "state": self.state_manager.current_state.value,
            "chunk_count": self.chunk_buffer.queue_size,
            "buffer_size": self.chunk_buffer.buffer_size,
            "is_playing": self.state_manager.current_state == PlaybackState.PLAYING,
            "is_paused": self.state_manager.current_state == PlaybackState.PAUSED,
            "device_id": self.config.device_id,
            "sample_rate": self.config.sample_rate,
            "channels": self.config.channels
        }
