#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска бота с AdsPower
Сначала запускает браузер, потом бота
"""

import subprocess
import time
import sys
from create_profile import create_profile, start_browser, stop_browser


def main():
    """Главная функция"""
    print("=== Запуск бота с AdsPower ===\n")
    
    # Создаем профиль и запускаем браузер
    print("1️⃣ Создаем профиль и запускаем браузер...")
    user_id = create_profile()
    
    if not user_id:
        print("❌ Не удалось создать профиль!")
        return
    
    print(f"✅ Профиль создан: {user_id}")
    time.sleep(5)
    
    # Запускаем браузер
    browser_info = start_browser(user_id)
    
    if not browser_info["success"]:
        print(f"❌ Не удалось запустить браузер: {browser_info['error']}")
        return
    
    print(f"✅ Браузер запущен: {browser_info['debug_port']}")
    
    try:
        # Ждем немного чтобы браузер полностью загрузился
        print("⏳ Ждем загрузки браузера...")
        time.sleep(3)
        
        # Запускаем бота
        print("\n2️⃣ Запускаем бота...")
        print("=" * 50)
        
        # Импортируем и запускаем бота
        from bot_example import run_flow
        
        # Сохраняем debug port в переменную окружения для бота
        import os
        os.environ['ADSPOWER_DEBUG_PORT'] = str(browser_info['debug_port'])
        print(f"🔧 Установлен debug port: {browser_info['debug_port']}")
        
        # Запускаем бота (можно указать конкретную карту: --card-index 0)
        run_flow()
        
    except KeyboardInterrupt:
        print("\n⏸️ Бот остановлен пользователем")
        
    except Exception as e:
        print(f"\n❌ Ошибка в работе бота: {e}")
        
    finally:
        # Останавливаем браузер
        print("\n3️⃣ Останавливаем браузер...")
        stop_browser(user_id)
    
    print("\n=== Завершено ===")


if __name__ == "__main__":
    main()
