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

# Массив имен - двумерный: для каждой карты 5 вариантов имени
FIRST_NAMES = [
    ["Emma", "Emily", "Emilia", "Emmy", "Emma-Lee"],         # 5 вариантов для карты 2
    ["James", "Jim", "Jimmy", "Jamie", "Jameson"],         # 5 вариантов для карты 3
    ["Sophia", "Sophie", "Sofia", "Soph", "Sophia-Rose"],         # 5 вариантов для карты 4
    ["Alexander", "Alex", "Alexis", "Alec", "Alexandria"]        # 5 вариантов для карты 5
]

# Массив фамилий - двумерный: для каждой карты 5 вариантов фамилии
LAST_NAMES = [
    ["Davis", "Davies", "Davis-Jones", "Davis-Brown", "Davis-Taylor"], # 5 вариантов для карты 2
    ["Wilson", "Wills", "Wilson-Smith", "Wilson-Brown", "Wilson-Davis"], # 5 вариантов для карты 3
    ["Moore", "Moor", "Moore-Taylor", "Moore-Wilson", "Moore-Brown"], # 5 вариантов для карты 4
    ["Taylor", "Tay", "Taylor-Moore", "Taylor-Wilson", "Taylor-Davis"] # 5 вариантов для карты 5
]

# Массив карт в формате кортежей (номер, срок, CVC)
CARDS = [
    ("5573 7700 1412 2786", "09/30", "904"),
    ("5573 7700 1409 2856", "09/30", "848")
]

# Статичные данные адреса
STATIC_ADDRESS = {
    "address": "_p_r_i_n_c_e_s_s_ _t_o_w_e_r_",
    "address_line2": "_4_2_0_8_ _4_2_ _f_l_o_o_r_", 
    "city": "Dubai",
    "province": "Dubai Marina",
    "phone": "508698540"
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
    
    return {
        # Данные аккаунта
        "email": generate_email(first_name, last_name),
        "password": generate_password(),
        
        # Данные доставки
        "first_name": first_name,
        "last_name": last_name,
        "address": STATIC_ADDRESS["address"],
        "address_line2": STATIC_ADDRESS["address_line2"],
        "city": STATIC_ADDRESS["city"],
        "province": STATIC_ADDRESS["province"],
        "phone": STATIC_ADDRESS["phone"],
        
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

def create_profile_with_proxy(proxy_index=None):
    """Создает профиль с прокси из AdsPower"""
    # Прокси теперь получаем автоматически из AdsPower через create_profile()
    return create_profile(proxy_index)

def main():
    """Главная функция - запускает цикл по картам и именам"""
    print("=== ЗАПУСК ЦИКЛА ЗАКАЗОВ С ADSPOWER ===")
    print(f"💳 Карт: {len(CARDS)}")
    print(f"🔄 Попыток на карту: 5")
    print(f"📊 Максимум заказов: {len(CARDS) * 5}")
    print(f"📍 Адрес: {STATIC_ADDRESS['address']}")
    print("=" * 60)
    
    successful_orders = 0
    failed_orders = 0
    order_counter = 0
    
    # Цикл по картам
    for card_index in range(len(CARDS)):
        try:
            # Запускаем 3 попытки для одной карты в одном браузере
            success = run_card_attempts(card_index, order_counter)
            
            if success:
                successful_orders += 1
                print(f"🎉 КАРТА #{card_index + 1} ВЫПОЛНЕНА УСПЕШНО!")
            else:
                failed_orders += 1
                print(f"💥 КАРТА #{card_index + 1} ИСЧЕРПАНА - все 5 попыток неудачны")
            
            order_counter += 1
            
            # Пауза между картами (кроме последней)
            if card_index < len(CARDS) - 1:
                print(f"\n⏳ Пауза 10 секунд перед следующей картой...")
                time.sleep(10)
                
        except KeyboardInterrupt:
            print(f"\n⏸️ Цикл остановлен пользователем на карте #{card_index + 1}")
            break
        except Exception as e:
            print(f"\n❌ Критическая ошибка в карте #{card_index + 1}: {e}")
            failed_orders += 1
            order_counter += 1
    
    # Итоговая статистика
    print(f"\n{'='*60}")
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"✅ Успешных заказов: {successful_orders}")
    print(f"❌ Неудачных заказов: {failed_orders}")
    print(f"📈 Успешность: {(successful_orders/(successful_orders+failed_orders)*100):.1f}%" if (successful_orders+failed_orders) > 0 else "0%")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
