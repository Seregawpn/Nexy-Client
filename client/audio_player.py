import asyncio
import sounddevice as sd
import numpy as np
import logging
import queue
import threading
import time

logger = logging.getLogger(__name__)

class AudioPlayer:
    """
    Воспроизводит аудиопоток в реальном времени с использованием sounddevice.
    Принимает аудиофрагменты (chunks) в виде NumPy массивов и воспроизводит их бесшовно.
    """
    def __init__(self, sample_rate=48000, channels=1, dtype='int16'):
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        
        self.audio_queue = queue.Queue()
        self.playback_thread = None
        self.stop_event = threading.Event()
        self.stream = None
        self.is_playing = False
        
        # Внутренний буфер для плавного воспроизведения
        self.internal_buffer = np.array([], dtype=np.int16)
        self.buffer_lock = threading.Lock()
        
        # Флаг для отслеживания ошибок аудио
        self.audio_error = False
        self.audio_error_message = ""
        
        # ПРОСТАЯ блокировка буфера после прерывания
        self.buffer_blocked_until = 0  # Время до которого буфер заблокирован
        self.buffer_block_duration = 0.5  # Длительность блокировки в секундах
        
        # Проверяем доступность аудио устройств
        self._check_audio_devices()

    def _playback_callback(self, outdata, frames, time, status):
        """Callback-функция для sounddevice, вызывается для заполнения буфера вывода."""
        if status:
            logger.warning(f"Sounddevice status: {status}")

        try:
            with self.buffer_lock:
                # Проверяем внутренний буфер
                if len(self.internal_buffer) >= frames:
                    # Достаточно данных в буфере
                    outdata[:frames] = self.internal_buffer[:frames].reshape(frames, self.channels)
                    self.internal_buffer = self.internal_buffer[frames:]
                else:
                    # Недостаточно данных, пытаемся получить из очереди
                    try:
                        # Собираем ВСЕ доступные чанки в буфер
                        while not self.audio_queue.empty():
                            chunk = self.audio_queue.get_nowait()
                            if chunk is not None and len(chunk) > 0:
                                self.internal_buffer = np.concatenate([self.internal_buffer, chunk])
                                logger.debug(f"🎵 Добавлен чанк в буфер: {len(chunk)} сэмплов. Общий размер буфера: {len(self.internal_buffer)}")
                            self.audio_queue.task_done()
                    except queue.Empty:
                        pass
                    
                    # Теперь проверяем снова
                    if len(self.internal_buffer) >= frames:
                        outdata[:frames] = self.internal_buffer[:frames].reshape(frames, self.channels)
                        self.internal_buffer = self.internal_buffer[frames:]
                        logger.debug(f"🎵 Отправлено в аудио: {frames} сэмплов. Осталось в буфере: {len(self.internal_buffer)}")
                    else:
                        # Все еще недостаточно данных, заполняем тишиной
                        available = len(self.internal_buffer)
                        if available > 0:
                            outdata[:available] = self.internal_buffer.reshape(-1, self.channels)
                            outdata[available:frames] = 0
                            self.internal_buffer = np.array([], dtype=np.int16)
                            logger.debug(f"🎵 Отправлено доступных: {available} сэмплов, остальное тишина")
                        else:
                            # Если нет данных, принудительно проверяем очередь еще раз
                            try:
                                chunk = self.audio_queue.get_nowait()
                                if chunk is not None and len(chunk) > 0:
                                    # Обрабатываем полученный чанк
                                    if len(chunk) >= frames:
                                        outdata[:frames] = chunk[:frames].reshape(frames, self.channels)
                                        # Остаток чанка сохраняем в буфер
                                        if len(chunk) > frames:
                                            self.internal_buffer = chunk[frames:]
                                        logger.debug(f"🎵 Чанк обработан напрямую: {frames} сэмплов")
                                    else:
                                        # Чанк меньше frames, заполняем тишиной
                                        outdata[:len(chunk)] = chunk.reshape(-1, self.channels)
                                        outdata[len(chunk):frames] = 0
                                        logger.debug(f"🎵 Короткий чанк: {len(chunk)} сэмплов, остальное тишина")
                                else:
                                    # Нет данных, тишина
                                    outdata.fill(0)
                                    logger.debug("🔇 Нет данных - тишина")
                                self.audio_queue.task_done()
                            except queue.Empty:
                                # Очередь пуста, тишина
                                outdata.fill(0)
                                logger.debug("🔇 Очередь пуста - тишина")
        except Exception as e:
            logger.error(f"❌ Ошибка в playback callback: {e}")
            outdata.fill(0)  # В случае ошибки отправляем тишину

    def add_chunk(self, audio_chunk: np.ndarray):
        """Добавляет аудио чанк в очередь воспроизведения."""
        if audio_chunk is None or len(audio_chunk) == 0:
            logger.warning("⚠️ Попытка добавить пустой аудио чанк!")
            return
        
        chunk_size = len(audio_chunk)
        logger.debug(f"🎵 Добавляю аудио чанк размером {chunk_size} сэмплов")
        
        # Проверяем временную блокировку буфера
        if self.is_buffer_locked():
            logger.warning(f"🚨 БУФЕР ВРЕМЕННО ЗАБЛОКИРОВАН - пропускаю добавление аудио чанка размером {chunk_size}!")
            return
        
        try:
            # Добавляем чанк в очередь
            self.audio_queue.put(audio_chunk)
            logger.debug(f"✅ Аудио чанк добавлен в очередь. Размер очереди: {self.audio_queue.qsize()}")
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении аудио чанка: {e}")
            # Попытка восстановления
            try:
                if not self.audio_queue.full():
                    self.audio_queue.put(audio_chunk)
                    logger.info("✅ Аудио чанк добавлен после восстановления")
                else:
                    logger.warning("⚠️ Очередь переполнена, чанк отброшен")
            except Exception as e2:
                logger.error(f"❌ Критическая ошибка при восстановлении: {e2}")

    def start_playback(self):
        """Запускает потоковое воспроизведение аудио."""
        if self.is_playing:
            logger.warning("⚠️ Воспроизведение уже запущено!")
            return
        
        logger.info("Запуск потокового воспроизведения аудио...")
        self.stop_event.clear()
        self._clear_buffers()  # Очищаем буферы перед началом
        
        try:
            # Создаем новый поток воспроизведения
            self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
            self.playback_thread.start()
            
            # Безопасно инициализируем звуковой поток с авто-подбором устройства
            self.stream = self._safe_init_stream()
            self.is_playing = True
            
            logger.info("✅ Потоковое воспроизведение аудио запущено!")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при запуске воспроизведения: {e}")
            self.is_playing = False
            self.playback_thread = None
            self.stream = None

    def stop_playback(self):
        """Останавливает потоковое воспроизведение аудио."""
        if not self.is_playing:
            logger.warning("⚠️ Воспроизведение уже остановлено!")
            return
        
        logger.info("Остановка потокового воспроизведения аудио...")
        
        try:
            # Устанавливаем флаг остановки
            self.stop_event.set()
            
            # Останавливаем звуковой поток
            if self.stream:
                if hasattr(self.stream, 'active') and self.stream.active:
                    self.stream.stop()
                    logger.info("✅ Звуковой поток остановлен")
                self.stream.close()
                self.stream = None
                logger.info("✅ Звуковой поток закрыт")
            
            # Ждем завершения потока воспроизведения
            if self.playback_thread and self.playback_thread.is_alive():
                self.playback_thread.join(timeout=1.0)
                if self.playback_thread.is_alive():
                    logger.warning("⚠️ Поток воспроизведения не завершился за 1 секунду")
                else:
                    logger.info("✅ Поток воспроизведения завершен")
            
            # Сбрасываем состояние
            self.is_playing = False
            self.playback_thread = None
            
            # Очищаем буферы
            self._clear_buffers()
            
            logger.info("✅ Потоковое воспроизведение аудио остановлено!")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при остановке воспроизведения: {e}")
            # Принудительно сбрасываем состояние
            self.is_playing = False
            self.playback_thread = None
            self.stream = None



    def _playback_loop(self):
        """Фоновый поток для воспроизведения аудио"""
        logger.info("🔄 Фоновый поток воспроизведения запущен")
        
        try:
            while not self.stop_event.is_set():
                # Проверяем, есть ли данные для воспроизведения
                if not self.audio_queue.empty() or len(self.internal_buffer) > 0:
                    # Небольшая пауза для снижения нагрузки на CPU
                    time.sleep(0.001)  # 1ms
                else:
                    # Если нет данных, ждем немного
                    time.sleep(0.01)  # 10ms
                    
        except Exception as e:
            logger.error(f"❌ Ошибка в фоновом потоке воспроизведения: {e}")
        finally:
            logger.info("🔄 Фоновый поток воспроизведения завершен")

    def _safe_init_stream(self):
        """
        Безопасная инициализация аудио потока с обработкой ошибок PortAudio.
        """
        try:
            # Пробуем разные настройки для macOS
            device_settings = [
                {'device': None, 'channels': self.channels},  # Системный по умолчанию
                {'device': 'default', 'channels': self.channels},  # Явно указываем default
                {'device': sd.default.device[1], 'channels': self.channels},  # Только выход
            ]
            
            for settings in device_settings:
                try:
                    logger.info(f"🔄 Пробую инициализировать аудио с настройками: {settings}")
                    
                    # Создаем поток с дополнительными параметрами для macOS
                    stream = sd.OutputStream(
                        samplerate=self.sample_rate,
                        channels=settings['channels'],
                        dtype=self.dtype,
                        device=settings['device'],
                        callback=self._playback_callback,
                        blocksize=2048,  # Увеличиваем размер блока для стабильности
                        latency='high'   # Более высокая задержка для предотвращения перегрузок
                    )
                    
                    stream.start()
                    logger.info(f"✅ Аудио поток успешно инициализирован с настройками: {settings}")
                    return stream
                    
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось инициализировать с настройками {settings}: {e}")
                    continue
            
            # Если все попытки не удались, пробуем альтернативные настройки
            logger.info("🔄 Пробую альтернативные настройки для macOS...")
            
            # Пробуем с минимальными настройками
            try:
                stream = sd.OutputStream(
                    samplerate=44100,  # Стандартная частота
                    channels=1,        # Моно
                    dtype='int16',     # Стандартный тип
                    callback=self._playback_callback,
                    blocksize=2048,    # Увеличенный размер блока
                    latency='high'     # Высокая задержка для стабильности
                )
                stream.start()
                logger.info("✅ Аудио поток инициализирован с альтернативными настройками")
                return stream
            except Exception as e:
                logger.warning(f"⚠️ Альтернативные настройки не помогли: {e}")
            
            # Если все попытки не удались
            raise Exception("Не удалось инициализировать аудио поток ни с одним из доступных устройств")
            
        except Exception as e:
            self.audio_error = True
            self.audio_error_message = str(e)
            logger.error(f"❌ Критическая ошибка инициализации аудио: {e}")
            raise

    def _clear_buffers(self):
        """Очищает внутренний буфер и очередь аудио."""
        # Очищаем внутренний буфер
        with self.buffer_lock:
            self.internal_buffer = np.array([], dtype=np.int16)
            logger.debug("✅ Внутренний буфер очищен")
        
        # Очищаем очередь аудио
        try:
            # Используем более эффективный способ очистки очереди
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                    self.audio_queue.task_done()
                except queue.Empty:
                    break
            
            # Дополнительная очистка для гарантии
            with self.audio_queue.mutex:
                self.audio_queue.queue.clear()
            
            logger.debug("✅ Очередь аудио очищена")
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при очистке очереди: {e}")
        
        # Сбрасываем счетчик join() для корректной работы
        try:
            self.audio_queue.join()
        except Exception:
            pass

    def wait_for_queue_empty(self):
        """
        НЕБЛОКИРУЮЩЕЕ ожидание завершения воспроизведения.
        Возвращает управление НЕМЕДЛЕННО, не зависает!
        """
        logger.info("🎵 Проверяю статус воспроизведения (НЕБЛОКИРУЮЩЕЕ)...")
        
        # БЫСТРАЯ ПРОВЕРКА без ожидания
        queue_size = self.audio_queue.qsize()
        with self.buffer_lock:
            buffer_size = len(self.internal_buffer)
            
        if queue_size == 0 and buffer_size == 0:
            logger.info("✅ Аудио уже завершено")
            return True
        else:
            logger.info(f"📊 Аудио еще воспроизводится: очередь={queue_size}, буфер={buffer_size}")
            return False

    def play_beep(self, frequency: float = 1000.0, duration_sec: float = 0.12, volume: float = 0.4):
        """
        Проигрывает короткий сигнал (beep) через текущую систему воспроизведения.
        - frequency: частота тона в Гц
        - duration_sec: длительность сигнала в секундах
        - volume: громкость [0.0..1.0]
        """
        try:
            # Гарантируем запуск воспроизведения
            if not self.is_playing:
                self.start_playback()

            # Генерируем синусоидальную волну
            num_samples = int(self.sample_rate * duration_sec)
            if num_samples <= 0:
                return

            t = np.linspace(0, duration_sec, num_samples, endpoint=False)
            waveform = np.sin(2 * np.pi * frequency * t)
            amplitude = int(32767 * max(0.0, min(volume, 1.0)))
            samples = (amplitude * waveform).astype(np.int16)

            # Добавляем в очередь для воспроизведения
            self.add_chunk(samples)
        except Exception as e:
            logger.warning(f"⚠️ Не удалось воспроизвести сигнал: {e}")

    def start_audio_monitoring(self):
        """
        Запускает фоновый мониторинг завершения аудио.
        НЕ блокирует основной поток!
        """
        logger.info("🎵 Запускаю фоновый мониторинг аудио...")
        
        # Создаем фоновую задачу для мониторинга
        import threading
        
        def monitor_audio():
            """Фоновая функция мониторинга"""
            try:
                while self.is_playing:
                    time.sleep(0.5)  # Проверяем каждые 500ms
                    
                    # Проверяем статус
                    queue_size = self.audio_queue.qsize()
                    with self.buffer_lock:
                        buffer_size = len(self.internal_buffer)
                    
                    # Если все воспроизведено - останавливаем
                    if queue_size == 0 and buffer_size == 0:
                        logger.info("✅ Аудио завершено, останавливаю мониторинг")
                        self.is_playing = False
                        break
                        
                logger.info("✅ Мониторинг аудио завершен")
                
            except Exception as e:
                logger.error(f"❌ Ошибка в мониторинге аудио: {e}")
                self.is_playing = False
        
        # Запускаем мониторинг в отдельном потоке
        self.monitor_thread = threading.Thread(target=monitor_audio, daemon=True)
        self.monitor_thread.start()
        logger.info("✅ Мониторинг аудио запущен в фоне")

    async def cleanup(self):
        """Очистка ресурсов плеера."""
        self.stop_playback()
        logger.info("Ресурсы AudioPlayer очищены.")

    def get_audio_status(self):
        """
        Возвращает статус аудио системы и информацию об ошибках.
        """
        return {
            'is_playing': self.is_playing,
            'has_error': self.audio_error,
            'error_message': self.audio_error_message,
            'stream_active': self.stream is not None and hasattr(self.stream, 'active') and self.stream.active,
            'queue_size': self.audio_queue.qsize(),
            'buffer_size': len(self.internal_buffer)
        }

    def reset_audio_error(self):
        """
        Сбрасывает флаги ошибок аудио для повторной попытки инициализации.
        """
        self.audio_error = False
        self.audio_error_message = ""
        logger.info("🔄 Флаги ошибок аудио сброшены")

    def clear_all_audio_data(self):
        """ПРИНУДИТЕЛЬНО очищает ВСЕ аудио данные - включая очередь и активное воспроизведение"""
        clear_time = time.time()
        logger.warning(f"🚨 clear_all_audio_data() вызван в {clear_time:.3f}")
        
        try:
            # Логируем состояние ДО очистки
            queue_before = self.audio_queue.qsize()
            buffer_before = len(self.internal_buffer)
            stream_active = hasattr(self, 'stream') and self.stream and hasattr(self.stream, 'active') and self.stream.active
            logger.warning(f"   📊 Состояние ДО: queue={queue_before}, buffer={buffer_before}, stream_active={stream_active}")
            
            logger.warning("🚨 ПРИНУДИТЕЛЬНАЯ очистка ВСЕХ аудио данных...")
            
            # 1️⃣ ПРИНУДИТЕЛЬНО очищаем очередь чанков
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                    self.audio_queue.task_done()
                except:
                    pass
            
            # 2️⃣ ДОПОЛНИТЕЛЬНАЯ очистка очереди через mutex
            try:
                with self.audio_queue.mutex:
                    self.audio_queue.queue.clear()
                logger.warning("🚨 Очередь ПРИНУДИТЕЛЬНО очищена через mutex!")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка очистки через mutex: {e}")
            
            # 3️⃣ ПРИНУДИТЕЛЬНО очищаем внутренний буфер
            with self.buffer_lock:
                self.internal_buffer = np.array([], dtype=np.int16)
            
            # 4️⃣ ПРИНУДИТЕЛЬНО останавливаем поток воспроизведения
            if hasattr(self, 'stream') and self.stream:
                try:
                    if hasattr(self.stream, 'active') and self.stream.active:
                        self.stream.abort()  # Агрессивная остановка
                        logger.warning("🚨 Аудио поток ПРИНУДИТЕЛЬНО остановлен через abort!")
                    self.stream.close()
                    self.stream = None
                    logger.warning("🚨 Аудио поток ПРИНУДИТЕЛЬНО закрыт!")
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка остановки потока: {e}")
            
            # 5️⃣ Сбрасываем состояние
            self.is_playing = False
            
            # 6️⃣ ПРИНУДИТЕЛЬНО останавливаем все звуковые потоки
            try:
                sd.stop()  # Останавливает все звуковые потоки
                logger.warning("🚨 ВСЕ звуковые потоки ПРИНУДИТЕЛЬНО остановлены!")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка остановки всех потоков: {e}")
            
            # 7️⃣ ДОПОЛНИТЕЛЬНАЯ очистка через _clear_buffers
            try:
                self._clear_buffers()
                logger.warning("🚨 Дополнительная очистка буферов выполнена!")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка дополнительной очистки: {e}")
            
            # 8️⃣ Устанавливаем временную блокировку буфера
            try:
                self.set_buffer_lock()
                logger.warning("🚨 Временная блокировка буфера установлена!")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка установки временной блокировки: {e}")
            
            # Логируем состояние ПОСЛЕ очистки
            queue_after = self.audio_queue.qsize()
            buffer_after = len(self.internal_buffer)
            total_time = (time.time() - clear_time) * 1000
            logger.warning(f"   📊 Состояние ПОСЛЕ: queue={queue_after}, buffer={buffer_after}")
            logger.warning(f"   ⏱️ Общее время очистки: {total_time:.1f}ms")
            
            # Проверяем результат
            if queue_after == 0 and buffer_after == 0:
                logger.warning("   🎯 ОЧИСТКА УСПЕШНА - все буферы пусты!")
            else:
                logger.warning(f"   ⚠️ ОЧИСТКА НЕПОЛНАЯ - queue={queue_after}, buffer={buffer_after}")
            
            logger.warning("✅ ВСЕ аудио данные ПРИНУДИТЕЛЬНО очищены!")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при очистке всех аудио данных: {e}")
            import traceback
            logger.error(f"   🔍 Traceback: {traceback.format_exc()}")

    def interrupt_immediately(self):
        """МГНОВЕННОЕ прерывание без ожидания - для критических ситуаций"""
        try:
            logger.warning("🚨 МГНОВЕННОЕ прерывание аудио...")
            
            # 1️⃣ НЕМЕДЛЕННО устанавливаем флаги прерывания
            self.interrupt_flag.set()
            self.stop_event.set()
            
            # 2️⃣ ПРИНУДИТЕЛЬНО очищаем буферы
            with self.buffer_lock:
                self.internal_buffer = np.array([], dtype=np.int16)
            
            # 3️⃣ Очищаем очередь чанков
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                    self.audio_queue.task_done()
                except:
                    pass
            
            # 4️⃣ Сбрасываем состояние
            self.is_playing = False
            
            logger.warning("✅ МГНОВЕННОЕ прерывание аудио выполнено!")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при мгновенном прерывании: {e}")

    def force_stop(self, immediate=False):
        """Универсальный метод остановки аудио с опцией мгновенной остановки"""
        if immediate:
            logger.info("🚨 force_stop(immediate=True) вызван - МГНОВЕННАЯ остановка")
        else:
            logger.info("🚨 force_stop() вызван - обычная остановка")
        
        try:
            # 1️⃣ Устанавливаем флаг остановки
            self.stop_event.set()
            self.is_playing = False
            
            # 2️⃣ Останавливаем поток воспроизведения
            if self.playback_thread and self.playback_thread.is_alive():
                if immediate:
                    logger.info("   🚨 МГНОВЕННО останавливаю поток воспроизведения...")
                    
                    # Принудительно прерываем поток
                    import ctypes
                    thread_id = self.playback_thread.ident
                    if thread_id:
                        try:
                            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                                ctypes.c_long(thread_id), 
                                ctypes.py_object(SystemExit)
                            )
                            if res > 1:
                                ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
                                logger.warning("   ⚠️ Не удалось прервать поток воспроизведения")
                            else:
                                logger.info("   ✅ Поток воспроизведения принудительно прерван")
                        except Exception as e:
                            logger.warning(f"   ⚠️ Ошибка принудительного прерывания потока: {e}")
                    
                    # Ждем завершения с коротким таймаутом
                    timeout = 0.1
                else:
                    logger.info("   🚨 Останавливаю поток воспроизведения...")
                    timeout = 0.5
                
                self.playback_thread.join(timeout=timeout)
                if self.playback_thread.is_alive():
                    logger.warning(f"   ⚠️ Поток воспроизведения не остановился в таймаут {timeout}s")
                else:
                    logger.info("   ✅ Поток воспроизведения остановлен")
            
            # 3️⃣ Останавливаем аудио поток
            if self.stream and self.stream.active:
                if immediate:
                    logger.info("   🚨 МГНОВЕННО останавливаю аудио поток...")
                    try:
                        self.stream.stop()
                        self.stream.close()
                        self.stream = None
                        logger.info("   ✅ Аудио поток МГНОВЕННО остановлен")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Ошибка остановки аудио потока: {e}")
                else:
                    logger.info("   🚨 Останавливаю аудио поток...")
                    try:
                        self.stream.stop()
                        self.stream.close()
                        self.stream = None
                        logger.info("   ✅ Аудио поток остановлен")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Ошибка остановки аудио потока: {e}")
            
            # 4️⃣ Очищаем очередь
            if not self.audio_queue.empty():
                queue_size = self.audio_queue.qsize()
                if immediate:
                    logger.info(f"   🧹 МГНОВЕННО очищаю очередь: {queue_size} элементов")
                else:
                    logger.info(f"   🧹 Очищаю очередь: {queue_size} элементов")
                
                while not self.audio_queue.empty():
                    try:
                        self.audio_queue.get_nowait()
                    except:
                        break
                
                if immediate:
                    logger.info("   ✅ Очередь МГНОВЕННО очищена")
                else:
                    logger.info("   ✅ Очередь очищена")
            
            # 5️⃣ Очищаем внутренний буфер
            with self.buffer_lock:
                self.internal_buffer = np.array([], dtype=np.int16)
                if immediate:
                    logger.info("   ✅ Внутренний буфер МГНОВЕННО очищен")
                else:
                    logger.info("   ✅ Внутренний буфер очищен")
            
            # 6️⃣ Для мгновенной остановки - дополнительная очистка
            if immediate:
                # Принудительно останавливаем все звуковые потоки
                try:
                    import sounddevice as sd
                    sd.stop()  # Останавливает все звуковые потоки
                    logger.info("   ✅ Все звуковые потоки МГНОВЕННО остановлены")
                except Exception as e:
                    logger.warning(f"   ⚠️ Ошибка остановки звуковых потоков: {e}")
            
            if immediate:
                logger.info("✅ force_stop(immediate=True) завершен")
            else:
                logger.info("✅ force_stop() завершен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка в force_stop: {e}")
    
    def force_stop_playback(self):
        """МГНОВЕННО останавливает воспроизведение аудио (alias для force_stop(immediate=True))"""
        return self.force_stop(immediate=True)
    
    def stop_all_audio_threads(self):
        """Останавливает все аудио потоки"""
        logger.info("🚨 stop_all_audio_threads() вызван")
        
        try:
            # 1️⃣ Останавливаем основной поток воспроизведения
            if self.playback_thread and self.playback_thread.is_alive():
                logger.info("   🚨 Останавливаю основной поток воспроизведения...")
                self.stop_event.set()
                self.playback_thread.join(timeout=0.2)
                if self.playback_thread.is_alive():
                    logger.warning("   ⚠️ Основной поток не остановился в таймаут")
                else:
                    logger.info("   ✅ Основной поток остановлен")
            
            # 2️⃣ Останавливаем все дочерние потоки
            import threading
            current_thread = threading.current_thread()
            all_threads = threading.enumerate()
            
            audio_threads = []
            for thread in all_threads:
                if (thread != current_thread and 
                    thread != threading.main_thread() and 
                    thread.is_alive() and
                    'audio' in thread.name.lower()):
                    audio_threads.append(thread)
            
            if audio_threads:
                logger.info(f"   🚨 Найдено {len(audio_threads)} аудио потоков для остановки")
                for thread in audio_threads:
                    try:
                        logger.info(f"   🚨 Останавливаю поток: {thread.name}")
                        # Принудительно прерываем поток
                        import ctypes
                        thread_id = thread.ident
                        if thread_id:
                            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                                ctypes.c_long(thread_id), 
                                ctypes.py_object(SystemExit)
                            )
                            if res > 1:
                                ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
                                logger.warning(f"   ⚠️ Не удалось прервать поток: {thread.name}")
                            else:
                                logger.info(f"   ✅ Поток прерван: {thread.name}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Ошибка прерывания потока {thread.name}: {e}")
            else:
                logger.info("   ✅ Дополнительные аудио потоки не найдены")
            
            # 3️⃣ Останавливаем аудио поток
            if self.stream and self.stream.active:
                logger.info("   🚨 Останавливаю аудио поток...")
                try:
                    self.stream.stop()
                    self.stream.close()
                    self.stream = None
                    logger.info("   ✅ Аудио поток остановлен")
                except Exception as e:
                    logger.warning(f"   ⚠️ Ошибка остановки аудио потока: {e}")
            
            logger.info("✅ stop_all_audio_threads завершен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка в stop_all_audio_threads: {e}")
    
    def clear_audio_buffers(self):
        """Очищает все аудио буферы"""
        logger.info("🧹 clear_audio_buffers() вызван")
        
        try:
            # 1️⃣ Очищаем очередь
            if not self.audio_queue.empty():
                queue_size = self.audio_queue.qsize()
                logger.info(f"   🧹 Очищаю очередь: {queue_size} элементов")
                while not self.audio_queue.empty():
                    try:
                        self.audio_queue.get_nowait()
                    except:
                        break
                logger.info("   ✅ Очередь очищена")
            
            # 2️⃣ Очищаем внутренний буфер
            with self.buffer_lock:
                self.internal_buffer = np.array([], dtype=np.int16)
                logger.info("   ✅ Внутренний буфер очищен")
            
            # 3️⃣ Очищаем системные аудио буферы
            try:
                import sounddevice as sd
                sd.stop()
                logger.info("   ✅ Системные аудио буферы очищены")
            except Exception as e:
                logger.warning(f"   ⚠️ Ошибка очистки системных буферов: {e}")
            
            logger.info("✅ clear_audio_buffers завершен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка в clear_audio_buffers: {e}")

    def _check_audio_devices(self):
        """Проверяет доступность аудио устройств."""
        try:
            sd.query_devices()
            logger.info("✅ Аудио устройства доступны.")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось получить список аудио устройств: {e}")
            self.audio_error = True
            self.audio_error_message = f"Не удалось получить список аудио устройств: {e}"
    
    def set_buffer_lock(self, duration=None):
        """Устанавливает временную блокировку буфера для предотвращения добавления новых чанков."""
        if duration is None:
            duration = self.buffer_block_duration
        
        self.buffer_blocked_until = time.time() + duration
        logger.warning(f"🚨 Временная блокировка буфера установлена на {duration:.1f} секунд")
    
    def is_buffer_locked(self):
        """Проверяет, заблокирован ли буфер временно."""
        return time.time() < self.buffer_blocked_until