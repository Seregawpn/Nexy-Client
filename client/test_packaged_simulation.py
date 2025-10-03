"""
Симуляция упакованного приложения для тестирования путей к ресурсам
Имитирует различные режимы PyInstaller без полной пересборки
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Добавляем пути к модулям
CLIENT_ROOT = Path(__file__).parent
sys.path.insert(0, str(CLIENT_ROOT))
sys.path.insert(0, str(CLIENT_ROOT / "modules"))

def simulate_pyinstaller_onefile():
    """
    Симуляция PyInstaller onefile режима
    Создает временную директорию и устанавливает sys._MEIPASS
    """
    print("\n" + "=" * 80)
    print("🧪 ТЕСТ 1: Симуляция PyInstaller ONEFILE режима")
    print("=" * 80)
    
    # Создаем временную директорию для имитации _MEIPASS
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Копируем ресурсы в временную директорию (имитация распаковки PyInstaller)
        assets_src = CLIENT_ROOT / "assets"
        assets_dst = temp_path / "assets"
        
        print(f"📁 Создаю временную структуру в: {temp_path}")
        shutil.copytree(assets_src, assets_dst)
        print(f"   ✓ Скопированы assets/ -> {assets_dst}")
        
        # Устанавливаем sys._MEIPASS
        sys._MEIPASS = str(temp_path)
        print(f"   ✓ Установлен sys._MEIPASS = {sys._MEIPASS}")
        
        try:
            # Тестируем определение путей
            from modules.welcome_message.utils.resource_path import (
                get_resource_base_path,
                get_resource_path,
                resource_exists
            )
            from modules.welcome_message.core.types import WelcomeConfig
            
            print("\n📊 Результаты:")
            
            base_path = get_resource_base_path()
            print(f"   • Базовый путь: {base_path}")
            print(f"   • Равен _MEIPASS: {str(base_path) == sys._MEIPASS}")
            
            config = WelcomeConfig()
            audio_path = config.get_audio_path()
            print(f"   • Путь к аудио: {audio_path}")
            print(f"   • Файл существует: {audio_path.exists()}")
            
            # Проверяем другие ресурсы
            test_resources = [
                "assets/audio/welcome_en.mp3",
                "assets/audio/welcome_en.wav",
            ]
            
            print("\n   📂 Проверка ресурсов:")
            all_ok = True
            for resource in test_resources:
                exists = resource_exists(resource)
                status = "✓" if exists else "✗"
                print(f"      {status} {resource}")
                if not exists:
                    all_ok = False
            
            if all_ok and audio_path.exists():
                print("\n   ✅ УСПЕХ: Все ресурсы найдены в ONEFILE режиме!")
            else:
                print("\n   ❌ ОШИБКА: Некоторые ресурсы не найдены!")
            
            return all_ok and audio_path.exists()
            
        finally:
            # Удаляем sys._MEIPASS после теста
            if hasattr(sys, "_MEIPASS"):
                delattr(sys, "_MEIPASS")
                print("\n   🧹 Очистка: sys._MEIPASS удален")

def simulate_pyinstaller_bundle():
    """
    Симуляция PyInstaller bundle режима (.app)
    Создает структуру Contents/MacOS/ и Contents/Resources/
    """
    print("\n" + "=" * 80)
    print("🧪 ТЕСТ 2: Симуляция PyInstaller BUNDLE режима (.app)")
    print("=" * 80)
    
    # Создаем временную структуру .app
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Создаем структуру .app bundle
        app_bundle = temp_path / "Nexy.app"
        contents = app_bundle / "Contents"
        macos_dir = contents / "MacOS"
        resources_dir = contents / "Resources"
        
        macos_dir.mkdir(parents=True)
        resources_dir.mkdir(parents=True)
        
        print(f"📁 Создаю структуру .app bundle в: {app_bundle}")
        
        # Копируем ресурсы
        assets_src = CLIENT_ROOT / "assets"
        assets_dst = resources_dir / "assets"
        shutil.copytree(assets_src, assets_dst)
        print(f"   ✓ Скопированы assets/ -> {assets_dst}")
        
        # Создаем фейковый исполняемый файл
        fake_exe = macos_dir / "Nexy"
        fake_exe.write_text("#!/bin/bash\necho 'Nexy'\n")
        fake_exe.chmod(0o755)
        print(f"   ✓ Создан исполняемый файл: {fake_exe}")
        
        # Сохраняем оригинальный sys.argv[0]
        original_argv0 = sys.argv[0]
        
        try:
            # Имитируем запуск из .app bundle
            sys.argv[0] = str(fake_exe)
            print(f"   ✓ Установлен sys.argv[0] = {sys.argv[0]}")
            
            # Перезагружаем модули для применения новых путей
            import importlib
            import modules.welcome_message.utils.resource_path
            import modules.welcome_message.core.types
            
            importlib.reload(modules.welcome_message.utils.resource_path)
            importlib.reload(modules.welcome_message.core.types)
            
            from modules.welcome_message.utils.resource_path import (
                get_resource_base_path,
                get_resource_path,
                resource_exists
            )
            from modules.welcome_message.core.types import WelcomeConfig
            
            print("\n📊 Результаты:")
            
            base_path = get_resource_base_path()
            print(f"   • Базовый путь: {base_path}")
            print(f"   • Находится в Resources: {'Resources' in str(base_path)}")
            
            config = WelcomeConfig()
            audio_path = config.get_audio_path()
            print(f"   • Путь к аудио: {audio_path}")
            print(f"   • Файл существует: {audio_path.exists()}")
            
            # Проверяем ресурсы
            test_resources = [
                "assets/audio/welcome_en.mp3",
                "assets/audio/welcome_en.wav",
            ]
            
            print("\n   📂 Проверка ресурсов:")
            all_ok = True
            for resource in test_resources:
                exists = resource_exists(resource)
                status = "✓" if exists else "✗"
                print(f"      {status} {resource}")
                if not exists:
                    all_ok = False
            
            if all_ok and audio_path.exists():
                print("\n   ✅ УСПЕХ: Все ресурсы найдены в BUNDLE режиме!")
            else:
                print("\n   ❌ ОШИБКА: Некоторые ресурсы не найдены!")
            
            return all_ok and audio_path.exists()
            
        finally:
            # Восстанавливаем оригинальный sys.argv[0]
            sys.argv[0] = original_argv0
            print("\n   🧹 Очистка: sys.argv[0] восстановлен")
            
            # Перезагружаем модули обратно
            importlib.reload(modules.welcome_message.utils.resource_path)
            importlib.reload(modules.welcome_message.core.types)

def test_development_mode():
    """
    Тест обычного development режима (baseline)
    """
    print("\n" + "=" * 80)
    print("🧪 ТЕСТ 3: Development режим (baseline)")
    print("=" * 80)
    
    from modules.welcome_message.utils.resource_path import (
        get_resource_base_path,
        resource_exists
    )
    from modules.welcome_message.core.types import WelcomeConfig
    
    print("\n📊 Результаты:")
    
    base_path = get_resource_base_path()
    print(f"   • Базовый путь: {base_path}")
    print(f"   • Равен client/: {base_path == CLIENT_ROOT}")
    
    config = WelcomeConfig()
    audio_path = config.get_audio_path()
    print(f"   • Путь к аудио: {audio_path}")
    print(f"   • Файл существует: {audio_path.exists()}")
    
    # Проверяем ресурсы
    test_resources = [
        "assets/audio/welcome_en.mp3",
        "assets/audio/welcome_en.wav",
    ]
    
    print("\n   📂 Проверка ресурсов:")
    all_ok = True
    for resource in test_resources:
        exists = resource_exists(resource)
        status = "✓" if exists else "✗"
        print(f"      {status} {resource}")
        if not exists:
            all_ok = False
    
    if all_ok and audio_path.exists():
        print("\n   ✅ УСПЕХ: Все ресурсы найдены в Development режиме!")
    else:
        print("\n   ❌ ОШИБКА: Некоторые ресурсы не найдены!")
    
    return all_ok and audio_path.exists()

def main():
    """Запуск всех тестов"""
    print("=" * 80)
    print("🚀 СИМУЛЯЦИЯ УПАКОВАННОГО ПРИЛОЖЕНИЯ")
    print("=" * 80)
    print("\nЭтот скрипт имитирует различные режимы PyInstaller")
    print("для быстрого тестирования без полной пересборки .app\n")
    
    results = {}
    
    try:
        # Тест 1: Development режим (baseline)
        results['development'] = test_development_mode()
        
        # Тест 2: PyInstaller onefile
        results['onefile'] = simulate_pyinstaller_onefile()
        
        # Тест 3: PyInstaller bundle (.app)
        results['bundle'] = simulate_pyinstaller_bundle()
        
    except Exception as e:
        print(f"\n❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Итоговая сводка
    print("\n" + "=" * 80)
    print("📊 ИТОГОВАЯ СВОДКА")
    print("=" * 80)
    
    for mode, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {mode.upper()}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("\n💡 Следующий шаг: Пересобрать приложение и протестировать реальный .app:")
        print("   cd /Users/sergiyzasorin/Development/Nexy/client")
        print("   ./packaging/build_final.sh")
    else:
        print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")
        print("\n💡 Проверьте логику определения путей в resource_path.py")
    
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



