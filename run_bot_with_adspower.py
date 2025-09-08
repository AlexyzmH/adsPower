#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный скрипт для запуска бота с AdsPower
Содержит массив данных (карты, адреса, прокси) и запускает цикл
"""

import subprocess
import time
import sys
import os
import random
import string
from create_profile import create_profile, start_browser, stop_browser

# МАССИВЫ ДАННЫХ ДЛЯ ГЕНЕРАЦИИ ЗАКАЗОВ

# Массив имен - двумерный: для каждой карты 3 варианта имени
FIRST_NAMES = [
    ["Khalid", "Khaled", "Khalil"],       # 3 варианта для карты 1
    ["Aisha", "Aysha", "Ayesha"],         # 3 варианта для карты 2
    ["Hassan", "Hasan", "Hussein"]        # 3 варианта для карты 3
]

# Массив фамилий - двумерный: для каждой карты 3 варианта фамилии
LAST_NAMES = [
    ["Al-Sabah", "Al-Sabah", "Al-Sabah"],                 # 3 варианта для карты 1
    ["Al-Maktoum", "Al-Maktoum", "Al-Maktoum"],           # 3 варианта для карты 2
    ["Al-Nahyan", "Al-Nahyan", "Al-Nahyan"]               # 3 варианта для карты 3
]

# Массив карт в формате кортежей (номер, срок, CVC)
CARDS = [
    ("5573770014194298", "09/30", "699"),
    ("5573770014199685", "09/30", "076"),
    ("5573770014157774", "09/30", "209")
]

# Массив адресов - двумерный: для каждой карты 3 варианта адреса (Princess Tower с разными символами)
ADDRESSES = [
    ["Princess Tower", "Princess=>Tower", "Princess::Tower"],                          # 3 варианта для карты 1
    ["Princess-Tower", "Princess/Tower", "Princess_Tower"],                            # 3 варианта для карты 2
    ["Princess--Tower", "Princess>>Tower", "Princess..Tower"]                          # 3 варианта для карты 3
]

# Массив адресов второй строки - двумерный: для каждой карты 3 варианта (rm, floor, room, charge)
ADDRESS_LINE2 = [
    ["42 floor, rm 4208", "42 floor, room 4208", "42 floor, charge 4208"],            # 3 варианта для карты 1
    ["42-floor-rm-4208", "42/floor/room/4208", "42::floor::charge::4208"],            # 3 варианта для карты 2
    ["42=>floor=>rm=>4208", "42--floor--room--4208", "42..floor..charge..4208"]       # 3 варианта для карты 3
]

# Массив телефонов - двумерный: для каждой карты 3 варианта телефона (реалистичные дубайские номера)
PHONES = [
    ["552468135", "505512616", "506172218"],                                           # 3 варианта для карты 1
    ["542891456", "558234791", "504567823"],                                           # 3 варианта для карты 2
    ["562345678", "502987654", "544123987"]                                            # 3 варианта для карты 3
]

# Статичные данные адреса (город и провинция остаются одинаковыми)
STATIC_ADDRESS = {
    "city": "Dubai",
    "province": "Dubai Marina"
}

# Прокси теперь получаем из AdsPower браузера через API

def generate_email(name, last_name):
    """Генерирует email в формате: 4буквы + имя + фамилия + 2цифры + 7букв@gmail.com"""
    # Генерируем 4 случайные буквы
    prefix = ''.join(random.choices(string.ascii_letters, k=4))
    # Генерируем случайное число от 10 до 99
    number = random.randint(10, 99)
    # Генерируем 7 случайных букв
    suffix = ''.join(random.choices(string.ascii_letters, k=4))
    return f"{prefix}{name}{last_name}{number}{suffix}@gmail.com"

def generate_password():
    """Генерирует случайный пароль из 14 символов"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=14))

def generate_order_data(card_index, name_index):
    """Генерирует данные заказа на основе индексов карты и имени"""
    card_number, card_expiry, card_cvc = CARDS[card_index]  # Распаковываем кортеж
    first_name = FIRST_NAMES[card_index][name_index]        # Берем имя из подмассива карты
    last_name = LAST_NAMES[card_index][name_index]          # Берем фамилию из подмассива карты
    address = ADDRESSES[card_index][name_index]             # Берем адрес из подмассива карты
    address_line2 = ADDRESS_LINE2[card_index][name_index]   # Берем адрес2 из подмассива карты
    phone = PHONES[card_index][name_index]                  # Берем телефон из подмассива карты
    
    return {
        # Данные аккаунта
        "email": generate_email(first_name, last_name),
        "password": generate_password(),
        
        # Данные доставки
        "first_name": first_name,
        "last_name": last_name,
        "address": address,
        "address_line2": address_line2,
        "city": STATIC_ADDRESS["city"],
        "province": STATIC_ADDRESS["province"],
        "phone": phone,
        
        # Данные карты
        "card_number": card_number,
        "card_expiry": card_expiry,
        "card_cvc": card_cvc,
        "card_name": f"{first_name} {last_name}"
    }

def run_single_attempt(order_data, attempt_num):
    """Запускает одну попытку регистрации в уже открытом браузере"""
    print(f"\n📋 Попытка #{attempt_num}:")
    print(f"   👤 {order_data['first_name']} {order_data['last_name']}")
    print(f"   📧 {order_data['email']}")
    print(f"   💳 {order_data['card_number']}")
    
    try:
        # Запускаем бота с данными заказа
        from bot_example import run_single_registration
        success = run_single_registration(order_data)
        
        if success:
            print(f"✅ Попытка #{attempt_num} успешна!")
            return True
        else:
            print(f"❌ Попытка #{attempt_num} не удалась!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка в попытке #{attempt_num}: {e}")
        return False

def run_card_attempts(card_index, order_counter):
    """Запускает 3 попытки для одной карты в одном браузере"""
    print(f"\n{'='*60}")
    print(f"🚀 КАРТА #{card_index + 1}: {CARDS[card_index][0]}")
    print(f"🌐 Создаем браузер с прокси из AdsPower")
    print(f"{'='*60}")
    
    user_id = None
    browser_info = None
    
    try:
        # 1. Создаем профиль с прокси из AdsPower
        print("1️⃣ Создаем профиль с прокси из AdsPower...")
        proxy_index = order_counter % 100  # Используем order_counter для выбора прокси
        user_id = create_profile_with_proxy(proxy_index)
        
        if not user_id:
            print("❌ Не удалось создать профиль!")
            return False
        
        print(f"✅ Профиль создан: {user_id}")
        time.sleep(5)
        
        # 2. Запускаем браузер
        print("2️⃣ Запускаем браузер...")
        browser_info = start_browser(user_id)
        
        if not browser_info["success"]:
            print(f"❌ Не удалось запустить браузер: {browser_info['error']}")
            return False
        
        print(f"✅ Браузер запущен: {browser_info['debug_port']}")
        time.sleep(15)
        
        # 3. Устанавливаем переменные окружения для бота
        os.environ['ADSPOWER_DEBUG_PORT'] = str(browser_info['debug_port'])
        if 'webdriver_path' in browser_info:
            os.environ['ADSPOWER_WEBDRIVER_PATH'] = browser_info['webdriver_path']
        
        # 4. Делаем 5 попыток в одном браузере
        card_success = False
        for attempt in range(5):
            name_index = attempt
            order_data = generate_order_data(card_index, name_index)
            
            success = run_single_attempt(order_data, attempt + 1)
            
            if success:
                card_success = True
                print(f"🎉 КАРТА #{card_index + 1} ВЫПОЛНЕНА УСПЕШНО на попытке #{attempt + 1}!")
                break  # Выходим из цикла попыток
            else:
                if attempt < 4:  # Если не последняя попытка
                    print(f"⏳ Ждем 5 секунд перед следующей попыткой...")
                    time.sleep(5)
        
        return card_success
            
    except KeyboardInterrupt:
        print(f"\n⏸️ Карта #{card_index + 1} остановлена пользователем")
        return False
        
    except Exception as e:
        print(f"\n❌ Ошибка в карте #{card_index + 1}: {e}")
        return False
        
    finally:
        # Останавливаем браузер только в конце всех попыток
        if user_id:
            print(f"3️⃣ Останавливаем браузер для карты #{card_index + 1}...")
            stop_browser(user_id)
            time.sleep(2)

def run_all_combinations_in_browser(browser_number):
    """Запускает все комбинации карт и имен в одном браузере"""
    user_id = None
    browser_info = None
    successful_attempts = 0
    
    try:
        # 1. Создаем профиль с прокси из AdsPower
        print("1️⃣ Создаем профиль с прокси из AdsPower...")
        user_id = create_profile_with_proxy(browser_number)
        
        if not user_id:
            print("❌ Не удалось создать профиль!")
            return 0
        
        print(f"✅ Профиль создан: {user_id}")
        time.sleep(5)
        
        # 2. Запускаем браузер
        print("2️⃣ Запускаем браузер...")
        browser_info = start_browser(user_id)
        
        if not browser_info["success"]:
            print(f"❌ Не удалось запустить браузер: {browser_info['error']}")
            return 0
        
        print(f"✅ Браузер запущен: {browser_info['debug_port']}")
        time.sleep(15)
        
        # 3. Устанавливаем переменные окружения для бота
        os.environ['ADSPOWER_DEBUG_PORT'] = str(browser_info['debug_port'])
        if 'webdriver_path' in browser_info:
            os.environ['ADSPOWER_WEBDRIVER_PATH'] = browser_info['webdriver_path']
        
        # 4. Делаем все комбинации карт и имен в одном браузере
        attempt_counter = 0
        for card_index in range(len(CARDS)):
            for name_index in range(3):  # 3 имени на каждую карту
                attempt_counter += 1
                print(f"\n🎯 ПОПЫТКА #{attempt_counter}: Карта #{card_index + 1}, Имя #{name_index + 1}")
                
                # Генерируем данные для этой попытки
                order_data = generate_order_data(card_index, name_index)
                
                # Запускаем одну попытку
                success = run_single_attempt(order_data, attempt_counter)
                
                if success:
                    successful_attempts += 1
                    print(f"🎉 ПОПЫТКА #{attempt_counter} УСПЕШНА!")
                else:
                    print(f"💥 ПОПЫТКА #{attempt_counter} НЕУДАЧНА")
                
                # Пауза между попытками (кроме последней)
                if attempt_counter < len(CARDS) * 3:
                    print(f"⏳ Пауза 3 секунды перед следующей попыткой...")
                    time.sleep(3)
        
        return successful_attempts
            
    except KeyboardInterrupt:
        print(f"\n⏸️ Браузер #{browser_number} остановлен пользователем")
        return successful_attempts
        
    except Exception as e:
        print(f"\n❌ Ошибка в браузере #{browser_number}: {e}")
        return successful_attempts
        
    finally:
        # Останавливаем браузер в конце всех попыток
        if user_id:
            print(f"3️⃣ Останавливаем браузер #{browser_number}...")
            stop_browser(user_id)
            time.sleep(2)

def create_profile_with_proxy(proxy_index=None):
    """Создает профиль с прокси из AdsPower"""
    # Прокси теперь получаем автоматически из AdsPower через create_profile()
    return create_profile(proxy_index)

def main():
    """Главная функция - запускает цикл браузеров (каждый браузер = все карты × все имена)"""
    print("=== ЗАПУСК ЦИКЛА ЗАКАЗОВ С ADSPOWER ===")
    print(f"💳 Карт: {len(CARDS)}")
    print(f"👤 Имен на карту: 3")
    print(f"🔄 Попыток в одном браузере: {len(CARDS) * 3}")
    print(f"📍 Адрес: {ADDRESSES[0][0]} (Princess Tower)")
    print(f"🏢 Город: {STATIC_ADDRESS['city']}")
    print("=" * 60)
    
    successful_orders = 0
    failed_orders = 0
    browser_counter = 0
    
    # Цикл браузеров (каждый браузер делает все комбинации карт и имен)
    while True:  # Бесконечный цикл браузеров
        try:
            browser_counter += 1
            print(f"\n{'='*60}")
            print(f"🌐 БРАУЗЕР #{browser_counter}")
            print(f"🎯 Попыток в этом браузере: {len(CARDS) * 3}")
            print(f"{'='*60}")
            
            # Запускаем все комбинации карт и имен в одном браузере
            browser_success = run_all_combinations_in_browser(browser_counter)
            
            if browser_success > 0:
                successful_orders += browser_success
                print(f"🎉 БРАУЗЕР #{browser_counter}: {browser_success} успешных заказов!")
            else:
                failed_orders += len(CARDS) * 3
                print(f"💥 БРАУЗЕР #{browser_counter}: все {len(CARDS) * 3} попыток неудачны")
            
            # Пауза между браузерами
            print(f"\n⏳ Пауза 15 секунд перед следующим браузером...")
            time.sleep(15)
                
        except KeyboardInterrupt:
            print(f"\n⏸️ Цикл остановлен пользователем на браузере #{browser_counter}")
            break
        except Exception as e:
            print(f"\n❌ Критическая ошибка в браузере #{browser_counter}: {e}")
            failed_orders += len(CARDS) * 3
            browser_counter += 1
    
    # Итоговая статистика
    print(f"\n{'='*60}")
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"✅ Успешных заказов: {successful_orders}")
    print(f"❌ Неудачных заказов: {failed_orders}")
    print(f"📈 Успешность: {(successful_orders/(successful_orders+failed_orders)*100):.1f}%" if (successful_orders+failed_orders) > 0 else "0%")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
