#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой скрипт для создания одного профиля в AdsPower
Использует настройки из config.json
"""

import requests
import json


def load_config():
    """Загружает настройки из config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки config.json: {e}")
        return None


def list_proxies():
    """Получает список всех прокси из AdsPower"""
    api_url = "http://127.0.0.1:50325"
    
    # Данные для запроса (пустой body для получения всех прокси)
    request_data = {}
    
    try:
        response = requests.post(f"{api_url}/api/v2/proxy-list/list", json=request_data)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("code") == 0:
                proxies = result.get("data", {}).get("list", [])
                print(f"📋 Найдено прокси: {len(proxies)}")
                
                for i, proxy in enumerate(proxies):
                    proxy_id = proxy.get('proxy_id')
                    proxy_type = proxy.get('type')
                    proxy_host = proxy.get('host')
                    proxy_port = proxy.get('port')
                    print(f"   {i+1}. ID: {proxy_id} | {proxy_type}://{proxy_host}:{proxy_port}")
                
                return proxies
            else:
                print(f"❌ Ошибка API: {result.get('msg')}")
                return []
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []


def create_profile(proxy_index=None):
    """Создает один профиль в AdsPower используя существующий прокси"""
    
    # Загружаем настройки
    config = load_config()
    if not config:
        return None
    
    # Берем первый профиль из конфига
    profile_config = config["profiles"][0]
    
    # URL API AdsPower
    api_url = "http://127.0.0.1:50325"
    
    # Получаем список прокси
    print("🔍 Получаю список прокси из AdsPower...")
    proxies = list_proxies()
    
    if not proxies:
        print("❌ Нет доступных прокси. Добавьте прокси в AdsPower приложении!")
        return None
    
    # Используем прокси по индексу или случайный
    if proxy_index is not None and 0 <= proxy_index < len(proxies):
        proxy = proxies[proxy_index]
        print(f"✅ Использую прокси #{proxy_index + 1}: {proxy.get('type')}://{proxy.get('host')}:{proxy.get('port')}")
    else:
        import random
        proxy = random.choice(proxies)
        print(f"✅ Использую случайный прокси: {proxy.get('type')}://{proxy.get('host')}:{proxy.get('port')}")
    
    proxy_id = proxy.get('proxy_id')
    
    # Данные для создания профиля
    profile_data = {
        "name": profile_config["name"],
        "group_id": "0",
        "remark": "Создан через скрипт",
        "proxyid": proxy_id  # Используем ID существующего прокси
    }
    
    print(f"Создаю профиль: {profile_config['name']}")
    
    try:
        # Отправляем запрос на создание профиля
        response = requests.post(f"{api_url}/api/v1/user/create", json=profile_data)
        
        # Проверяем ответ
        if response.status_code == 200:
            result = response.json()
            
            if result.get("code") == 0:
                user_id = result.get("data", {}).get("id")
                print(f"✅ Профиль успешно создан!")
                print(f"   Имя: {profile_config['name']}")
                print(f"   ID: {user_id}")
                print(f"   Прокси ID: {proxy_id}")
                return user_id
            else:
                print(f"❌ Ошибка API: {result.get('msg')}")
                return None
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def start_browser(user_id):
    """Запускает браузер для профиля и возвращает WebDriver данные"""
    api_url = "http://127.0.0.1:50325"
    
    # Данные для запуска браузера (API v2)
    browser_data = {
        "profile_id": user_id,
        "headless": "0",  # 0 = обычный режим, 1 = headless
        "last_opened_tabs": "1",  # Продолжить с последних открытых вкладок
        "proxy_detection": "1",  # Открыть страницу проверки прокси
        "password_filling": "0",  # Не заполнять пароли
        "password_saving": "0",  # Не сохранять пароли
        "cdp_mask": "1",  # Маскировать CDP детекцию
        "delete_cache": "0"  # Не удалять кэш
    }
    
    print(f"🚀 Запускаю браузер для профиля {user_id}...")
    
    try:
        response = requests.post(f"{api_url}/api/v2/browser-profile/start", json=browser_data)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("code") == 0:
                data = result.get("data", {})
                ws_selenium = data.get("ws", {}).get("selenium")
                ws_puppeteer = data.get("ws", {}).get("puppeteer")
                debug_port = data.get("debug_port")
                webdriver_path = data.get("webdriver")
                
                print(f"✅ Браузер успешно запущен!")
                print(f"   Selenium URL: {ws_selenium}")
                print(f"   Puppeteer URL: {ws_puppeteer}")
                print(f"   Debug Port: {debug_port}")
                print(f"   WebDriver Path: {webdriver_path}")
                
                return {
                    "success": True,
                    "ws_selenium": ws_selenium,
                    "ws_puppeteer": ws_puppeteer,
                    "debug_port": debug_port,
                    "webdriver_path": webdriver_path,
                    "user_id": user_id
                }
            else:
                print(f"❌ Ошибка запуска браузера: {result.get('msg')}")
                return {"success": False, "error": result.get('msg')}
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {"success": False, "error": str(e)}


def stop_browser(user_id):
    """Останавливает браузер профиля"""
    api_url = "http://127.0.0.1:50325"
    
    # Данные для остановки браузера (API v2)
    browser_data = {
        "profile_id": user_id
    }
    
    print(f"🛑 Останавливаю браузер для профиля {user_id}...")
    
    try:
        response = requests.post(f"{api_url}/api/v2/browser-profile/stop", json=browser_data)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("code") == 0:
                print(f"✅ Браузер успешно остановлен!")
                return True
            else:
                print(f"❌ Ошибка остановки браузера: {result.get('msg')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def main():
    """Главная функция"""
    print("=== Создание профиля AdsPower ===\n")
    
    # Создаем профиль
    user_id = create_profile()
    
    if user_id:
        print(f"\n🎉 Профиль создан с ID: {user_id}")
        
        # Запускаем браузер
        browser_info = start_browser(user_id)
        
        if browser_info["success"]:
            print(f"\n🌐 Браузер готов для автоматизации!")
            print(f"   WebDriver URL: {browser_info['ws_url']}")
            print(f"\n💡 Теперь ваш бот может подключиться к браузеру!")
            print(f"   Используйте WebDriver URL для Selenium/Playwright")
            
            # Спрашиваем пользователя
            input("\n⏸️ Нажмите Enter чтобы остановить браузер...")
            
            # Останавливаем браузер
            stop_browser(user_id)
        else:
            print(f"\n❌ Не удалось запустить браузер: {browser_info['error']}")
    else:
        print("\n❌ Не удалось создать профиль.")
    
    print("\n=== Скрипт завершен ===")


if __name__ == "__main__":
    main()
