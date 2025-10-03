#!/usr/bin/env python3
"""
Новый gRPC сервер с интеграцией всех модулей
Заменяет старый grpc_server.py с полной поддержкой модульной архитектуры
"""

import asyncio
import logging
import grpc.aio
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import time
from datetime import datetime
from typing import Dict, Any, Optional, AsyncGenerator

# Protobuf файлы генерируются автоматически из streaming.proto
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import streaming_pb2
import streaming_pb2_grpc

# Импорт новых модулей
from .grpc_service_manager import GrpcServiceManager

# Импорты мониторинга (относительные пути)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from monitoring import record_request, set_active_connections, get_metrics, get_status

# Логирование настроено в main.py
logger = logging.getLogger(__name__)

def _get_dtype_string(dtype) -> str:
    """Правильно преобразует numpy dtype в строку для protobuf"""
    if hasattr(dtype, 'name'):
        return dtype.name  # np.int16 -> 'int16'
    dtype_str = str(dtype)
    if dtype_str == '<i2':
        return 'int16'
    elif dtype_str == '<f4':
        return 'float32'
    elif dtype_str == '<f8':
        return 'float64'
    return dtype_str

class NewStreamingServicer(streaming_pb2_grpc.StreamingServiceServicer):
    """Новый gRPC сервис с интеграцией всех модулей"""
    
    def __init__(self):
        logger.info("🚀 Инициализация нового gRPC сервера с модулями...")
        
        # Инициализируем менеджеры модулей
        self.grpc_service_manager = GrpcServiceManager()
        self.interrupt_manager = None
        
        # Флаг инициализации
        self.is_initialized = False
        
        logger.info("✅ Новый gRPC сервер создан")
    
    async def initialize(self):
        """Инициализация всех модулей"""
        if self.is_initialized:
            logger.info("⚠️ Сервер уже инициализирован")
            return True
        
        try:
            logger.info("🔧 Инициализация модулей...")
            
            # Инициализируем gRPC Service Manager
            await self.grpc_service_manager.initialize()
            logger.info("✅ gRPC Service Manager инициализирован")
            
            # Используем Interrupt Manager из gRPC Service Manager
            self.interrupt_manager = self.grpc_service_manager.modules.get('interrupt_handling')
            if not self.interrupt_manager:
                raise RuntimeError("Interrupt Manager module not found in GrpcServiceManager")
            logger.info("✅ Interrupt Manager подключен к gRPC сервису")
            
            # Запускаем все модули
            await self.grpc_service_manager.start()
            logger.info("✅ Все модули запущены")
            
            self.is_initialized = True
            logger.info("🎉 Новый gRPC сервер полностью инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации нового сервера: {e}")
            return False
    
    async def cleanup(self):
        """Очистка всех ресурсов"""
        try:
            logger.info("🧹 Очистка ресурсов нового сервера...")
            
            if self.is_initialized:
                # Останавливаем все модули
                await self.grpc_service_manager.stop()
                logger.info("✅ Все модули остановлены")

                # Очищаем gRPC Service Manager
                await self.grpc_service_manager.cleanup()
                logger.info("✅ gRPC Service Manager очищен")
            
            self.is_initialized = False
            self.interrupt_manager = None
            logger.info("✅ Новый сервер полностью очищен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки нового сервера: {e}")
    
    async def StreamAudio(self, request: streaming_pb2.StreamRequest, context) -> AsyncGenerator[streaming_pb2.StreamResponse, None]:
        """Обработка StreamRequest через новые модули с мониторингом"""
        start_time = time.time()
        session_id = request.session_id or f"session_{datetime.now().timestamp()}"
        hardware_id = request.hardware_id or "unknown"
        
        logger.info(f"📨 Получен StreamRequest: session={session_id}, hardware_id={hardware_id}")
        logger.info(f"📨 StreamRequest данные: prompt_len={len(request.prompt)}, screenshot_len={len(request.screenshot) if request.screenshot else 0}")
        
        try:
            # Увеличиваем счетчик активных соединений
            current_connections = get_metrics().get('active_connections', 0)
            set_active_connections(current_connections + 1)
            # В новом protobuf нет interrupt_flag в StreamRequest
            # Прерывания обрабатываются через отдельный InterruptSession API
            
            if not self.interrupt_manager:
                logger.error("Interrupt Manager недоступен, запрос отклонён")
                yield streaming_pb2.StreamResponse(error_message="Interrupt manager unavailable")
                return

            # Проверяем глобальный флаг прерывания
            if self.interrupt_manager.should_interrupt(hardware_id):
                logger.info(f"🛑 Глобальное прерывание активно для {hardware_id}, отклоняем запрос {session_id}")
                
                response = streaming_pb2.StreamResponse(
                    error_message="Глобальное прерывание активно"
                )
                yield response
                return
            
            # Обрабатываем запрос через gRPC Service Manager
            logger.info(f"🔄 Обработка запроса через модули...")
            
            # Подготавливаем данные для обработки
            request_data = {
                'hardware_id': hardware_id,
                'text': request.prompt,
                'screenshot': request.screenshot,
                'session_id': session_id,
                'interrupt_flag': False  # В новом protobuf нет interrupt_flag в StreamRequest
            }
            logger.info(f"🔄 Request data подготовлен: text='{request.prompt[:50]}...', screenshot_exists={bool(request.screenshot)}")
            
            # Потоковая обработка: передаём результаты по мере готовности
            sent_any = False
            logger.info(f"🔄 Начинаем потоковую обработку для {session_id}")
            async for item in self.grpc_service_manager.process(request_data):
                logger.info(f"🔄 Получен item от grpc_service_manager: {list(item.keys())}")
                success = item.get('success', False)
                if not success:
                    err = item.get('error') or 'Ошибка обработки запроса'
                    logger.error(f"❌ Ошибка обработки запроса {session_id}: {err}")
                    yield streaming_pb2.StreamResponse(error_message=err)
                    return
                # Текст
                txt = item.get('text_response')
                if txt:
                    logger.info(f"→ StreamAudio: sending text_chunk len={len(txt)} for session={session_id}")
                    yield streaming_pb2.StreamResponse(text_chunk=txt)
                    sent_any = True
                # Одиночный аудио-чанк
                ch = item.get('audio_chunk')
                if isinstance(ch, (bytes, bytearray)) and len(ch) > 0:
                    logger.info(f"→ StreamAudio: sending audio_chunk bytes={len(ch)} for session={session_id}")
                    yield streaming_pb2.StreamResponse(
                        audio_chunk=streaming_pb2.AudioChunk(audio_data=ch, dtype='int16', shape=[])
                    )
                    sent_any = True
                # Список аудио-чанков (на случай, если интеграция вернёт массив)
                for idx, chunk_data in enumerate(item.get('audio_chunks') or []):
                    if chunk_data:
                        logger.info(f"→ StreamAudio: sending audio_chunk[{idx}] bytes={len(chunk_data)} for session={session_id}")
                        yield streaming_pb2.StreamResponse(
                            audio_chunk=streaming_pb2.AudioChunk(audio_data=chunk_data, dtype='int16', shape=[])
                        )
                        sent_any = True
            # Завершение стрима
            logger.info(f"→ StreamAudio: end_message for session={session_id} (sent_any={sent_any})")
            yield streaming_pb2.StreamResponse(end_message="Обработка завершена")
        except Exception as e:
            logger.error(f"💥 Критическая ошибка в StreamRequest: {e}")
            import traceback
            traceback.print_exc()
            
            # Записываем ошибку в метрики
            record_request(time.time() - start_time, is_error=True)
            
            response = streaming_pb2.StreamResponse(
                error_message=f"Внутренняя ошибка сервера: {str(e)}"
            )
            yield response
        finally:
            # Уменьшаем счетчик активных соединений
            current_connections = get_metrics().get('active_connections', 0)
            set_active_connections(max(0, current_connections - 1))
            
            # Записываем метрику запроса
            response_time = time.time() - start_time
            record_request(response_time, is_error=False)

    async def GenerateWelcomeAudio(self, request: streaming_pb2.WelcomeRequest, context) -> AsyncGenerator[streaming_pb2.WelcomeResponse, None]:
        """Генерация приветственного аудио через AudioProcessor"""
        start_time = time.time()
        session_id = request.session_id or f"welcome_{datetime.now().timestamp()}"
        text = (request.text or "").strip()

        if not text:
            logger.error("❌ GenerateWelcomeAudio: пустой текст приветствия")
            record_request(0.0, is_error=True)
            yield streaming_pb2.WelcomeResponse(error_message="Empty welcome text")
            return

        logger.info(
            "📨 GenerateWelcomeAudio: session=%s, text_len=%s, voice=%s, language=%s",
            session_id,
            len(text),
            request.voice or "default",
            request.language or "default",
        )

        try:
            if not self.is_initialized:
                init_ok = await self.initialize()
                if not init_ok:
                    logger.error("❌ GenerateWelcomeAudio: failed to initialize server modules")
                    record_request(time.time() - start_time, is_error=True)
                    yield streaming_pb2.WelcomeResponse(error_message="Server is not initialized")
                    return

            audio_processor = self.grpc_service_manager.modules.get('audio_generation') if self.grpc_service_manager else None
            if not audio_processor:
                logger.error("❌ GenerateWelcomeAudio: audio_generation module not available")
                record_request(time.time() - start_time, is_error=True)
                yield streaming_pb2.WelcomeResponse(error_message="Audio processor unavailable")
                return

            if not getattr(audio_processor, 'is_initialized', False):
                logger.info("🔄 GenerateWelcomeAudio: initializing audio processor on demand")
                if hasattr(audio_processor, 'initialize'):
                    init_ok = await audio_processor.initialize()
                    if not init_ok:
                        record_request(time.time() - start_time, is_error=True)
                        yield streaming_pb2.WelcomeResponse(error_message="Failed to initialize audio processor")
                        return

            audio_info = {}
            if hasattr(audio_processor, 'get_audio_info'):
                try:
                    audio_info = audio_processor.get_audio_info() or {}
                except Exception as info_err:
                    logger.warning(f"⚠️ GenerateWelcomeAudio: failed to get audio info: {info_err}")

            sample_rate = int(audio_info.get('sample_rate') or 48000)
            channels = int(audio_info.get('channels') or 1)
            dtype = 'int16'
            bytes_per_sample = max(1, int(audio_info.get('bits_per_sample') or 16) // 8)
            bytes_per_frame = bytes_per_sample * max(1, channels)

            total_bytes = 0

            # Генерируем аудио чанки
            logger.info("🎵 GenerateWelcomeAudio: start streaming TTS")
            generator = None
            if hasattr(audio_processor, 'generate_speech_streaming'):
                logger.info("🔍 GenerateWelcomeAudio: using generate_speech_streaming")
                generator = audio_processor.generate_speech_streaming(text)
            elif hasattr(audio_processor, 'generate_speech'):
                logger.info("🔍 GenerateWelcomeAudio: using generate_speech")
                generator = audio_processor.generate_speech(text)

            if generator is None:
                logger.error("❌ GenerateWelcomeAudio: audio processor does not provide streaming interface")
                yield streaming_pb2.WelcomeResponse(error_message="Audio processor streaming not available")
                return
            
            logger.info(f"🔍 GenerateWelcomeAudio: generator created, type={type(generator)}")

            async for chunk in generator:
                logger.info(f"🔍 GenerateWelcomeAudio: received chunk type={type(chunk)}, len={len(chunk) if chunk else 0}")
                if not chunk:
                    logger.warning("⚠️ GenerateWelcomeAudio: empty chunk received, skipping")
                    continue
                chunk_bytes = bytes(chunk)
                logger.info(f"🔍 GenerateWelcomeAudio: chunk_bytes len={len(chunk_bytes)}")
                total_bytes += len(chunk_bytes)
                yield streaming_pb2.WelcomeResponse(
                    audio_chunk=streaming_pb2.AudioChunk(
                        audio_data=chunk_bytes,
                        dtype=dtype,
                        shape=[],
                    )
                )

            duration_sec = 0.0
            if total_bytes and bytes_per_frame:
                duration_sec = total_bytes / (bytes_per_frame * float(sample_rate))

            metadata = streaming_pb2.WelcomeMetadata(
                method="server",
                duration_sec=duration_sec,
                sample_rate=sample_rate,
                channels=channels,
            )
            yield streaming_pb2.WelcomeResponse(metadata=metadata)
            yield streaming_pb2.WelcomeResponse(end_message="Welcome audio generation completed")

            response_time = time.time() - start_time
            record_request(response_time, is_error=False)

        except Exception as e:
            logger.error(f"❌ GenerateWelcomeAudio: ошибка генерации приветствия: {e}")
            import traceback
            traceback.print_exc()
            record_request(time.time() - start_time, is_error=True)
            yield streaming_pb2.WelcomeResponse(error_message=f"Failed to generate welcome audio: {e}")


    async def InterruptSession(self, request: streaming_pb2.InterruptRequest, context) -> streaming_pb2.InterruptResponse:
        """Обработка InterruptRequest через Interrupt Manager"""
        hardware_id = request.hardware_id or "unknown"
        # В InterruptRequest нет session_id, только hardware_id
        
        logger.info(f"🛑 Получен InterruptRequest: hardware_id={hardware_id}")
        
        try:
            if not self.interrupt_manager:
                logger.error("Interrupt Manager недоступен, прерывание невозможно")
                return streaming_pb2.InterruptResponse(
                    success=False,
                    message="Interrupt manager unavailable",
                    interrupted_sessions=[]
                )

            # Используем Interrupt Manager для обработки прерывания
            interrupt_result = await self.interrupt_manager.interrupt_session(
                hardware_id=hardware_id
            )
            
            if interrupt_result.get('success', False):
                logger.info(f"✅ Прерывание успешно обработано для {hardware_id}")
                
                return streaming_pb2.InterruptResponse(
                    success=True,
                    message="Сессии успешно прерваны",
                    interrupted_sessions=interrupt_result.get('cleaned_sessions', [])
                )
            else:
                logger.warning(f"⚠️ Не удалось обработать прерывание для {hardware_id}")
                
                return streaming_pb2.InterruptResponse(
                    success=False,
                    message=interrupt_result.get('message', 'Не удалось прервать сессии'),
                    interrupted_sessions=[]
                )
        
        except Exception as e:
            logger.error(f"💥 Ошибка в InterruptRequest: {e}")
            import traceback
            traceback.print_exc()
            
            return streaming_pb2.InterruptResponse(
                success=False,
                message=f"Ошибка обработки прерывания: {str(e)}",
                interrupted_sessions=[]
            )

async def run_server(port: int = 50051, max_workers: int = 100):
    """Запуск оптимизированного gRPC сервера для 100 пользователей"""
    logger.info(f"🚀 Запуск оптимизированного gRPC сервера на порту {port} с {max_workers} воркерами")
    
    # Оптимизированный ThreadPoolExecutor
    executor = ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix="grpc-worker"
    )
    
    # Настройки для высокой нагрузки
    options = [
        # Keep-alive настройки
        ('grpc.keepalive_time_ms', 30000),
        ('grpc.keepalive_timeout_ms', 5000),
        ('grpc.keepalive_permit_without_calls', True),
        
        # HTTP/2 настройки
        ('grpc.http2.max_pings_without_data', 0),
        ('grpc.http2.min_time_between_pings_ms', 10000),
        ('grpc.http2.min_ping_interval_without_data_ms', 300000),
        
        # Буферы
        ('grpc.max_receive_message_length', 4 * 1024 * 1024),  # 4MB
        ('grpc.max_send_message_length', 4 * 1024 * 1024),     # 4MB
        
        # Таймауты
        ('grpc.client_idle_timeout_ms', 300000),  # 5 минут
    ]
    
    # Создаем сервер с оптимизированными настройками
    server = grpc.aio.server(executor, options=options)
    
    # Создаем сервис
    servicer = NewStreamingServicer()
    
    # Инициализируем сервис
    init_success = await servicer.initialize()
    if not init_success:
        logger.error("❌ Не удалось инициализировать сервис")
        return False
    
    # Добавляем сервис на сервер
    streaming_pb2_grpc.add_StreamingServiceServicer_to_server(servicer, server)
    
    # Настраиваем порт
    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"✅ Оптимизированный сервер настроен на {listen_addr}")
    logger.info(f"📊 Настройки производительности:")
    logger.info(f"   - Воркеры: {max_workers}")
    logger.info(f"   - Keep-alive: 30s")
    logger.info(f"   - Буферы: 4MB")
    logger.info(f"   - Таймаут клиента: 5 минут")
    
    try:
        # Запускаем сервер
        await server.start()
        logger.info(f"🎉 Оптимизированный gRPC сервер запущен на порту {port}")
        
        # Ждем завершения
        await server.wait_for_termination()
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"💥 Ошибка запуска сервера: {e}")
    finally:
        # Очищаем ресурсы
        logger.info("🧹 Остановка сервера...")
        await servicer.cleanup()
        
        # Graceful shutdown
        await server.stop(grace=5.0)
        logger.info("✅ Оптимизированный сервер остановлен")

async def main():
    """Основная функция"""
    try:
        await run_server()
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
