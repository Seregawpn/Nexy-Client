"""
SimpleModuleCoordinator - Центральный координатор модулей
Управляет инициализацией, запуском и остановкой всех модулей приложения
Четкое разделение ответственности без дублирования
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

# Импорты интеграций (НЕ модулей напрямую!)
from integrations.tray_controller_integration import TrayControllerIntegration
from integrations.mode_management_integration import ModeManagementIntegration
from integrations.hardware_id_integration import HardwareIdIntegration, HardwareIdIntegrationConfig
from integrations.grpc_client_integration import GrpcClientIntegration
from integrations.speech_playback_integration import SpeechPlaybackIntegration
from modules.tray_controller.core.tray_types import TrayConfig
from integrations.input_processing_integration import InputProcessingIntegration, InputProcessingConfig
from integrations.voice_recognition_integration import VoiceRecognitionIntegration, VoiceRecognitionConfig
from integrations.permissions_integration import PermissionsIntegration
from modules.permissions.core.types import PermissionConfig
from integrations.updater_integration import UpdaterIntegration
from integrations.network_manager_integration import NetworkManagerIntegration
from modules.network_manager.core.config import NetworkManagerConfig
from integrations.audio_device_integration import AudioDeviceIntegration
from modules.audio_device_manager.core.types import AudioDeviceManagerConfig
from integrations.interrupt_management_integration import InterruptManagementIntegration, InterruptManagementIntegrationConfig
from modules.input_processing.keyboard.types import KeyboardConfig
from integrations.screenshot_capture_integration import ScreenshotCaptureIntegration
from integrations.signal_integration import SignalIntegration
from modules.signals.config.types import PatternConfig
from integrations.signal_integration import SignalsIntegrationConfig

# Импорты core компонентов
from integration.core.event_bus import EventBus, EventPriority
from integration.core.state_manager import ApplicationStateManager, AppMode
from integration.core.error_handler import ErrorHandler, ErrorSeverity, ErrorCategory

# Импорт конфигурации
from config.unified_config_loader import UnifiedConfigLoader

# Импорт Workflows
from integration.workflows import ListeningWorkflow, ProcessingWorkflow

logger = logging.getLogger(__name__)

# Глобальная защита от множественного запуска
_app_running = False

class SimpleModuleCoordinator:
    """Центральный координатор модулей для Nexy AI Assistant"""
    
    def __init__(self):
        # Core компоненты (центральные)
        self.event_bus: Optional[EventBus] = None
        self.state_manager: Optional[ApplicationStateManager] = None
        self.error_handler: Optional[ErrorHandler] = None
        
        # Интеграции (обертки для модулей)
        self.integrations: Dict[str, Any] = {}
        
        # Workflows (координаторы режимов)
        self.workflows: Dict[str, Any] = {}
        
        # Конфигурация
        self.config = UnifiedConfigLoader()
        
        # Состояние
        self.is_initialized = False
        self.is_running = False
        # Фоновый asyncio loop и поток для асинхронных интеграций
        self._bg_loop = None
        self._bg_thread = None
        
    async def initialize(self) -> bool:
        """Инициализация всех компонентов и интеграций"""
        try:
            print("\n" + "="*60)
            print("🚀 SIMPLE MODULE COORDINATOR - ИНИЦИАЛИЗАЦИЯ")
            print("="*60)
            print("Инициализация core компонентов и интеграций...")
            print("="*60 + "\n")
            
            # 1. Создаем core компоненты
            print("🔧 Создание core компонентов...")
            self.event_bus = EventBus()
            self.state_manager = ApplicationStateManager()
            self.error_handler = ErrorHandler(self.event_bus)
            print("✅ Core компоненты созданы")
            
            # 1.1 Запускаем фоновый asyncio loop (для EventBus/интеграций)
            self._start_background_loop()

            # 2. Создаем интеграции
            print("🔧 Создание интеграций...")
            # Прикрепляем EventBus к StateManager, чтобы централизованно публиковать смену режимов
            try:
                self.state_manager.attach_event_bus(self.event_bus)
                # Фиксируем основной loop в EventBus
                self.event_bus.attach_loop(self._bg_loop)
            except Exception:
                pass
            await self._create_integrations()
            print("✅ Интеграции созданы")
            
            # 3. Инициализируем интеграции
            print("🔧 Инициализация интеграций...")
            await self._initialize_integrations()
            print("✅ Интеграции инициализированы")
            
            # 4. Настраиваем координацию
            print("🔧 Настройка координации...")
            await self._setup_coordination()
            print("✅ Координация настроена")
            
            self.is_initialized = True
            
            print("\n" + "="*60)
            print("✅ ВСЕ КОМПОНЕНТЫ ИНИЦИАЛИЗИРОВАНЫ!")
            print("="*60)
            print("🎯 Иконка должна появиться в меню-баре macOS")
            print("🖱️ Кликните по иконке, чтобы увидеть меню")
            print("⌨️ Нажмите ПРОБЕЛ для тестирования клавиатуры")
            print("⌨️ Нажмите Ctrl+C для выхода")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Критическая ошибка инициализации: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _create_integrations(self):
        """Создание всех интеграций"""
        try:
            # Hardware ID Integration — должен стартовать рано, чтобы ID был доступен всем
            self.integrations['hardware_id'] = HardwareIdIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                error_handler=self.error_handler,
                config=None  # берёт значения из unified_config.yaml при наличии
            )

            # TrayController Integration - используем конфигурацию модуля
            # Конфигурация будет загружена внутри TrayControllerIntegration
            tray_config = None  # Будет создана автоматически из unified_config.yaml
            
            self.integrations['tray'] = TrayControllerIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                error_handler=self.error_handler,
                config=tray_config
            )
            
            # InputProcessing Integration - загружаем из конфигурации
            config_data = self.config._load_config()
            kbd_cfg = config_data['integrations']['keyboard']
            keyboard_config = KeyboardConfig(
                key_to_monitor=kbd_cfg['key_to_monitor'],
                short_press_threshold=kbd_cfg['short_press_threshold'],
                long_press_threshold=kbd_cfg['long_press_threshold'],
                event_cooldown=kbd_cfg['event_cooldown'],
                hold_check_interval=kbd_cfg['hold_check_interval'],
                debounce_time=kbd_cfg['debounce_time']
            )
            
            input_cfg = config_data['integrations']['input_processing']
            input_config = InputProcessingConfig(
                keyboard_config=keyboard_config,
                enable_keyboard_monitoring=input_cfg['enable_keyboard_monitoring'],
                auto_start=input_cfg['auto_start'],
                keyboard_backend=kbd_cfg.get('backend', 'auto')
            )
            
            self.integrations['input'] = InputProcessingIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                error_handler=self.error_handler,
                config=input_config
            )
            
            # Permissions Integration - используем конфигурацию модуля
            # Конфигурация будет загружена внутри PermissionsIntegration
            permissions_config = None  # Будет создана автоматически из unified_config.yaml
            
            self.integrations['permissions'] = PermissionsIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                error_handler=self.error_handler,
                config=permissions_config
            )
            
            # Updater Integration - новая система обновлений
            updater_cfg = config_data.get('updater', {})
            
            self.integrations['updater'] = UpdaterIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                config=updater_cfg
            )
            
            # Network Manager Integration - используем конфигурацию модуля
            # Конфигурация будет загружена внутри NetworkManagerIntegration
            network_config = None  # Будет создана автоматически из unified_config.yaml
            
            self.integrations['network'] = NetworkManagerIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                error_handler=self.error_handler,
                config=network_config
            )
            
            # Audio Device Integration - используем конфигурацию модуля
            # Конфигурация будет загружена внутри AudioDeviceIntegration
            audio_config = None  # Будет создана автоматически из unified_config.yaml
            
            self.integrations['audio'] = AudioDeviceIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                error_handler=self.error_handler,
                config=audio_config
            )
            
            # Interrupt Management Integration - загружаем из конфигурации
            int_cfg = config_data['integrations']['interrupt_management']
            interrupt_config = InterruptManagementIntegrationConfig(
                max_concurrent_interrupts=int_cfg['max_concurrent_interrupts'],
                interrupt_timeout=int_cfg['interrupt_timeout'],
                retry_attempts=int_cfg['retry_attempts'],
                retry_delay=int_cfg['retry_delay'],
                enable_speech_interrupts=int_cfg['enable_speech_interrupts'],
                enable_recording_interrupts=int_cfg['enable_recording_interrupts'],
                enable_session_interrupts=int_cfg['enable_session_interrupts'],
                enable_full_reset=int_cfg['enable_full_reset']
            )
            
            self.integrations['interrupt'] = InterruptManagementIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                error_handler=self.error_handler,
                config=interrupt_config
            )

            # Screenshot Capture Integration (PROCESSING)
            self.integrations['screenshot_capture'] = ScreenshotCaptureIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                error_handler=self.error_handler,
            )
            
            # Voice Recognition Integration - конфигурация по умолчанию/из unified_config
            try:
                vrec_cfg_raw = config_data['integrations'].get('voice_recognition', {})
                # Централизованный язык: берем из STT
                language = self.config.get_stt_language("en-US")
                vrec_config = VoiceRecognitionConfig(
                    timeout_sec=vrec_cfg_raw.get('timeout_sec', 10.0),
                    simulate=vrec_cfg_raw.get('simulate', True),
                    simulate_success_rate=vrec_cfg_raw.get('simulate_success_rate', 0.7),
                    simulate_min_delay_sec=vrec_cfg_raw.get('simulate_min_delay_sec', 1.0),
                    simulate_max_delay_sec=vrec_cfg_raw.get('simulate_max_delay_sec', 3.0),
                    language=language,
                )
            except Exception:
                # Fallback с централизованным языком
                vrec_config = VoiceRecognitionConfig(language=self.config.get_stt_language("en-US"))

            self.integrations['voice_recognition'] = VoiceRecognitionIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                error_handler=self.error_handler,
                config=vrec_config,
            )

            # Mode Management Integration (централизация режимов)
            self.integrations['mode_management'] = ModeManagementIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                error_handler=self.error_handler,
            )

            # Grpc Client Integration
            self.integrations['grpc'] = GrpcClientIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                error_handler=self.error_handler,
            )

            # Speech Playback Integration
            self.integrations['speech_playback'] = SpeechPlaybackIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                error_handler=self.error_handler,
            )

            # Signals Integration (audio cues via EventBus -> playback)
            try:
                sig_raw = config_data.get('integrations', {}).get('signals', {})
                patterns_cfg = {}
                for name, p in sig_raw.get('patterns', {}).items():
                    patterns_cfg[name] = PatternConfig(
                        audio=p.get('audio', True),
                        visual=p.get('visual', False),
                        volume=p.get('volume', 0.2),
                        tone_hz=p.get('tone_hz', 880),
                        duration_ms=p.get('duration_ms', 120),
                        cooldown_ms=p.get('cooldown_ms', 300),
                    )
                sig_cfg = SignalsIntegrationConfig(
                    enabled=sig_raw.get('enabled', True),
                    sample_rate=sig_raw.get('sample_rate', 48_000),
                    default_volume=sig_raw.get('default_volume', 0.2),
                    patterns=patterns_cfg or None,
                )
            except Exception:
                sig_cfg = SignalsIntegrationConfig()

            self.integrations['signals'] = SignalIntegration(
                event_bus=self.event_bus,
                state_manager=self.state_manager,
                error_handler=self.error_handler,
                config=sig_cfg,
            )

            print("✅ Интеграции созданы: tray, input, permissions, update_manager, network, audio, interrupt, voice_recognition, screenshot_capture, grpc, speech_playback, signals")
            
            # 3. Создаем Workflows (координаторы режимов)
            print("🔧 Создание Workflows...")
            
            self.workflows['listening'] = ListeningWorkflow(
                event_bus=self.event_bus
            )
            print("✅ ListeningWorkflow создан")
            
            self.workflows['processing'] = ProcessingWorkflow(
                event_bus=self.event_bus
            )
            print("✅ ProcessingWorkflow создан")
            
            print("✅ Все Workflows созданы успешно")
            
        except Exception as e:
            print(f"❌ Ошибка создания интеграций: {e}")
            raise
    
    async def _initialize_integrations(self):
        """Инициализация всех интеграций"""
        try:
            # Инициализируем интеграции
            for name, integration in self.integrations.items():
                print(f"🔧 Инициализация {name}...")
                success = await integration.initialize()
                if not success:
                    print(f"❌ Ошибка инициализации {name}")
                    raise Exception(f"Failed to initialize {name}")
                print(f"✅ {name} инициализирован")
            
            # Инициализируем Workflows
            print("🔧 Инициализация Workflows...")
            for name, workflow in self.workflows.items():
                print(f"🔧 Инициализация workflow {name}...")
                await workflow.initialize()
                print(f"✅ Workflow {name} инициализирован")
                
        except Exception as e:
            print(f"❌ Ошибка инициализации интеграций/workflows: {e}")
            raise
    
    async def _setup_coordination(self):
        """Настройка координации между модулями"""
        try:
            # Подписываемся на события приложения
            await self.event_bus.subscribe("app.startup", self._on_app_startup, EventPriority.HIGH)
            await self.event_bus.subscribe("app.shutdown", self._on_app_shutdown, EventPriority.HIGH)
            await self.event_bus.subscribe("app.mode_changed", self._on_mode_changed, EventPriority.MEDIUM)

            # Подписываемся на события клавиатуры
            await self.event_bus.subscribe("keyboard.long_press", self._on_keyboard_event, EventPriority.HIGH)
            await self.event_bus.subscribe("keyboard.release", self._on_keyboard_event, EventPriority.HIGH)
            await self.event_bus.subscribe("keyboard.short_press", self._on_keyboard_event, EventPriority.HIGH)

            # Подписываемся на события скриншота для логирования
            try:
                await self.event_bus.subscribe("screenshot.captured", self._on_screenshot_captured, EventPriority.MEDIUM)
                await self.event_bus.subscribe("screenshot.error", self._on_screenshot_error, EventPriority.MEDIUM)
            except Exception:
                pass

            # Подписываемся на события аудио для явного логирования
            try:
                await self.event_bus.subscribe("audio.device_switched", self._on_audio_device_switched, EventPriority.MEDIUM)
                await self.event_bus.subscribe("audio.device_snapshot", self._on_audio_device_snapshot, EventPriority.MEDIUM)
            except Exception:
                pass
            
            print("✅ Координация настроена")
            
        except Exception as e:
            print(f"❌ Ошибка настройки координации: {e}")
            raise
    
    async def start(self) -> bool:
        """Запуск всех интеграций"""
        try:
            if not self.is_initialized:
                print("❌ Компоненты не инициализированы")
                return False
            
            if self.is_running:
                print("⚠️ Компоненты уже запущены")
                return True
            
            print("🚀 Запуск всех интеграций...")
            
            # Запускаем все интеграции
            for name, integration in self.integrations.items():
                print(f"🚀 Запуск {name}...")
                success = await integration.start()
                if not success:
                    print(f"❌ Ошибка запуска {name}")
                    return False
                print(f"✅ {name} запущен")
            
            # Запускаем все Workflows
            print("🚀 Запуск Workflows...")
            for name, workflow in self.workflows.items():
                print(f"🚀 Запуск workflow {name}...")
                await workflow.start()
                print(f"✅ Workflow {name} запущен")
            
            self.is_running = True
            
            # Публикуем событие запуска
            await self.event_bus.publish("app.startup", {
                "coordinator": "simple_module_coordinator",
                "integrations": list(self.integrations.keys())
            })
            
            print("✅ Все интеграции запущены")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска интеграций: {e}")
            return False
    
    async def stop(self) -> bool:
        """Остановка всех интеграций"""
        try:
            if not self.is_running:
                print("⚠️ Компоненты не запущены")
                return True
            
            print("⏹️ Остановка всех интеграций...")
            
            # Публикуем событие остановки
            await self.event_bus.publish("app.shutdown", {
                "coordinator": "simple_module_coordinator"
            })
            
            # Останавливаем все интеграции
            for name, integration in self.integrations.items():
                print(f"⏹️ Остановка {name}...")
                success = await integration.stop()
                if not success:
                    print(f"⚠️ Ошибка остановки {name}")
                else:
                    print(f"✅ {name} остановлен")
            
            # Останавливаем все Workflows
            print("⏹️ Остановка Workflows...")
            for name, workflow in self.workflows.items():
                print(f"⏹️ Остановка workflow {name}...")
                await workflow.stop()
                print(f"✅ Workflow {name} остановлен")
            
            self.is_running = False
            print("✅ Все интеграции и workflows остановлены")
            # Останавливаем фоновый loop
            try:
                if self._bg_loop and self._bg_loop.is_running():
                    self._bg_loop.call_soon_threadsafe(self._bg_loop.stop)
                if self._bg_thread:
                    self._bg_thread.join(timeout=1.0)
            except Exception:
                pass
            return True
            
        except Exception as e:
            print(f"❌ Ошибка остановки интеграций: {e}")
            return False
    
    async def run(self):
        """Запуск приложения"""
        global _app_running
        try:
            # Проверяем, не запущено ли уже приложение
            if _app_running or self.is_running:
                print("⚠️ Приложение уже запущено")
                return
            
            _app_running = True
                
            # Инициализируем
            success = await self.initialize()
            if not success:
                print("❌ Не удалось инициализировать компоненты")
                return
            
            # Запускаем
            success = await self.start()
            if not success:
                print("❌ Не удалось запустить компоненты")
                return
            
            # Получаем приложение rumps для отображения иконки
            tray_integration = self.integrations.get('tray')
            if not tray_integration:
                print("❌ TrayController интеграция не найдена")
                return
            
            app = tray_integration.get_app()
            if not app:
                print("❌ Не удалось получить приложение трея")
                return
            
            print("🎯 Запуск приложения с иконкой в меню-баре...")
            
            # Запускаем UI-таймер ПОСЛЕ того как rumps приложение готово
            # Используем rumps.Timer для запуска таймера в UI-потоке (однократно)
            import rumps
            def start_timer_callback(_):
                try:
                    tray_integration.start_ui_timer()
                    logger.info("✅ UI-таймер запущен через rumps callback")
                    # Останавливаем startup_timer после первого запуска
                    startup_timer.stop()
                except Exception as e:
                    logger.error(f"❌ Ошибка запуска UI-таймера через callback: {e}")
            
            # Запускаем таймер через 1 секунду после старта приложения (однократно)
            # В rumps.Timer нет параметра repeat; останавливаем таймер внутри колбэка
            startup_timer = rumps.Timer(start_timer_callback, 1.0)
            startup_timer.start()
            
            # Запускаем приложение rumps (блокирующий вызов)
            app.run()
            
        except KeyboardInterrupt:
            print("\n⏹️ Приложение прервано пользователем")
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
        finally:
            _app_running = False
            await self.stop()
    
    # Обработчики событий (только координация, не дублирование логики)
    
    async def _on_app_startup(self, event):
        """Обработка запуска приложения"""
        try:
            print("🚀 Обработка запуска приложения в координаторе")
            # Делегируем обработку интеграциям через EventBus
            # Координатор не делает работу модулей!
            
        except Exception as e:
            print(f"❌ Ошибка обработки запуска приложения: {e}")
    
    async def _on_app_shutdown(self, event):
        """Обработка завершения приложения"""
        try:
            print("⏹️ Обработка завершения приложения в координаторе")
            # Делегируем обработку интеграциям через EventBus
            
        except Exception as e:
            print(f"❌ Ошибка обработки завершения приложения: {e}")
    
    async def _on_mode_changed(self, event):
        """Обработка смены режима приложения"""
        try:
            from integration.core.event_utils import event_data
            data = event_data(event)
            new_mode = data.get("mode", None)
            printable_mode = getattr(new_mode, "value", None) or str(new_mode) if new_mode is not None else "unknown"
            print(f"🔄 Координация смены режима: {printable_mode}")
            
            # Делегируем обработку интеграциям
            # Координатор только координирует, не обрабатывает!
            
        except Exception as e:
            print(f"❌ Ошибка обработки смены режима: {e}")
    
    async def _on_keyboard_event(self, event):
        """Обработка событий клавиатуры"""
        try:
            from integration.core.event_utils import event_type as _etype
            event_type = _etype(event, "unknown")
            print(f"⌨️ Координация события клавиатуры: {event_type}")
            
            # Делегируем обработку интеграциям
            # Координатор только координирует, не обрабатывает!
            
        except Exception as e:
            print(f"❌ Ошибка обработки события клавиатуры: {e}")
            
    async def _on_screenshot_captured(self, event):
        """Логирование результата захвата скриншота"""
        try:
            data = (event or {}).get("data", {})
            path = data.get("image_path")
            width = data.get("width")
            height = data.get("height")
            size_bytes = data.get("size_bytes")
            session_id = data.get("session_id")
            print(f"🖼️ Screenshot captured: {path} ({width}x{height}, {size_bytes} bytes), session={session_id}")
            logger.info(f"Screenshot captured: path={path}, size={size_bytes}, dims={width}x{height}, session={session_id}")
        except Exception as e:
            logger.debug(f"Failed to log screenshot.captured: {e}")

    async def _on_screenshot_error(self, event):
        """Логирование ошибок захвата скриншота"""
        try:
            data = (event or {}).get("data", {})
            err = data.get("error")
            session_id = data.get("session_id")
            print(f"🖼️ Screenshot error: {err}, session={session_id}")
            logger.warning(f"Screenshot error: {err}, session={session_id}")
        except Exception as e:
            logger.debug(f"Failed to log screenshot.error: {e}")

    async def _on_audio_device_switched(self, event):
        """Логирование переключений аудио устройства."""
        try:
            data = (event or {}).get("data", {})
            from_device = data.get("from_device")
            to_device = data.get("to_device")
            device_type = data.get("device_type")
            print(f"🔊 Audio switched: {from_device} → {to_device} [{device_type}]")
            logger.info(f"Audio switched: {from_device} -> {to_device} type={device_type}")
        except Exception as e:
            logger.debug(f"Failed to log audio.device_switched: {e}")

    async def _on_audio_device_snapshot(self, event):
        """Логирование текущего устройства при запуске."""
        try:
            data = (event or {}).get("data", {})
            current = data.get("current_device")
            device_type = data.get("device_type")
            print(f"🔊 Audio device: {current} [{device_type}] (snapshot)")
            logger.info(f"Audio device snapshot: {current} type={device_type}")
        except Exception as e:
            logger.debug(f"Failed to log audio.device_snapshot: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Получить статус всех компонентов"""
        return {
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "core_components": {
                "event_bus": self.event_bus is not None,
                "state_manager": self.state_manager is not None,
                "error_handler": self.error_handler is not None
            },
            "integrations": {
                name: integration.get_status() 
                for name, integration in self.integrations.items()
            }
        }

    def _start_background_loop(self):
        """Запускает отдельный поток с asyncio loop, чтобы не блокироваться на app.run()."""
        import asyncio, threading
        if self._bg_loop and self._bg_thread:
            return
        self._bg_loop = asyncio.new_event_loop()
        def _runner():
            asyncio.set_event_loop(self._bg_loop)
            try:
                self._bg_loop.run_forever()
            finally:
                self._bg_loop.close()
        self._bg_thread = threading.Thread(target=_runner, name="nexy-bg-loop", daemon=True)
        self._bg_thread.start()
        print("🧵 Фоновый asyncio loop запущен для EventBus/интеграций")
