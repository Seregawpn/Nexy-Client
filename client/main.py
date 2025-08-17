import asyncio
import logging
from rich.console import Console
from enum import Enum
import sys
from pathlib import Path

# Добавляем корневую директорию в путь для импорта
sys.path.append(str(Path(__file__).parent.parent))

from audio_player import AudioPlayer
from stt_recognizer import StreamRecognizer
from input_handler import InputHandler
from grpc_client import GrpcClient
from screen_capture import ScreenCapture
from utils.hardware_id import get_hardware_id, get_hardware_info

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

console = Console()

class AppState(Enum):
    IDLE = 1          # Ассистент спит, микрофон выключен
    LISTENING = 2     # Записываем команду (пробел зажат)
    PROCESSING = 3    # Обрабатываем команду
    SPEAKING = 4      # Ассистент говорит

async def main():
    """Основная функция клиента с push-to-talk логикой, захватом экрана и Hardware ID"""
    
    # Инициализируем компоненты в правильном порядке
    console.print("[bold blue]🔧 Инициализация компонентов...[/bold blue]")
    
    # 1. Сначала инициализируем STT (до gRPC)
    console.print("[blue]🎤 Инициализация STT...[/blue]")
    stt_recognizer = StreamRecognizer()
    
    # 2. Инициализируем захват экрана
    console.print("[blue]📸 Инициализация захвата экрана...[/blue]")
    screen_capture = ScreenCapture()
    
    # 3. Инициализируем аудио плеер
    console.print("[blue]🔊 Инициализация аудио плеера...[/blue]")
    audio_player = AudioPlayer(sample_rate=48000)
    
    # 4. Инициализируем gRPC клиент (последним)
    console.print("[blue]🌐 Инициализация gRPC клиента...[/blue]")
    grpc_client = GrpcClient()
    
    # 5. Получаем Hardware ID (один раз при запуске, с кэшированием)
    console.print("[blue]🆔 Получение Hardware ID...[/blue]")
    
    # Проверяем аргументы командной строки для управления кэшем
    import sys
    force_regenerate = "--force-regenerate" in sys.argv
    clear_cache = "--clear-cache" in sys.argv
    
    if clear_cache:
        from utils.hardware_id import clear_hardware_id_cache
        clear_hardware_id_cache()
        console.print("[yellow]🗑️ Кэш Hardware ID очищен[/yellow]")
    
    hardware_id = get_hardware_id(force_regenerate=force_regenerate)  # Автоматически использует кэш если доступен
    hardware_info = get_hardware_info()
    
    console.print(f"[bold green]✅ Hardware ID получен: {hardware_id[:16]}...[/bold green]")
    console.print(f"[blue]📱 UUID: {hardware_info['hardware_uuid'][:16]}...[/blue]")
    console.print(f"[blue]🔢 Serial: {hardware_info['serial_number']}[/blue]")
    
    # Показываем информацию о кэше
    from utils.hardware_id import get_cache_info
    cache_info = get_cache_info()
    if cache_info['exists']:
        console.print(f"[green]💾 Hardware ID загружен из кэша[/green]")
    else:
        console.print(f"[yellow]🔄 Hardware ID сгенерирован заново[/yellow]")
    
    # Показываем справку по управлению кэшем
    if "--help" in sys.argv:
        console.print("\n[yellow]📋 Управление кэшем Hardware ID:[/yellow]")
        console.print("[yellow]  • --clear-cache      - очистить кэш[/yellow]")
        console.print("[yellow]  • --force-regenerate - принудительно пересоздать ID[/yellow]")
        console.print("[yellow]  • --help            - показать эту справку[/yellow]")
        console.print("[yellow]  • Без аргументов    - использовать кэш если доступен[/yellow]")
    
    # Очередь для событий от клавиатуры
    event_queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    input_handler = InputHandler(loop, event_queue)
    
    # Состояние приложения
    state = AppState.IDLE
    
    # Переменные для хранения скриншота и активного вызова
    current_screenshot = None
    current_screen_info = None
    active_call = None
    
    console.print("[bold green]✅ Ассистент готов![/bold green]")
    console.print("[yellow]📋 Управление:[/yellow]")
    console.print("[yellow]  • Зажмите пробел → СРАЗУ активируется микрофон[/yellow]")
    console.print("[yellow]  • Удерживайте пробел → продолжается запись[/yellow]")
    console.print("[yellow]  • Отпустите пробел → останавливается запись + отправка команды[/yellow]")
    console.print("[yellow]  • Короткое нажатие → прерывание речи ассистента[/yellow]")
    console.print("[yellow]  • При активации автоматически захватывается экран[/yellow]")
    console.print("[yellow]  • Hardware ID отправляется с каждой командой[/yellow]")

    try:
        # Получаем информацию об экране
        screen_info = screen_capture.get_screen_info()
        console.print(f"[bold blue]📱 Экран: {screen_info.get('width', 0)}x{screen_info.get('height', 0)} пикселей[/bold blue]")
        
        # Подключаемся к gRPC серверу (после инициализации всех компонентов)
        console.print("[blue]🔌 Подключение к серверу...[/blue]")
        if not await grpc_client.connect():
            console.print("[bold red]❌ Не удалось подключиться к серверу[/bold red]")
            return
            
        console.print("[bold green]✅ Подключено к серверу[/bold green]")
        
        # Основной цикл обработки событий
        while True:
            event = await event_queue.get()
            
            if event == "start_recording":
                # Прерываем текущую речь, если она есть
                if active_call and not active_call.done():
                    console.print("[bold yellow]Прерываю предыдущий ответ...[/bold yellow]")
                    active_call.cancel()
                    grpc_client.audio_player.interrupt()
                    active_call = None
                
                # Если ассистент неактивен, начинаем запись
                if state == AppState.IDLE:
                    state = AppState.LISTENING
                    
                    console.print("[bold blue]📸 Захватываю экран...[/bold blue]")
                    current_screenshot = screen_capture.capture_screen(quality=80)
                    current_screen_info = screen_info
                    
                    if current_screenshot:
                        console.print(f"[bold green]✅ Скриншот захвачен: {len(current_screenshot)} символов Base64[/bold green]")
                    else:
                        console.print("[bold yellow]⚠️ Не удалось захватить скриншот[/bold yellow]")
                        current_screenshot = None
                    
                    stt_recognizer.start_recording()
                    console.print("[bold green]🎤 Слушаю команду...[/bold green]")
                    console.print("[yellow]💡 Удерживайте пробел и говорите команду[/yellow]")
                
            elif event == "interrupt_speech":
                # Короткое нажатие теперь тоже прерывает речь
                if active_call and not active_call.done():
                    console.print("[bold red]⏹️ Речь прервана (короткое нажатие)[/bold red]")
                    active_call.cancel()
                    grpc_client.audio_player.interrupt()
                    active_call = None
                    state = AppState.IDLE
                elif state == AppState.LISTENING:
                    stt_recognizer.stop_recording_and_recognize()
                    state = AppState.IDLE
                    console.print("[bold yellow]⚠️ Запись команды прервана[/bold yellow]")
                else:
                    console.print("[yellow]ℹ️ Ассистент не говорит[/yellow]")
                    
            elif event == "stop_recording" and state == AppState.LISTENING:
                state = AppState.PROCESSING
                console.print("[bold blue]🔍 Обрабатываю команду...[/bold blue]")
                
                command = stt_recognizer.stop_recording_and_recognize()
                
                if command and command.strip():
                    console.print(f"[bold green]📝 Команда: {command}[/bold green]")
                    
                    try:
                        # Запускаем стриминг и получаем объект вызова
                        stream_generator = grpc_client.stream_audio(
                            command, 
                            current_screenshot, 
                            current_screen_info,
                            hardware_id
                        )
                        
                        # Получаем сам объект вызова
                        active_call = await stream_generator.__anext__()
                        state = AppState.SPEAKING
                        
                        # Ожидаем завершения стриминга
                        async for _ in stream_generator:
                            # Этот цикл просто исчерпывает генератор
                            pass
                        
                        state = AppState.IDLE
                        active_call = None
                        console.print("[bold green]✅ Команда выполнена[/bold green]")
                        
                    except Exception as e:
                        console.print(f"[bold red]❌ Ошибка выполнения команды: {e}[/bold red]")
                        state = AppState.IDLE
                        active_call = None
                else:
                    console.print("[yellow]⚠️ Команда не распознана[/yellow]")
                    state = AppState.IDLE
                    
    except KeyboardInterrupt:
        console.print("\n[bold yellow]👋 Выход...[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]❌ Критическая ошибка: {e}[/bold red]")
    finally:
        if active_call and not active_call.done():
            active_call.cancel()
        stt_recognizer.cleanup()
        if grpc_client.audio_player.is_playing:
            grpc_client.audio_player.stop_playback()
        logger.info("Клиент завершил работу.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]👋 Выход...[/bold yellow]")
