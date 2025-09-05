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


def create_profile():
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
    
    # Используем первый доступный прокси
    proxy = proxies[0]
    proxy_id = proxy.get('proxy_id')  # Исправлено: proxy_id вместо id
    
    print(f"✅ Использую прокси: {proxy.get('type')}://{proxy.get('host')}:{proxy.get('port')}")
    
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


def main():
    """Главная функция"""
    print("=== Создание профиля AdsPower ===\n")
    
    # Создаем профиль
    user_id = create_profile()
    
    if user_id:
        print(f"\n🎉 Готово! Профиль создан с ID: {user_id}")
    else:
        print(f"\n❌ Не удалось создать профиль")
    
    print("\n=== Скрипт завершен ===")


if __name__ == "__main__":
    main()
