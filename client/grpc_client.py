import asyncio
import logging
import numpy as np
import grpc
import sys
import os
import time

# Добавляем корневую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streaming_pb2
import streaming_pb2_grpc
from audio_player import AudioPlayer
from rich.console import Console

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

console = Console()

class GrpcClient:
    """gRPC клиент для стриминга аудио и текста"""
    
    def __init__(self, server_address: str = "localhost:50051"):
        self.server_address = server_address
        self.audio_player = AudioPlayer(sample_rate=48000)
        self.channel = None
        self.stub = None
    
    async def connect(self):
        """Подключение к gRPC серверу"""
        try:
            # Настройки для больших сообщений (аудио + скриншоты)
            options = [
                ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB
                ('grpc.max_metadata_size', 1024 * 1024),  # 1MB для метаданных
            ]
            
            # Создаем неблокирующий канал с увеличенными лимитами
            self.channel = grpc.aio.insecure_channel(self.server_address, options=options)
            self.stub = streaming_pb2_grpc.StreamingServiceStub(self.channel)
            
            console.print(f"[bold green]✅ Подключение к gRPC серверу {self.server_address} установлено[/bold green]")
            console.print(f"[blue]📏 Максимальный размер сообщения: 50MB[/blue]")
            return True
            
        except Exception as e:
            console.print(f"[bold red]❌ Ошибка подключения к серверу: {e}[/bold red]")
            return False
    
    def connect_sync(self):
        """Синхронное подключение к gRPC серверу (для восстановления соединения)"""
        try:
            # Настройки для больших сообщений (аудио + скриншоты)
            options = [
                ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB
                ('grpc.max_metadata_size', 1024 * 1024),  # 1MB для метаданных
            ]
            
            # Создаем синхронный канал для восстановления с увеличенными лимитами
            import grpc
            self.channel = grpc.insecure_channel(self.server_address, options=options)
            self.stub = streaming_pb2_grpc.StreamingServiceStub(self.channel)
            
            console.print(f"[bold green]✅ Синхронное подключение к gRPC серверу {self.server_address} восстановлено[/bold green]")
            console.print(f"[blue]📏 Максимальный размер сообщения: 50MB[/blue]")
            return True
            
        except Exception as e:
            console.print(f"[bold red]❌ Ошибка синхронного подключения к серверу: {e}[/bold red]")
            return False
    
    async def disconnect(self):
        """Отключение от сервера"""
        if self.channel:
            await self.channel.close()
            console.print("[bold yellow]🔌 Отключено от сервера[/bold yellow]")
    
    def interrupt_stream(self):
        """МГНОВЕННО прерывает активный gRPC стриминг на сервере!"""
        try:
            console.print(f"[bold red]🔍 ДИАГНОСТИКА gRPC: channel={self.channel}, stub={self.stub}[/bold red]")
            
            if self.channel:
                # Проверяем статус канала
                try:
                    is_closed = self.channel.closed()
                    console.print(f"[blue]🔍 Канал закрыт: {is_closed}[/blue]")
                except AttributeError:
                    console.print("[blue]🔍 Метод .closed() недоступен, пробуем другой способ[/blue]")
                    is_closed = False
                
                if not is_closed:
                    # МГНОВЕННО закрываем канал - это принудительно прервет все активные вызовы!
                    console.print("[bold red]🚨 ЗАКРЫВАЮ gRPC канал...[/bold red]")
                    
                    # КРИТИЧНО: channel.close() - это корутина, нужно создать задачу для её выполнения
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Создаем задачу для асинхронного закрытия канала
                        console.print("[blue]🔍 Создаю задачу для закрытия канала...[/blue]")
                        loop.create_task(self._close_channel_and_recreate())
                    else:
                        # Если цикл не запущен, создаем канал напрямую
                        console.print("[blue]🔍 Создаю канал напрямую...[/blue]")
                        self.channel = grpc.aio.insecure_channel(self.server_address)
                        self.stub = streaming_pb2_grpc.StreamingServiceStub(self.channel)
                        console.print("[bold green]✅ Новый gRPC канал создан для следующих вызовов[/bold green]")
                else:
                    console.print("[yellow]⚠️ gRPC канал уже закрыт[/yellow]")
            else:
                console.print("[yellow]⚠️ gRPC канал = None[/yellow]")
        except Exception as e:
            console.print(f"[red]⚠️ Ошибка прерывания gRPC стриминга: {e}[/red]")
            import traceback
            console.print(f"[red]🔍 Traceback: {traceback.format_exc()}[/red]")
    
    def force_interrupt_server(self):
        """ПРИНУДИТЕЛЬНОЕ прерывание на сервере через вызов InterruptSession!"""
        logger.info(f"🚨 force_interrupt_server() вызван в {time.time():.3f}")
        
        try:
            console.print("[bold red]🚨 ПРИНУДИТЕЛЬНОЕ прерывание на СЕРВЕРЕ![/bold red]")
            logger.info("   🚨 ПРИНУДИТЕЛЬНОЕ прерывание на СЕРВЕРЕ!")
            
            # КРИТИЧНО: вызываем новый метод InterruptSession на сервере!
            if self.stub:
                try:
                    # Создаем запрос прерывания
                    interrupt_request = streaming_pb2.InterruptSessionRequest(
                        session_id="force_interrupt",
                        reason="user_interruption"
                    )
                    
                    # Отправляем запрос прерывания
                    console.print("[blue]🔍 Отправляю запрос прерывания на сервер...[/blue]")
                    logger.info("   🔍 Отправляю запрос прерывания на сервер...")
                    
                    # Создаем задачу для асинхронного вызова
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Создаем задачу для асинхронного вызова
                        loop.create_task(self._send_interrupt_request(interrupt_request))
                    else:
                        console.print("[yellow]⚠️ Цикл событий не запущен[/yellow]")
                        
                except Exception as e:
                    console.print(f"[red]❌ Ошибка отправки запроса прерывания: {e}[/red]")
                    logger.error(f"   ❌ Ошибка отправки запроса прерывания: {e}")
            else:
                console.print("[yellow]⚠️ gRPC stub недоступен[/yellow]")
                logger.warning("   ⚠️ gRPC stub недоступен")
                
        except Exception as e:
            console.print(f"[red]❌ Ошибка в force_interrupt_server: {e}[/red]")
            logger.error(f"   ❌ Ошибка в force_interrupt_server: {e}")
    
    async def _send_interrupt_request(self, interrupt_request):
        """Асинхронно отправляет запрос прерывания на сервер"""
        try:
            console.print("[blue]🔍 Асинхронно отправляю запрос прерывания...[/blue]")
            logger.info("   🔍 Асинхронно отправляю запрос прерывания...")
            
            # Вызываем метод InterruptSession
            response = await self.stub.InterruptSession(interrupt_request)
            
            console.print(f"[bold green]✅ Прерывание на сервере успешно! Ответ: {response}[/bold green]")
            logger.info(f"   ✅ Прерывание на сервере успешно! Ответ: {response}")
            
        except Exception as e:
            console.print(f"[red]❌ Ошибка асинхронной отправки прерывания: {e}[/red]")
            logger.error(f"   ❌ Ошибка асинхронной отправки прерывания: {e}")
    
    def close_connection(self):
        """ПРИНУДИТЕЛЬНО закрывает gRPC соединение"""
        logger.info(f"🚨 close_connection() вызван в {time.time():.3f}")
        
        try:
            console.print("[bold red]🚨 ПРИНУДИТЕЛЬНО закрываю gRPC соединение![/bold red]")
            logger.info("   🚨 ПРИНУДИТЕЛЬНО закрываю gRPC соединение!")
            
            # 1️⃣ Закрываем канал
            if self.channel:
                try:
                    # Создаем задачу для асинхронного закрытия
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Создаем задачу для закрытия
                        close_task = loop.create_task(self._force_close_channel())
                        console.print("[blue]🔍 Задача закрытия канала создана[/blue]")
                    else:
                        # Если цикл не запущен, закрываем напрямую
                        self.channel.close()
                        console.print("[bold green]✅ gRPC канал закрыт напрямую[/bold green]")
                except Exception as e:
                    console.print(f"[red]❌ Ошибка закрытия канала: {e}[/red]")
                    logger.error(f"   ❌ Ошибка закрытия канала: {e}")
            
            # 2️⃣ Сбрасываем stub
            self.stub = None
            console.print("[bold green]✅ gRPC stub сброшен[/bold green]")
            
            # 3️⃣ Сбрасываем канал
            self.channel = None
            console.print("[bold green]✅ gRPC канал сброшен[/bold green]")
            
            logger.info("   ✅ gRPC соединение принудительно закрыто")
            
        except Exception as e:
            console.print(f"[red]❌ Ошибка в close_connection: {e}[/red]")
            logger.error(f"   ❌ Ошибка в close_connection: {e}")
    
    async def _force_close_channel(self):
        """Принудительно закрывает gRPC канал"""
        try:
            console.print("[blue]🔍 Принудительно закрываю gRPC канал...[/blue]")
            logger.info("   🔍 Принудительно закрываю gRPC канал...")
            
            # Проверяем, что канал существует
            if self.channel is None:
                console.print("[yellow]⚠️ gRPC канал уже закрыт или не существует[/yellow]")
                logger.info("   ⚠️ gRPC канал уже закрыт или не существует")
                return
            
            # Закрываем канал
            await self.channel.close()
            
            console.print("[bold green]✅ gRPC канал принудительно закрыт[/bold green]")
            logger.info("   ✅ gRPC канал принудительно закрыт")
            
        except Exception as e:
            console.print(f"[red]❌ Ошибка принудительного закрытия канала: {e}[/red]")
            logger.error(f"   ❌ Ошибка принудительного закрытия канала: {e}")
    
    def reset_state(self):
        """Сбрасывает состояние gRPC клиента"""
        logger.info(f"🚨 reset_state() вызван в {time.time():.3f}")
        
        try:
            console.print("[bold blue]🔄 Сбрасываю состояние gRPC клиента...[/bold blue]")
            logger.info("   🔄 Сбрасываю состояние gRPC клиента...")
            
            # 1️⃣ Сбрасываем stub
            self.stub = None
            console.print("[green]✅ gRPC stub сброшен[/green]")
            
            # 2️⃣ Сбрасываем канал
            self.channel = None
            console.print("[green]✅ gRPC канал сброшен[/green]")
            
            # 3️⃣ Сбрасываем аудио плеер
            if self.audio_player:
                try:
                    if hasattr(self.audio_player, 'clear_all_audio_data'):
                        self.audio_player.clear_all_audio_data()
                        console.print("[green]✅ Аудио плеер очищен[/green]")
                    elif hasattr(self.audio_player, 'force_stop'):
                        self.audio_player.force_stop()
                        console.print("[green]✅ Аудио плеер остановлен[/green]")
                except Exception as e:
                    console.print(f"[yellow]⚠️ Ошибка сброса аудио плеера: {e}[/yellow]")
                    logger.warning(f"   ⚠️ Ошибка сброса аудио плеера: {e}")
            
            console.print("[bold green]✅ Состояние gRPC клиента сброшено![/bold green]")
            logger.info("   ✅ Состояние gRPC клиента сброшено!")
            
        except Exception as e:
            console.print(f"[red]❌ Ошибка в reset_state: {e}[/red]")
            logger.error(f"   ❌ Ошибка в reset_state: {e}")
    
    def clear_buffers(self):
        """Очищает все gRPC буферы"""
        logger.info(f"🧹 clear_buffers() вызван в {time.time():.3f}")
        
        try:
            console.print("[bold blue]🧹 Очищаю все gRPC буферы...[/bold blue]")
            logger.info("   🧹 Очищаю все gRPC буферы...")
            
            # 1️⃣ Очищаем буферы канала
            if self.channel and hasattr(self.channel, 'close'):
                try:
                    # Принудительно закрываем канал для очистки буферов
                    # Создаем задачу для асинхронного закрытия
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(self._force_close_channel())
                        console.print("[blue]🔍 Задача очистки gRPC буферов создана[/blue]")
                    else:
                        # Если цикл не запущен, закрываем напрямую
                        self.channel.close()
                        console.print("[bold green]✅ gRPC буферы очищены напрямую[/bold green]")
                except Exception as e:
                    console.print(f"[yellow]⚠️ Ошибка очистки gRPC буферов: {e}[/yellow]")
                    logger.warning(f"   ⚠️ Ошибка очистки gRPC буферов: {e}")
            else:
                console.print("[blue]ℹ️ gRPC канал уже закрыт или не существует[/blue]")
                logger.info("   ℹ️ gRPC канал уже закрыт или не существует")
            
            # 2️⃣ Очищаем буферы stub
            if self.stub:
                self.stub = None
                console.print("[green]✅ gRPC stub буферы очищены[/green]")
            
            # 3️⃣ Очищаем системные буферы
            import gc
            gc.collect()
            console.print("[green]✅ Системные буферы очищены[/green]")
            
            console.print("[bold green]✅ Все gRPC буферы очищены![/bold green]")
            logger.info("   ✅ Все gRPC буферы очищены!")
            
        except Exception as e:
            console.print(f"[red]❌ Ошибка в clear_buffers: {e}[/red]")
            logger.error(f"   ❌ Ошибка в clear_buffers: {e}")
    
    def interrupt_immediately(self):
        """СИНХРОННОЕ мгновенное прерывание - атомарная операция!"""
        try:
            console.print("[bold red]🚨 СИНХРОННОЕ мгновенное прерывание![/bold red]")
            
            # 1. НЕМЕДЛЕННО отменяем текущий вызов
            if hasattr(self, 'current_call') and self.current_call and not self.current_call.done():
                self.current_call.cancel()
                console.print("[bold red]🚨 Текущий gRPC вызов ОТМЕНЕН![/bold red]")
            
            # 2. Создаем НОВЫЙ канал ТОЛЬКО для команды прерывания
            import grpc
            interrupt_channel = grpc.insecure_channel(self.server_address)
            interrupt_stub = streaming_pb2_grpc.StreamingServiceStub(interrupt_channel)
            
            # 3. СИНХРОННО вызываем InterruptSession
            if hasattr(self, 'hardware_id') and self.hardware_id:
                request = streaming_pb2.InterruptRequest(hardware_id=self.hardware_id)
                try:
                    response = interrupt_stub.InterruptSession(request, timeout=0.5)
                    console.print(f"[bold green]✅ Сервер прервал {len(response.interrupted_sessions)} сессий![/bold green]")
                except Exception as e:
                    console.print(f"[red]⚠️ Ошибка вызова InterruptSession: {e}[/red]")
                finally:
                    interrupt_channel.close()
                    console.print("[bold red]🚨 Канал прерывания закрыт![/bold red]")
            else:
                console.print("[yellow]⚠️ Hardware ID недоступен для прерывания[/yellow]")
                
        except Exception as e:
            console.print(f"[red]⚠️ Ошибка синхронного прерывания: {e}[/red]")
            import traceback
            console.print(f"[red]🔍 Traceback: {traceback.format_exc()}[/red]")
    
    async def _force_interrupt_server_call(self):
        """Асинхронно вызывает прерывание на сервере"""
        logger.info(f"🚨 _force_interrupt_server_call() начат в {time.time():.3f}")
        
        try:
            if hasattr(self, 'hardware_id') and self.hardware_id:
                logger.info(f"   🆔 Hardware ID: {self.hardware_id[:20]}...")
                
                # Создаем запрос на прерывание
                request = streaming_pb2.InterruptRequest(hardware_id=self.hardware_id)
                logger.info("   📤 Создан InterruptRequest")
                
                # Вызываем метод на сервере
                logger.info("   🔄 Вызываю stub.InterruptSession...")
                start_time = time.time()
                response = await self.stub.InterruptSession(request)
                call_time = (time.time() - start_time) * 1000
                logger.info(f"   ⏱️ stub.InterruptSession: {call_time:.1f}ms")
                
                if response.success:
                    logger.info(f"   ✅ Сервер успешно прервал {len(response.interrupted_sessions)} сессий")
                    console.print(f"[bold green]✅ Сервер успешно прервал {len(response.interrupted_sessions)} сессий![/bold green]")
                    console.print(f"[bold green]✅ Прерванные сессии: {response.interrupted_sessions}[/bold green]")
                else:
                    logger.warning("   ⚠️ Сервер не нашел активных сессий для прерывания")
                    console.print(f"[yellow]⚠️ Сервер не нашел активных сессий для прерывания[/yellow]")
            else:
                logger.warning("   ⚠️ Hardware ID недоступен для прерывания")
                console.print("[yellow]⚠️ Hardware ID недоступен для прерывания[/yellow]")
        except Exception as e:
            logger.error(f"   ❌ Ошибка вызова прерывания на сервере: {e}")
            console.print(f"[red]⚠️ Ошибка вызова прерывания на сервере: {e}[/red]")
        
        logger.info(f"   🏁 _force_interrupt_server_call завершен в {time.time():.3f}")
    
    def _force_interrupt_server_sync(self):
        """Синхронно вызывает прерывание на сервере (fallback)"""
        try:
            if hasattr(self, 'hardware_id') and self.hardware_id:
                # Создаем запрос на прерывание
                request = streaming_pb2.InterruptRequest(hardware_id=self.hardware_id)
                
                # Вызываем метод на сервере синхронно
                response = self.stub.InterruptSession(request)
                
                if response.success:
                    console.print(f"[bold green]✅ Сервер успешно прервал {len(response.interrupted_sessions)} сессий![/bold green]")
                    console.print(f"[bold green]✅ Прерванные сессии: {response.interrupted_sessions}[/bold green]")
                else:
                    console.print(f"[yellow]⚠️ Сервер не нашел активных сессий для прерывания[/yellow]")
            else:
                console.print("[yellow]⚠️ Hardware ID недоступен для прерывания[/yellow]")
        except Exception as e:
            console.print(f"[red]⚠️ Ошибка вызова прерывания на сервере: {e}[/red]")
    
    async def _force_recreate_channel(self):
        """Принудительно создает новый канал для прерывания старого"""
        try:
            # Сначала закрываем старый канал
            if self.channel:
                try:
                    await self.channel.close()
                    console.print("[bold red]🚨 Старый канал ПРИНУДИТЕЛЬНО закрыт![/bold red]")
                except:
                    pass
            
            # Создаем новый канал
            self.channel = grpc.aio.insecure_channel(self.server_address)
            self.stub = streaming_pb2_grpc.StreamingServiceStub(self.channel)
            console.print("[bold green]✅ Новый gRPC канал создан для принудительного прерывания[/bold green]")
        except Exception as e:
            console.print(f"[red]⚠️ Ошибка принудительного создания канала: {e}[/red]")
    
    async def _close_channel_and_recreate(self):
        """Асинхронно закрывает канал и воссоздает его"""
        try:
            # Асинхронно закрываем канал
            await self.channel.close()
            console.print("[bold red]🚨 МГНОВЕННОЕ прерывание gRPC канала![/bold red]")
            
            # Создаем новый канал
            await self._recreate_channel()
        except Exception as e:
            console.print(f"[red]⚠️ Ошибка закрытия канала: {e}[/red]")
    
    async def _recreate_channel(self):
        """Воссоздает gRPC канал асинхронно"""
        try:
            self.channel = grpc.aio.insecure_channel(self.server_address)
            self.stub = streaming_pb2_grpc.StreamingServiceStub(self.channel)
            console.print("[bold green]✅ Новый gRPC канал создан для следующих вызовов[/bold green]")
        except Exception as e:
            console.print(f"[red]⚠️ Ошибка воссоздания gRPC канала: {e}[/red]")
    
    async def stream_audio(self, prompt: str, screenshot_base64: str = None, screen_info: dict = None, hardware_id: str = None):
        """
        Запускает стриминг аудио и текста.
        Эта функция является асинхронным генератором, который сначала возвращает 
        объект вызова (для возможности отмены), а затем ничего не возвращает, 
        поскольку обработка происходит внутри.
        """
        if not self.stub:
            console.print("[bold red]❌ Не подключен к серверу[/bold red]")
            return
        
        call = None
        try:
            console.print(f"[bold yellow]🚀 Запуск gRPC стриминга для: {prompt}[/bold yellow]")
            
            if screenshot_base64:
                console.print(f"[bold blue]📸 Отправляю скриншот: {screen_info.get('width', 0)}x{screen_info.get('height', 0)} пикселей[/bold blue]")
            
            if hardware_id:
                console.print(f"[bold blue]🆔 Отправляю Hardware ID: {hardware_id[:16]}...[/bold blue]")
            
            self.audio_player.start_playback()
            
            request = streaming_pb2.StreamRequest(
                prompt=prompt,
                screenshot=screenshot_base64 if screenshot_base64 else "",
                screen_width=screen_info.get('width', 0) if screen_info else 0,
                screen_height=screen_info.get('height', 0) if screen_info else 0,
                hardware_id=hardware_id if hardware_id else ""
            )
            
            call = self.stub.StreamAudio(request)
            
            # Сразу возвращаем объект вызова, чтобы main мог его отменить
            yield call
            
            async for response in call:
                if response.HasField('text_chunk'):
                    console.print(f"[green]📄 Текст: {response.text_chunk}[/green]")
                
                elif response.HasField('audio_chunk'):
                    audio_chunk = np.frombuffer(
                        response.audio_chunk.audio_data, 
                        dtype=response.audio_chunk.dtype
                    ).reshape(response.audio_chunk.shape)
                    console.print(f"[blue]🎵 Аудио чанк получен: {len(audio_chunk)} сэмплов[/blue]")
                    self.audio_player.add_chunk(audio_chunk)
                
                elif response.HasField('end_message'):
                    console.print(f"[bold green]✅ {response.end_message}[/bold green]")
                    break
                
                elif response.HasField('error_message'):
                    console.print(f"[bold red]❌ Ошибка от сервера: {response.error_message}[/bold red]")
                    break
            
            # НЕ вызываем wait_for_queue_empty - пусть аудио воспроизводится естественным образом
            # self.audio_player.wait_for_queue_empty()
            
            # Запускаем ожидание естественного завершения воспроизведения
            # self.audio_player.wait_for_natural_completion()  # ← ЭТОТ МЕТОД НЕ СУЩЕСТВУЕТ!
            
            # Используем существующий метод для проверки статуса
            if hasattr(self.audio_player, 'wait_for_queue_empty'):
                # Проверяем статус без блокировки
                is_completed = self.audio_player.wait_for_queue_empty()
                if is_completed:
                    console.print("[blue]🎵 Аудио уже завершено[/blue]")
                else:
                    console.print("[blue]🎵 Аудио продолжает воспроизводиться...[/blue]")
            else:
                console.print("[yellow]⚠️ Метод wait_for_queue_empty недоступен[/yellow]")
            
            # Логируем завершение стрима, но НЕ останавливаем воспроизведение
            console.print("[bold green]✅ gRPC стрим завершен, аудио продолжает воспроизводиться...[/bold green]")
            
        except grpc.aio.AioRpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                console.print("[bold yellow]⚠️ Стриминг отменен клиентом[/bold yellow]")
            else:
                console.print(f"[bold red]❌ gRPC ошибка: {e.details()}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]❌ Произошла непредвиденная ошибка в стриминге: {e}[/bold red]")
        finally:
            # НЕ останавливаем воспроизведение автоматически - пусть аудио играет до конца
            # if self.audio_player.is_playing:
            #     self.audio_player.stop_playback()
            
            # Убеждаемся, что call завершен, если он был создан
            if call and not call.done():
                call.cancel()

async def main():
    """Основная функция клиента"""
    client = GrpcClient()
    
    try:
        # Подключаемся к серверу
        if not await client.connect():
            return
        
        # Основной цикл
        while True:
            prompt = console.input("[bold cyan]🎤 Введите промпт (или 'quit'): [/bold cyan]")
            if prompt.lower() == 'quit':
                break
            
            # Запускаем стриминг
            await client.stream_audio(prompt)
    
    except KeyboardInterrupt:
        console.print("\n[bold yellow]👋 Выход...[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]❌ Произошла непредвиденная ошибка: {e}[/bold red]")
    finally:
        await client.disconnect()
        logger.info("gRPC клиент завершил работу.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]👋 Выход...[/bold yellow]")
