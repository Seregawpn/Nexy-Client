#!/usr/bin/env python3
"""
Новый gRPC сервер с интеграцией всех модулей
Заменяет старый grpc_server.py с полной поддержкой модульной архитектуры
"""

import asyncio
import logging
import grpc.aio
from concurrent.futures import ThreadPoolExecutor
import sys
import os
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, AsyncGenerator

# Добавляем корневую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Protobuf файлы генерируются автоматически из streaming.proto
import streaming_pb2
import streaming_pb2_grpc

# Импорт новых модулей
from modules.grpc_service.core.grpc_service_manager import GrpcServiceManager

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
        """Обработка StreamRequest через новые модули"""
        session_id = request.session_id or f"session_{datetime.now().timestamp()}"
        hardware_id = request.hardware_id or "unknown"
        
        logger.info(f"📨 Получен StreamRequest: session={session_id}, hardware_id={hardware_id}")
        logger.info(f"📨 StreamRequest данные: prompt_len={len(request.prompt)}, screenshot_len={len(request.screenshot) if request.screenshot else 0}")
        
        try:
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
            
            response = streaming_pb2.StreamResponse(
                error_message=f"Внутренняя ошибка сервера: {str(e)}"
            )
            yield response
    
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

async def run_server(port: int = 50051, max_workers: int = 10):
    """Запуск нового gRPC сервера"""
    logger.info(f"🚀 Запуск нового gRPC сервера на порту {port}")
    
    # Создаем сервер
    server = grpc.aio.server(ThreadPoolExecutor(max_workers=max_workers))
    
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
    
    logger.info(f"✅ Новый сервер настроен на {listen_addr}")
    
    try:
        # Запускаем сервер
        await server.start()
        logger.info(f"🎉 Новый gRPC сервер запущен на порту {port}")
        
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
        logger.info("✅ Новый сервер остановлен")

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
