import asyncio
import logging
import numpy as np
import grpc
import sys
import os

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
            # Создаем неблокирующий канал
            self.channel = grpc.aio.insecure_channel(self.server_address)
            self.stub = streaming_pb2_grpc.StreamingServiceStub(self.channel)
            
            console.print(f"[bold green]✅ Подключение к gRPC серверу {self.server_address} установлено[/bold green]")
            return True
            
        except Exception as e:
            console.print(f"[bold red]❌ Ошибка подключения к серверу: {e}[/bold red]")
            return False
    
    async def disconnect(self):
        """Отключение от сервера"""
        if self.channel:
            await self.channel.close()
            console.print("[bold yellow]🔌 Отключено от сервера[/bold yellow]")
    
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
                    self.audio_player.add_chunk(audio_chunk)
                
                elif response.HasField('end_message'):
                    console.print(f"[bold green]✅ {response.end_message}[/bold green]")
                    break
                
                elif response.HasField('error_message'):
                    console.print(f"[bold red]❌ Ошибка от сервера: {response.error_message}[/bold red]")
                    break
            
            self.audio_player.wait_for_queue_empty()
            
        except grpc.aio.AioRpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                console.print("[bold yellow]⚠️ Стриминг отменен клиентом[/bold yellow]")
            else:
                console.print(f"[bold red]❌ gRPC ошибка: {e.details()}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]❌ Произошла непредвиденная ошибка в стриминге: {e}[/bold red]")
        finally:
            if self.audio_player.is_playing:
                self.audio_player.stop_playback()
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
