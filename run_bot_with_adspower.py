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

# Массив имен - для каждой карты одно имя
FIRST_NAMES = [
    "Mohammed",   # для карты 1
    "Fatima",     # для карты 2
    "Ahmed",      # для карты 3
    "Aisha",      # для карты 4
    "Omar",       # для карты 5
    "Khadija"     # для карты 6
]

# Массив фамилий - для каждой карты одна фамилия
LAST_NAMES = [
    "Al-Rashid",     # для карты 1
    "Al-Zahra",      # для карты 2
    "Al-Mansouri",   # для карты 3
    "Al-Sabah",      # для карты 4
    "Al-Maktoum",    # для карты 5
    "Al-Nahyan"      # для карты 6
]

# Массив карт в формате кортежей (номер, срок, CVC)
CARDS = [
    ("5573770014543221", "09/30", "153"),  # карта 1
    ("5573770014573426", "09/30", "162"),  # карта 2
    ("5573 7700 1455 3055", "09/30", "932"),  # карта 3
    ("5573 7700 1452 9246", "09/30", "654"),  # карта 4
    ("5573 7700 1454 6463", "09/30", "124"),  # карта 5
    ("5573770014599009", "09/30", "554")   # карта 6
]

# Массив адресов - для каждой карты один адрес
ADDRESSES = [
    "Princess!!Tower",       # для карты 1
    "Princess??Tower",       # для карты 2
    "Princess~Tower",        # для карты 3
    "Princess::Tower",       # для карты 4
    "Princess||Tower",       # для карты 5
    "Princess**Tower"        # для карты 6
]

# Массив адресов второй строки - для каждой карты один адрес
ADDRESS_LINE2 = [
    "42!!floor!!rm!!4208",        # для карты 1
    "42??floor??rm??4208",        # для карты 2
    "42~level~room~4208",         # для карты 3
    "42::story::apartment::4208", # для карты 4
    "42||storey||suite||4208",    # для карты 5
    "42**deck**unit**4208"        # для карты 6
]

# Массив телефонов - для каждой карты один телефон
PHONES = [
    "504729381",    # для карты 1
    "558463927",    # для карты 2
    "504821637",    # для карты 3
    "552847639",    # для карты 4
    "505691273",    # для карты 5
    "506284951"     # для карты 6
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

def generate_order_data(card_index):
    """Генерирует данные заказа на основе индекса карты"""
    card_number, card_expiry, card_cvc = CARDS[card_index]  # Распаковываем кортеж
    first_name = FIRST_NAMES[card_index]        # Берем имя для карты
    last_name = LAST_NAMES[card_index]          # Берем фамилию для карты
    address = ADDRESSES[card_index]             # Берем адрес для карты
    address_line2 = ADDRESS_LINE2[card_index]   # Берем адрес2 для карты
    phone = PHONES[card_index]                  # Берем телефон для карты
    
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
        
        # 4. Делаем 3 попытки с одной картой в одном браузере
        card_success = False
        
        # Генерируем данные для текущей карты
        order_data = generate_order_data(card_index)
        
        # Делаем ВСЕ 3 попытки с одними и теми же данными (независимо от результата)
        for attempt in range(3):
            print(f"\n🔄 Попытка #{attempt + 1} с картой #{card_index + 1}")
            
            from bot_example import run_single_registration
            success = run_single_registration(order_data)
            
            if success:
                card_success = True
                print(f"🎉 КАРТА #{card_index + 1} ВЫПОЛНЕНА УСПЕШНО на попытке #{attempt + 1}!")
            else:
                print(f"❌ Попытка #{attempt + 1} не удалась")
            
            # Делаем паузу между попытками (кроме последней)
            if attempt < 2:
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
        
        # 4. Делаем 3 попытки с одной картой в одном браузере
        # Определяем какую карту использовать для этого браузера
        card_index = (browser_number - 1) % len(CARDS)
        order_data = generate_order_data(card_index)
        
        print(f"🎯 Браузер #{browser_number} использует карту #{card_index + 1}: {CARDS[card_index][0]}")
        
        # Делаем ВСЕ 3 попытки с одними и теми же данными (независимо от результата)
        for attempt in range(3):
            print(f"\n🔄 Попытка #{attempt + 1} с картой #{card_index + 1}")
            
            from bot_example import run_single_registration
            success = run_single_registration(order_data)
            
            if success:
                successful_attempts += 1
                print(f"🎉 КАРТА #{card_index + 1} ВЫПОЛНЕНА УСПЕШНО на попытке #{attempt + 1}!")
            else:
                print(f"❌ Попытка #{attempt + 1} не удалась")
            
            # Делаем паузу между попытками (кроме последней)
            if attempt < 2:
                print(f"⏳ Ждем 5 секунд перед следующей попыткой...")
                time.sleep(5)
        
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
    print(f"👤 Попыток в одном браузере: 3 (с одной картой)")
    print(f"🔄 Логика: 1 браузер = 1 карта = 3 попытки")
    print(f"📍 Адрес: {ADDRESSES[0]} (Princess Tower)")
    print(f"🏢 Город: {STATIC_ADDRESS['city']}")
    print("=" * 60)
    
    successful_orders = 0
    failed_orders = 0
    browser_counter = 0
    
    # Проверяем количество карт
    total_cards = len(CARDS)
    print(f"📊 Всего карт для использования: {total_cards}")
    print(f"🔄 Каждая карта будет использована в отдельном браузере")
    print(f"🎯 Всего браузеров будет запущено: {total_cards}")
    print("=" * 60)
    
    # Цикл браузеров (каждый браузер использует одну карту)
    for browser_number in range(1, total_cards + 1):
        try:
            print(f"\n{'='*60}")
            print(f"🌐 БРАУЗЕР #{browser_number}")
            print(f"🎯 Попыток в этом браузере: 3 (с одной картой)")
            print(f"{'='*60}")
            
            # Запускаем все комбинации карт и имен в одном браузере
            browser_success = run_all_combinations_in_browser(browser_number)
            
            if browser_success > 0:
                successful_orders += browser_success
                print(f"🎉 БРАУЗЕР #{browser_number}: {browser_success} успешных заказов!")
            else:
                failed_orders += 3
                print(f"💥 БРАУЗЕР #{browser_number}: все 3 карты неудачны")
            
            # Пауза между браузерами
            print(f"\n⏳ Пауза 15 секунд перед следующим браузером...")
            time.sleep(15)
                
        except KeyboardInterrupt:
            print(f"\n⏸️ Цикл остановлен пользователем на браузере #{browser_number}")
            break
        except Exception as e:
            print(f"\n❌ Критическая ошибка в браузере #{browser_number}: {e}")
            failed_orders += 3
    
    # Все карты использованы
    print(f"\n{'='*60}")
    print(f"🏁 ВСЕ КАРТЫ ИСПОЛЬЗОВАНЫ!")
    print(f"📊 Запущено браузеров: {total_cards}")
    print(f"🎯 Каждая карта получила 3 попытки")
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
