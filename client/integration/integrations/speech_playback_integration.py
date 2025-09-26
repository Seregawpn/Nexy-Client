"""
SpeechPlaybackIntegration — интеграция модуля последовательного воспроизведения с EventBus

Слушает gRPC-ответы (`grpc.response.audio`, `grpc.request_completed|failed`) и проигрывает аудио-чанки.
Поддерживает отмену через `keyboard.short_press`/`interrupt.request`.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

import numpy as np

from integration.core.event_bus import EventBus, EventPriority
from integration.core.state_manager import ApplicationStateManager, AppMode
from integration.core.error_handler import ErrorHandler

from modules.speech_playback.core.player import SequentialSpeechPlayer, PlayerConfig
from modules.speech_playback.core.state import PlaybackState

# ЦЕНТРАЛИЗОВАННАЯ КОНФИГУРАЦИЯ АУДИО
from config.unified_config_loader import unified_config

logger = logging.getLogger(__name__)


class SpeechPlaybackIntegration:
    """Интеграция SequentialSpeechPlayer с EventBus"""

    def __init__(
        self,
        event_bus: EventBus,
        state_manager: ApplicationStateManager,
        error_handler: ErrorHandler,
    ):
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.error_handler = error_handler
        
        # ЦЕНТРАЛИЗОВАННАЯ КОНФИГУРАЦИЯ - единый источник истины
        self.config = unified_config.get_speech_playback_config()

        self._player: Optional[SequentialSpeechPlayer] = None
        self._initialized = False
        self._running = False
        self._had_audio_for_session: Dict[Any, bool] = {}
        self._finalized_sessions: Dict[Any, bool] = {}
        self._last_audio_ts: float = 0.0
        self._silence_task: Optional[asyncio.Task] = None
        # Пометка завершённых сервером сессий (получен grpc.request_completed/failed)
        self._grpc_done_sessions: Dict[Any, bool] = {}
        # Текущая активная сессия воспроизведения (последняя)
        self._current_session_id: Optional[Any] = None
        # Пометки отменённых сессий для фильтрации поздних чанков
        self._cancelled_sessions: set = set()

    async def initialize(self) -> bool:
        try:
            # Ленивая инициализация плеера с централизованной конфигурацией
            pc = PlayerConfig(
                sample_rate=self.config['sample_rate'],
                channels=self.config['channels'],
                dtype=self.config['dtype'],
                buffer_size=self.config['buffer_size'],
                max_memory_mb=self.config['max_memory_mb'],
                auto_device_selection=self.config['auto_device_selection'],
            )
            self._player = SequentialSpeechPlayer(pc)
            # Коллбек завершения воспроизведения — сигнализируем в EventBus
            try:
                self._player.set_callbacks(on_playback_completed=self._on_player_completed)
            except Exception:
                pass

            # Подписки
            await self.event_bus.subscribe("grpc.response.audio", self._on_audio_chunk, EventPriority.HIGH)
            await self.event_bus.subscribe("grpc.request_completed", self._on_grpc_completed, EventPriority.HIGH)
            await self.event_bus.subscribe("grpc.request_failed", self._on_grpc_failed, EventPriority.HIGH)
            # Сигналы (короткие тоны) через EventBus
            await self.event_bus.subscribe("playback.signal", self._on_playback_signal, EventPriority.HIGH)
            
            # ЕДИНЫЙ канал прерываний - только playback.cancelled
            await self.event_bus.subscribe("playback.cancelled", self._on_unified_interrupt, EventPriority.CRITICAL)
            
            # Устаревшие прямые прерывания (для обратной совместимости, но перенаправляем в единый канал)
            # УБРАНО: keyboard.short_press - прерывания только при переходе в LISTENING
            # УБРАНО: interrupt.request - обрабатывается централизованно в InterruptManagementIntegration
            await self.event_bus.subscribe("app.shutdown", self._on_app_shutdown, EventPriority.HIGH)
            # Реагируем на смену выходного устройства
            try:
                await self.event_bus.subscribe("audio.device_switched", self._on_audio_device_switched, EventPriority.MEDIUM)
            except Exception:
                pass

            self._initialized = True
            logger.info("SpeechPlaybackIntegration initialized")
            return True
        except Exception as e:
            await self._handle_error(e, where="speech.initialize")
            return False

    async def start(self) -> bool:
        if not self._initialized:
            logger.error("SpeechPlaybackIntegration not initialized")
            return False
        self._running = True
        return True

    async def stop(self) -> bool:
        try:
            if self._player:
                try:
                    self._player.stop_playback()
                    self._player.shutdown()
                except Exception:
                    pass
            self._running = False
            return True
        except Exception as e:
            await self._handle_error(e, where="speech.stop", severity="warning")
            return False

    # -------- Event Handlers --------
    async def _on_audio_chunk(self, event):
        try:
            data = (event or {}).get("data", {})
            sid = data.get("session_id")
            # Фильтрация поздних чанков после отмены
            if sid is not None and (sid in self._cancelled_sessions):
                logger.debug(f"Ignoring audio chunk for cancelled sid={sid}")
                return
            if sid is not None:
                self._current_session_id = sid
            audio_bytes: bytes = data.get("bytes") or b""
            dtype: str = (data.get("dtype") or 'int16').lower()
            shape = data.get("shape") or []
            src_sample_rate: Optional[int] = data.get("sample_rate")
            src_channels: Optional[int] = data.get("channels")
            if not audio_bytes:
                return

            # Инициализация плеера при первом чанке
            if self._player and not self._player.state_manager.is_playing and not self._player.state_manager.is_paused:
                if not self._player.initialize():
                    await self._handle_error(Exception("player_init_failed"), where="speech.player_init")
                    return

            # Декодирование в numpy + диагностика формата
            try:
                # Определяем dtype с учётом возможной эндИанности
                dt: Any
                if dtype in ('float32', 'float'):
                    dt = np.float32
                elif dtype in ('int16_be', 'pcm_s16be'):
                    dt = np.dtype('>i2')
                elif dtype in ('int16_le', 'pcm_s16le'):
                    dt = np.dtype('<i2')
                elif dtype in ('int16', 'short'):
                    # По умолчанию считаем little-endian, но проверим byteswap эвристикой
                    dt = np.dtype('<i2')
                else:
                    dt = np.dtype('<i2')

                arr = np.frombuffer(audio_bytes, dtype=dt)
                # Если тип int16 без явной эндИанности — эвристика byteswap по пику сигнала
                try:
                    if dt.kind == 'i' and dt.itemsize == 2 and dtype in ('int16', 'short'):
                        peak = float(np.max(np.abs(arr))) if arr.size else 0.0
                        swapped = arr.byteswap().newbyteorder()
                        peak_sw = float(np.max(np.abs(swapped))) if swapped.size else 0.0
                        if peak_sw > peak * 1.8:
                            arr = swapped
                except Exception:
                    pass
                if shape and len(shape) > 0:
                    try:
                        arr = arr.reshape(shape)
                    except Exception:
                        pass
                # Приводим dtype к int16 при поступлении float32 (если выбран int16 вывод)
                if arr.dtype == np.float32:
                    scaled = np.clip(arr, -1.0, 1.0) * 32767.0
                    arr = scaled.astype(np.int16)
                # Если уже int16 - оставляем как есть (убираем лишние конвертации)
                # Прочее приведение формата (ресемплинг/каналы) выполняет плеер на основе metadata

                # Диагностика: логируем основы формата (без спамма)
                try:
                    _min = float(arr.min()) if arr.size else 0.0
                    _max = float(arr.max()) if arr.size else 0.0
                    logger.info(f"🔍 audio_chunk: sid={sid}, dtype={arr.dtype}, shape={getattr(arr,'shape',())}, min={_min:.3f}, max={_max:.3f}, bytes={len(audio_bytes)}")
                except Exception:
                    pass
            except Exception as e:
                await self._handle_error(e, where="speech.decode_audio", severity="warning")
                return

            # Добавляем чанк и запускаем/возобновляем воспроизведение
            try:
                if self._player:
                    self._player.add_audio_data(
                        arr,
                        priority=0,
                        metadata={
                            "session_id": sid,
                            "sample_rate": src_sample_rate,
                            "channels": src_channels,
                        },
                    )
                    # Определяем текущее состояние плеера и корректно управляем
                    state = self._player.state_manager.get_state()
                    if state == PlaybackState.PAUSED:
                        # Если пауза — резюмируем
                        self._player.resume_playback()
                    elif state != PlaybackState.PLAYING:
                        # IDLE/ERROR/STOPPING — пытаемся запустить воспроизведение
                        # Повторная/идемпотентная инициализация безопасна
                        if not self._player.initialize():
                            await self._handle_error(Exception("player_init_failed"), where="speech.player_init")
                            return
                        if not self._player.start_playback():
                            await self._handle_error(Exception("start_failed"), where="speech.start_playback")
                            return
                        await self.event_bus.publish("playback.started", {"session_id": sid})
                self._had_audio_for_session[sid] = True

                # Обновляем метку времени последнего аудио и запускаем таймер тишины
                try:
                    self._last_audio_ts = asyncio.get_event_loop().time()
                    if self._silence_task and not self._silence_task.done():
                        self._silence_task.cancel()
                    self._silence_task = asyncio.create_task(self._finalize_on_silence(sid, timeout=1.0))
                except Exception:
                    pass
            except Exception as e:
                await self._handle_error(e, where="speech.add_chunk")

        except Exception as e:
            await self._handle_error(e, where="speech.on_audio_chunk", severity="warning")

    async def _on_audio_device_switched(self, event):
        """Мягкое перестроение числа каналов при смене устройства вывода"""
        try:
            if not self._player:
                return
            # Опрашиваем лучшее устройство и его каналы
            try:
                from modules.speech_playback.utils.device_utils import get_best_audio_device
                dev = get_best_audio_device()
                if not dev:
                    return
                target_ch = 1 if getattr(dev, 'channels', 1) <= 1 else 2
            except Exception:
                return
            # Переинициализируем вывод, если число каналов изменилось
            try:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, self._player.reconfigure_channels, target_ch)
            except Exception:
                pass
        except Exception as e:
            await self._handle_error(e, where="speech.on_device_switched", severity="warning")

    async def _on_grpc_completed(self, event):
        try:
            data = (event or {}).get("data", {})
            sid = data.get("session_id")
            if sid is not None:
                self._grpc_done_sessions[sid] = True
            # Даем плееру доиграть буфер асинхронно
            async def _drain_and_stop():
                try:
                    if self._player:
                        # ожидаем опустошения буфера в отдельном потоке
                        loop = asyncio.get_running_loop()
                        await loop.run_in_executor(None, self._player.wait_for_completion)
                        # Небольшая задержка для дренажа устройства вывода
                        try:
                            drain_sec = max(0.05, min(0.25, (self.config['buffer_size'] / self.config['sample_rate']) * 4.0))
                            await asyncio.sleep(drain_sec)
                        except Exception:
                            pass
                        # Корректно останавливаем поток воспроизведения
                        self._player.stop_playback()
                    await self.event_bus.publish("playback.completed", {"session_id": sid})
                    self._finalized_sessions[sid] = True
                    # Возвращаем приложение в SLEEPING централизованно
                    try:
                        await self.event_bus.publish("mode.request", {
                            "target": AppMode.SLEEPING,
                            "source": "speech_playback"
                        })
                    except Exception:
                        pass
                except Exception as e:
                    await self._handle_error(e, where="speech.drain_stop", severity="warning")
            asyncio.create_task(_drain_and_stop())
        except Exception as e:
            await self._handle_error(e, where="speech.on_grpc_completed", severity="warning")

    async def _on_grpc_failed(self, event):
        try:
            data = (event or {}).get("data", {})
            sid = data.get("session_id")
            err = (data.get("error") or "").lower()
            if sid is not None:
                self._grpc_done_sessions[sid] = True
                if err == 'cancelled':
                    self._cancelled_sessions.add(sid)
            if self._player:
                try:
                    self._player.stop_playback()
                except Exception:
                    pass
            await self.event_bus.publish("playback.failed", {"session_id": sid, "error": data.get("error")})
            self._finalized_sessions[sid] = True
            # Возврат в SLEEPING не инициируем, если ошибка — отмена (cancelled)
            if err != 'cancelled':
                try:
                    await self.event_bus.publish("mode.request", {
                        "target": AppMode.SLEEPING,
                        "source": "speech_playback"
                    })
                except Exception:
                    pass
        except Exception as e:
            await self._handle_error(e, where="speech.on_grpc_failed", severity="warning")

    async def _on_unified_interrupt(self, event):
        """ЕДИНЫЙ обработчик прерывания воспроизведения"""
        try:
            data = event.get("data", {})
            source = data.get("source", "unknown")
            reason = data.get("reason", "interrupt")
            
            logger.info(f"SpeechPlayback: ЕДИНЫЙ канал прерывания, source={source}, reason={reason}")
            
            # Помечаем текущую сессию как отменённую (если есть)
            if self._current_session_id is not None:
                self._cancelled_sessions.add(self._current_session_id)
                
            # Отменяем таймер тишины, если активен
            try:
                if self._silence_task and not self._silence_task.done():
                    self._silence_task.cancel()
            except Exception:
                pass
            
            # Останавливаем воспроизведение
            if self._player:
                self._player.stop_playback()
            
            # Очищаем все сессии
            self._finalized_sessions.clear()
            
            logger.info("SpeechPlayback: прерывание обработано через ЕДИНЫЙ канал")
            
        except Exception as e:
            await self._handle_error(e, where="speech.on_unified_interrupt", severity="warning")
    
    async def _on_legacy_interrupt(self, event):
        """Обработчик устаревших прерываний (перенаправляет в единый канал)"""
        try:
            event_type = event.get("type", "unknown")
            data = event.get("data", {})
            
            logger.info(f"SpeechPlayback: получено устаревшее прерывание {event_type}, перенаправляем в ЕДИНЫЙ канал")
            
            # Перенаправляем в единый канал прерывания
            await self.event_bus.publish("playback.cancelled", {
                "session_id": data.get("session_id"),
                "reason": "legacy_interrupt",
                "source": f"legacy_{event_type}",
                "original_event": event_type
            })
            
        except Exception as e:
            await self._handle_error(e, where="speech.on_legacy_interrupt", severity="warning")

    async def _on_app_shutdown(self, event):
        await self.stop()

    async def _on_playback_signal(self, event: Dict[str, Any]):
        """Приём коротких сигналов (PCM s16le mono) для немедленного воспроизведения."""
        try:
            if not self._player:
                return
            data = (event or {}).get("data", {})
            pcm = data.get("pcm")
            if not pcm:
                return
            sr = int(data.get("sample_rate", 0))
            ch = int(data.get("channels", 1))
            gain = float(data.get("gain", 1.0))
            priority = int(data.get("priority", 10))
            pattern = data.get("pattern")

            logger.info(f"🔔 playback.signal: pattern={pattern}, bytes={len(pcm)}, sr={sr}, ch={ch}, gain={gain}, prio={priority}")

            # Проверяем sample rate — должен совпадать с плеером
            target_sr = int(self.config['sample_rate'])
            if sr != target_sr:
                logger.debug(f"Signal SR mismatch: got={sr}, player={target_sr} — skipping")
                return

            # Декодируем PCM s16le mono
            try:
                arr = np.frombuffer(pcm, dtype=np.int16)
            except Exception:
                return

            # Применяем gain (осторожно с переполнением)
            try:
                if gain != 1.0:
                    a = arr.astype(np.float32) * max(0.0, min(1.0, gain))
                    a = np.clip(a, -32768.0, 32767.0).astype(np.int16)
                else:
                    a = arr
            except Exception:
                a = arr

            # Добавляем данные и при необходимости запускаем воспроизведение
            try:
                meta = {"kind": "signal", "pattern": pattern}
                self._player.add_audio_data(a, priority=priority, metadata=meta)
                state = self._player.state_manager.get_state()
                if state == PlaybackState.PAUSED:
                    self._player.resume_playback()
                elif state != PlaybackState.PLAYING:
                    if not self._player.initialize():
                        await self._handle_error(Exception("player_init_failed"), where="speech.signal.player_init")
                        return
                    if not self._player.start_playback():
                        await self._handle_error(Exception("start_failed"), where="speech.signal.start_playback")
                        return
                    await self.event_bus.publish("playback.started", {"signal": True})
            except Exception as e:
                await self._handle_error(e, where="speech.signal.add_chunk")
        except Exception as e:
            await self._handle_error(e, where="speech.on_playback_signal", severity="warning")

    # -------- Utils --------
    async def _finalize_on_silence(self, sid, timeout: float = 1.5):
        """Фолбэк: если после последнего чанка наступила тишина и плеер остановился — завершаем PROCESSING."""
        try:
            start = self._last_audio_ts
            await asyncio.sleep(timeout)
            # Если не было новых чанков
            if self._last_audio_ts == start and self._player:
                # Если буфер пуст — завершаем воспроизведение и сессию
                buf_empty = (getattr(self._player, 'chunk_buffer', None) and self._player.chunk_buffer.is_empty)
                # Финализируем ТОЛЬКО если сервер закончил поток (grpc_done), буфер пуст, и сессия ещё не финализирована
                if self._grpc_done_sessions.get(sid) and buf_empty and not self._finalized_sessions.get(sid):
                    # Небольшая задержка для дренажа устройства
                    try:
                        drain_sec = max(0.05, min(0.25, (self.config['buffer_size'] / self.config['sample_rate']) * 4.0))
                        await asyncio.sleep(drain_sec)
                    except Exception:
                        pass
                    # Корректно останавливаем воспроизведение и завершаем
                    try:
                        if self._player:
                            self._player.stop_playback()
                    except Exception:
                        pass
                    await self.event_bus.publish("playback.completed", {"session_id": sid})
                    self._finalized_sessions[sid] = True
                    try:
                        await self.event_bus.publish("mode.request", {
                            "target": AppMode.SLEEPING,
                            "source": "speech_playback"
                        })
                    except Exception:
                        pass
        except asyncio.CancelledError:
            return
        except Exception:
            # Тихо игнорируем ошибки фолбэка
            pass

    def _on_player_completed(self):
        """Коллбек плеера: воспроизведение завершено (буфер пуст, поток завершён)."""
        try:
            sid = self._current_session_id
            if sid is None:
                return
            # Завершаем только если сервер завершил поток и мы еще не финализировали
            if self._grpc_done_sessions.get(sid) and not self._finalized_sessions.get(sid):
                loop = asyncio.get_event_loop()
                # На всякий случай — остановим воспроизведение, если ещё не остановлено
                try:
                    if self._player:
                        self._player.stop_playback()
                except Exception:
                    pass
                loop.create_task(self.event_bus.publish("playback.completed", {"session_id": sid}))
                self._finalized_sessions[sid] = True
                loop.create_task(self.event_bus.publish("mode.request", {
                    "target": AppMode.SLEEPING,
                    "source": "speech_playback"
                }))
        except Exception:
            pass
    async def _handle_error(self, e: Exception, *, where: str, severity: str = "error"):
        if hasattr(self.error_handler, 'handle'):
            await self.error_handler.handle(
                error=e,
                category="speech_playback",
                severity=severity,
                context={"where": where}
            )
        else:
            logger.error(f"Speech playback error at {where}: {e}")

    def get_status(self) -> Dict[str, Any]:
        return {
            "initialized": self._initialized,
            "running": self._running,
            "player": (self._player.get_status() if self._player else {}),
        }
