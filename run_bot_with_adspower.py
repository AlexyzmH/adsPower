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

# Массив имен - для каждой пары карт одно имя
FIRST_NAMES = [
    "Omar",      # для пары 1
    "Layla",     # для пары 2
    "Hassan"     # для пары 3
]

# Массив фамилий - для каждой пары карт одна фамилия
LAST_NAMES = [
    "Al-Sabah",      # для пары 1
    "Al-Maktoum",    # для пары 2
    "Al-Nahyan"      # для пары 3
]

# Массив карт в формате пар (двумерный массив)
CARDS = [
    # Пара 1
    [
        ("5573770015136538", "09/30", "246"),  # карта 1.1
        ("5573770015175841", "09/30", "134")   # карта 1.2
    ],
    # Пара 2
    [
        ("5573770015128477", "09/30", "582"),  # карта 2.1
        ("5573770015129269", "09/30", "834")   # карта 2.2
    ],
    # Пара 3
    [
        ("5573770015183043", "09/30", "352"),  # карта 3.1
        ("5573770014913127", "09/30", "332")   # карта 3.2
    ]
]

# Массив адресов - для каждой пары карт один адрес
ADDRESSES = [
    "Princess**Tower",       # для пары 1
    "Princess++Tower",       # для пары 2
    "Princess##Tower"        # для пары 3
]

# Массив адресов второй строки - для каждой пары карт один адрес
ADDRESS_LINE2 = [
    "42**floor**rm**4208",        # для пары 1
    "42++level++room++4208",      # для пары 2
    "42##floor##apt##4208"        # для пары 3
]

# Массив телефонов - для каждой пары карт один телефон
PHONES = [
    "507384291",    # для пары 1
    "508472639",    # для пары 2
    "506293847"     # для пары 3
]

# Статичные данные адреса (город и провинция остаются одинаковыми)
STATIC_ADDRESS = {
    "city": "Dubai",
    "province": "Dubai Marina"
}

# Прокси теперь получаем из AdsPower браузера через API

def generate_email(name, last_name):
    """Генерирует простой email в формате: имя.фамилия + 3цифры@gmail.com"""
    # Генерируем 3 случайные цифры
    number = random.randint(100, 999)
    # Чередуем между gmail и yahoo
    domains = ["gmail.com", "yahoo.com"]
    domain = random.choice(domains)
    return f"{name.lower()}.{last_name.lower()}{number}@{domain}"

def generate_password():
    """Генерирует случайный пароль из 14 символов"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=14))

def generate_order_data(pair_index, card_in_pair_index):
    """Генерирует данные заказа на основе индексов пары карт и карты в паре"""
    card_number, card_expiry, card_cvc = CARDS[pair_index][card_in_pair_index]  # Берем карту из пары
    first_name = FIRST_NAMES[pair_index]        # Берем имя для пары
    last_name = LAST_NAMES[pair_index]          # Берем фамилию для пары
    address = ADDRESSES[pair_index]             # Берем адрес для пары
    address_line2 = ADDRESS_LINE2[pair_index]   # Берем адрес2 для пары
    phone = PHONES[pair_index]                  # Берем телефон для пары
    
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

def run_single_attempt_with_two_cards(pair_index, attempt_num):
    """Запускает попытку с двумя картами на один аккаунт"""
    print(f"\n📋 Попытка #{attempt_num} (Пара карт #{pair_index + 1}):")
    
    # Генерируем данные аккаунта (одинаковые для обеих карт)
    order_data = generate_order_data(pair_index, 0)  # Используем первую карту для данных аккаунта
    
    print(f"   👤 {order_data['first_name']} {order_data['last_name']}")
    print(f"   📧 {order_data['email']}")
    print(f"   📍 {order_data['address']}")
    print(f"   📞 {order_data['phone']}")
    
    try:
        from bot_example import attempt_registration
        
        # Получаем обе карты из пары
        card1_data = generate_order_data(pair_index, 0)
        card2_data = generate_order_data(pair_index, 1)
        
        print(f"   💳 Карта 1: {card1_data['card_number']}")
        print(f"   💳 Карта 2: {card2_data['card_number']}")
        
        # Запускаем бота с двумя картами
        success = attempt_registration(1, 0, card1_data, return_driver=False, second_card_data=card2_data)
        
        if success:
            print(f"✅ Попытка #{attempt_num} успешна!")
            return True
        else:
            print(f"❌ Попытка #{attempt_num} не удалась!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка в попытке #{attempt_num}: {e}")
        return False

def run_pair_attempts(pair_index, order_counter):
    """Запускает попытки для пары карт в одном браузере"""
    print(f"\n{'='*60}")
    print(f"🚀 ПАРА КАРТ #{pair_index + 1}:")
    print(f"   💳 Карта 1: {CARDS[pair_index][0][0]}")
    print(f"   💳 Карта 2: {CARDS[pair_index][1][0]}")
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
        time.sleep(10)
        
        # 3. Устанавливаем переменные окружения для бота
        os.environ['ADSPOWER_DEBUG_PORT'] = str(browser_info['debug_port'])
        if 'webdriver_path' in browser_info:
            os.environ['ADSPOWER_WEBDRIVER_PATH'] = browser_info['webdriver_path']
        
        # 4. Делаем попытку с парой карт в одном браузере
        pair_success = run_single_attempt_with_two_cards(pair_index, 1)
        
        if pair_success:
            print(f"🎉 ПАРА КАРТ #{pair_index + 1} ВЫПОЛНЕНА УСПЕШНО!")
        else:
            print(f"❌ Пара карт #{pair_index + 1} не удалась")
        
        return pair_success
            
    except KeyboardInterrupt:
        print(f"\n⏸️ Пара карт #{pair_index + 1} остановлена пользователем")
        return False
        
    except Exception as e:
        print(f"\n❌ Ошибка в паре карт #{pair_index + 1}: {e}")
        return False
        
    finally:
        # Останавливаем браузер только в конце всех попыток
        if user_id:
            print(f"3️⃣ Останавливаем браузер для пары карт #{pair_index + 1}...")
            stop_browser(user_id)
            time.sleep(5)

def run_all_pairs_in_browser(browser_number):
    """Запускает одну пару карт в отдельном браузере"""
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
        time.sleep(10)
        
        # 3. Устанавливаем переменные окружения для бота
        os.environ['ADSPOWER_DEBUG_PORT'] = str(browser_info['debug_port'])
        if 'webdriver_path' in browser_info:
            os.environ['ADSPOWER_WEBDRIVER_PATH'] = browser_info['webdriver_path']
        
        # 4. Делаем попытку с одной парой карт в этом браузере
        pair_index = browser_number - 1  # browser_number начинается с 1, pair_index с 0
        print(f"\n🎯 Браузер #{browser_number} пробует пару карт #{pair_index + 1}")
        
        success = run_single_attempt_with_two_cards(pair_index, 1)
        
        if success:
            successful_attempts += 1
            print(f"🎉 ПАРА КАРТ #{pair_index + 1} ВЫПОЛНЕНА УСПЕШНО!")
        else:
            print(f"❌ Пара карт #{pair_index + 1} не удалась")
        
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
    """Главная функция - запускает цикл браузеров (каждый браузер = одна пара карт)"""
    print("=== ЗАПУСК ЦИКЛА ЗАКАЗОВ С ADSPOWER ===")
    print(f"💳 Пар карт: {len(CARDS)}")
    print(f"💳 Всего карт: {len(CARDS) * 2}")
    print(f"🔄 Логика: 1 аккаунт = 2 карты (если первая не прошла, пробуем вторую)")
    print(f"📍 Адрес: {ADDRESSES[0]} (Princess Tower)")
    print(f"🏢 Город: {STATIC_ADDRESS['city']}")
    print("=" * 60)
    
    successful_orders = 0
    failed_orders = 0
    browser_counter = 0
    
    # Проверяем количество пар карт
    total_pairs = len(CARDS)
    print(f"📊 Всего пар карт: {total_pairs}")
    print(f"🔄 Каждая пара будет использована в отдельном браузере")
    print(f"🎯 Всего браузеров будет запущено: {total_pairs}")
    print("=" * 60)
    
    # Цикл браузеров (каждый браузер использует одну пару карт)
    for browser_number in range(1, total_pairs + 1):
        try:
            print(f"\n{'='*60}")
            print(f"🌐 БРАУЗЕР #{browser_number}")
            print(f"🎯 Пара карт в этом браузере: #{browser_number}")
            print(f"{'='*60}")
            
            # Запускаем одну пару карт в отдельном браузере
            browser_success = run_all_pairs_in_browser(browser_number)
            
            if browser_success > 0:
                successful_orders += browser_success
                print(f"🎉 БРАУЗЕР #{browser_number}: {browser_success} успешных заказов!")
            else:
                failed_orders += 1
                print(f"💥 БРАУЗЕР #{browser_number}: пара карт неудачна")
            
            # Пауза между браузерами
            print(f"\n⏳ Пауза 10 секунд перед следующим браузером...")
            time.sleep(10)
                
        except KeyboardInterrupt:
            print(f"\n⏸️ Цикл остановлен пользователем на браузере #{browser_number}")
            break
        except Exception as e:
            print(f"\n❌ Критическая ошибка в браузере #{browser_number}: {e}")
            failed_orders += 1
    
    # Все пары карт использованы
    print(f"\n{'='*60}")
    print(f"🏁 ВСЕ ПАРЫ КАРТ ИСПОЛЬЗОВАНЫ!")
    print(f"📊 Запущено браузеров: {total_pairs}")
    print(f"🎯 Каждая пара получила отдельный браузер с 2 картами")
    print(f"{'='*60}")
    
    # Итоговая статистика
    print(f"\n{'='*60}")
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"✅ Успешных заказов: {successful_orders}")
    print(f"❌ Неудачных заказов: {failed_orders}")
    print(f"📈 Успешность: {(successful_orders/(successful_orders+failed_orders)*100):.1f}%" if (successful_orders+failed_orders) > 0 else "0%")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
