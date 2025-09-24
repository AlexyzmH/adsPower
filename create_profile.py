#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой скрипт для создания одного профиля в AdsPower
Использует настройки из config.json
"""

import requests
import json
import random
import secrets
import os


def get_random_browser():
    """Возвращает случайный браузер из списка"""
    browsers = [
        "chrome",
        "firefox", 
        "edge",
        "safari"
    ]
    return random.choice(browsers)


def get_random_os():
    """Возвращает случайную операционную систему из списка (только десктопные системы)"""
    operating_systems = [
        "Windows",    # Windows 10/11
        "macOS",      # macOS Monterey/Ventura/Sonoma
        "Linux"       # Ubuntu/Debian/Fedora
    ]
    return random.choice(operating_systems)


def generate_realistic_mac_address():
    """
    Генерирует реалистичную MAC-адрес для настоящего железа (не виртуальных машин)
    Использует OUI (Organizationally Unique Identifier) от реальных производителей
    """
    # OUI от реальных производителей сетевого оборудования
    real_hardware_ouis = [
        # Intel Corporation
        "00:1B:21", "00:1C:42", "00:1D:7E", "00:1E:67", "00:1F:3A",
        "00:21:6A", "00:22:FB", "00:24:81", "00:25:00", "00:26:55",
        "00:27:19", "00:28:45", "00:29:AB", "00:2A:70", "00:2B:0D",
        
        # Realtek Semiconductor
        "00:1F:5B", "00:1F:5C", "00:1F:5D", "00:1F:5E", "00:1F:5F",
        "00:1F:60", "00:1F:61", "00:1F:62", "00:1F:63", "00:1F:64",
        "00:1F:65", "00:1F:66", "00:1F:67", "00:1F:68", "00:1F:69",
        
        # Broadcom Corporation
        "00:10:18", "00:10:1F", "00:10:2F", "00:10:3F", "00:10:4F",
        "00:10:5F", "00:10:6F", "00:10:7F", "00:10:8F", "00:10:9F",
        "00:10:AF", "00:10:BF", "00:10:CF", "00:10:DF", "00:10:EF",
        
        # Qualcomm Atheros
        "00:13:10", "00:13:46", "00:13:74", "00:13:CE", "00:13:E8",
        "00:15:00", "00:15:6D", "00:15:AF", "00:15:B7", "00:15:C7",
        "00:15:E9", "00:15:F2", "00:16:01", "00:16:3E", "00:16:44",
        
        # Marvell Technology Group
        "00:50:43", "00:50:DA", "00:50:E2", "00:50:F2", "00:50:F5",
        "00:50:F6", "00:50:F7", "00:50:F8", "00:50:F9", "00:50:FA",
        "00:50:FB", "00:50:FC", "00:50:FD", "00:50:FE", "00:50:FF",
        
        # ASUS
        "00:1F:C6", "00:22:15", "00:24:8C", "00:26:18", "00:26:4A",
        "00:26:5B", "00:26:82", "00:26:AB", "00:26:CE", "00:26:F2",
        "00:27:19", "00:27:22", "00:27:8E", "00:27:EB", "00:28:45",
        
        # Dell
        "00:14:22", "00:15:C5", "00:16:35", "00:18:8B", "00:1A:A0",
        "00:1B:78", "00:1C:23", "00:1D:09", "00:1E:4C", "00:1F:29",
        "00:21:70", "00:22:19", "00:23:7D", "00:24:B8", "00:25:64",
        
        # HP
        "00:1F:29", "00:21:5A", "00:22:64", "00:23:7D", "00:24:81",
        "00:25:B3", "00:26:55", "00:27:19", "00:28:45", "00:29:AB",
        "00:2A:70", "00:2B:0D", "00:2C:44", "00:2D:76", "00:2E:3C",
        
        # Lenovo
        "00:21:86", "00:22:68", "00:23:24", "00:24:81", "00:25:64",
        "00:26:55", "00:27:19", "00:28:45", "00:29:AB", "00:2A:70",
        "00:2B:0D", "00:2C:44", "00:2D:76", "00:2E:3C", "00:2F:9A",
        
        # Apple (для macOS)
        "00:1B:63", "00:1C:42", "00:1D:4F", "00:1E:52", "00:1F:5B",
        "00:21:E9", "00:22:41", "00:23:12", "00:23:DF", "00:24:36",
        "00:25:00", "00:25:4B", "00:25:BC", "00:26:08", "00:26:4A",
        "00:26:B0", "00:26:BB", "00:27:10", "00:27:3E", "00:27:8E"
    ]
    
    # Выбираем случайный OUI
    oui = random.choice(real_hardware_ouis)
    
    # Генерируем последние 3 байта (6 hex символов)
    # Используем secrets для криптографически стойкой генерации
    last_three_bytes = secrets.token_hex(3)
    
    # Форматируем как MAC-адрес
    mac_address = f"{oui}:{last_three_bytes[0:2]}:{last_three_bytes[2:4]}:{last_three_bytes[4:6]}"
    
    return mac_address


def get_adspower_api_url():
    """Автоматически определяет URL API AdsPower"""
    # Проверяем переменную окружения для ручного указания порта
    manual_port = os.environ.get('ADSPOWER_PORT')
    if manual_port:
        try:
            port = int(manual_port)
            api_url = f"http://127.0.0.1:{port}"
            response = requests.get(f"{api_url}/api/v1/user/list", timeout=2)
            if response.status_code == 200:
                print(f"✅ Используем порт из переменной окружения: {port}")
                return api_url
            else:
                print(f"⚠️ Порт {port} из переменной окружения недоступен")
        except:
            print(f"⚠️ Неверный порт в переменной окружения: {manual_port}")
    
    # Расширенный список возможных портов AdsPower
    possible_ports = [
        # Стандартные порты
        50325, 50326, 50327, 50328, 50329,
        # Альтернативные порты
        50330, 50331, 50332, 50333, 50334, 50335,
        # Другие возможные порты
        50320, 50321, 50322, 50323, 50324,
        50336, 50337, 50338, 50339, 50340,
        # Пользовательские порты (если кто-то изменил)
        50300, 50301, 50302, 50303, 50304, 50305,
        50310, 50311, 50312, 50313, 50314, 50315
    ]
    
    print("🔍 Ищу AdsPower API...")
    
    for port in possible_ports:
        api_url = f"http://127.0.0.1:{port}"
        try:
            # Проверяем доступность API
            response = requests.get(f"{api_url}/api/v1/user/list", timeout=1)
            if response.status_code == 200:
                print(f"✅ Найден AdsPower API на порту {port}")
                return api_url
        except:
            continue
    
    # Если не найден, пробуем сканировать диапазон портов
    print("🔍 Сканирую диапазон портов 50300-50400...")
    for port in range(50300, 50401):
        api_url = f"http://127.0.0.1:{port}"
        try:
            response = requests.get(f"{api_url}/api/v1/user/list", timeout=0.5)
            if response.status_code == 200:
                print(f"✅ Найден AdsPower API на порту {port}")
                return api_url
        except:
            continue
    
    # Если все еще не найден, просим пользователя указать порт
    print("❌ AdsPower API не найден автоматически!")
    print("💡 Возможные решения:")
    print("   1. Убедитесь, что AdsPower запущен")
    print("   2. Проверьте, что API включен в настройках")
    print("   3. Укажите порт вручную в коде")
    
    # Возвращаем стандартный порт как fallback
    return "http://127.0.0.1:50325"


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
    api_url = get_adspower_api_url()
    
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
    
    # URL API AdsPower (автоматическое определение порта)
    api_url = get_adspower_api_url()
    
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
        proxy = random.choice(proxies)
        print(f"✅ Использую случайный прокси: {proxy.get('type')}://{proxy.get('host')}:{proxy.get('port')}")
    
    # Проверяем тип прокси (может влиять на детекцию устройства)
    proxy_type = proxy.get('type', '').lower()
    proxy_host = proxy.get('host', '')
    
    print(f"🔍 АНАЛИЗ ПРОКСИ:")
    print(f"   Тип: {proxy_type}")
    print(f"   Хост: {proxy_host}")
    
    # Предупреждаем о возможных проблемах
    if 'mobile' in proxy_host.lower() or '4g' in proxy_host.lower() or '5g' in proxy_host.lower():
        print(f"⚠️ ВНИМАНИЕ: Прокси может быть мобильным - это может влиять на детекцию устройства!")
    
    proxy_id = proxy.get('proxy_id')
    
    # Настройки браузера и ОС из конфига или случайные
    browser_setting = profile_config.get("browser", "random")
    os_setting = profile_config.get("os", "random")
    
    if browser_setting == "random":
        browser = get_random_browser()
    else:
        browser = browser_setting
    
    if os_setting == "random":
        os = get_random_os()
    else:
        os = os_setting
    
    # Проверяем совместимость браузера и ОС
    if browser == "safari" and os != "macOS":
        print(f"⚠️ Safari несовместим с {os}, принудительно меняю на macOS")
        os = "macOS"
    elif browser == "edge" and os == "Linux":
        print(f"⚠️ Edge на Linux может быть нестабильным, меняю на Chrome")
        browser = "chrome"
    
    # Генерируем реалистичную MAC-адрес
    mac_address = generate_realistic_mac_address()
    
    print(f"🌐 Браузер: {browser}")
    print(f"💻 ОС: {os}")
    print(f"🔧 MAC-адрес: {mac_address}")
    print(f"🔧 ПРИНУДИТЕЛЬНО: mobile=0, touch=0, device_type=desktop")
    print(f"🔧 AdsPower автоматически настроит фингерпринт для {browser} на {os}")
    
    # Данные для создания профиля
    profile_data = {
        "name": profile_config["name"],
        "group_id": "0",
        "remark": "Создан через скрипт (ПРИНУДИТЕЛЬНО ДЕСКТОП)",
        "proxyid": proxy_id,  # Используем ID существующего прокси
        
        # ПРИНУДИТЕЛЬНЫЕ настройки для предотвращения мобильных профилей
        "device_type": "desktop",  # ПРИНУДИТЕЛЬНО: десктоп
        "is_mobile": False,  # ПРИНУДИТЕЛЬНО: НЕ мобильное
        
        # Куки для профиля
        "cookies": profile_config.get("cookies", []),
        
        # Настройки фингерпринта
        "fingerprint_config": {
            "automatic_timezone": "1",  # Автоматический часовой пояс по IP
            "webrtc": "proxy",  # Подмена IP через прокси 
            "language": ["ar-AE", "ar"],  # Язык арабский (ОАЭ)
            "page_language_switch": "0",  # Отключаем автоматический язык страницы
            "page_language": "ar-AE",  # Арабский язык страницы (ОАЭ)
            "timezone": "Asia/Dubai",  # Часовой пояс ОАЭ
            "webgl_image": "1",  # Включить WebGL image fingerprint
            "webgl": "3",  # Случайный WebGL metadata
            "audio": "1",
            
            # Настройки браузера и ОС (ПРИНУДИТЕЛЬНО ТОЛЬКО ДЕСКТОПНЫЕ)
            "browser": browser,  # Случайный браузер (chrome, firefox, edge, safari)
            "os": os,  # ПРИНУДИТЕЛЬНО: Windows, macOS, Linux (НЕ Android!)
            "platform": os,  # Платформа (обычно совпадает с ОС)
            
            # Дополнительные принудительные настройки для десктопа
            "mobile": "0",  # ПРИНУДИТЕЛЬНО: НЕ мобильное устройство
            "touch": "0",  # ПРИНУДИТЕЛЬНО: НЕ сенсорный экран
            "device_type": "desktop",  # ПРИНУДИТЕЛЬНО: десктопное устройство
            
            # MAC-адрес для реалистичности
            "mac_address": mac_address,  # Реалистичная MAC-адрес от настоящего железа
            
            # Дополнительные настройки для реалистичности
            "hardware_concurrency": random.choice(["2", "3", "4", "6", "8", "10", "12", "16", "20", "24", "32", "64"]),  # Количество ядер CPU
            "device_memory": str(random.choice([4, 8, 16, 32])),  # Объем RAM в GB
            "screen_resolution": random.choice(["1920_1080", "2560_1440", "3840_2160", "3440_1440"]),  # Современные разрешения экрана
            "color_depth": str(random.choice([24, 32])),  # Глубина цвета
            "canvas": "1",  # Включить canvas fingerprint
            "fonts": ["Arial", "Calibri", "Cambria", "Times New Roman"],  # Список шрифтов
            
            # Настройки масштабирования для правильного отображения
            "device_scale_factor": "1",  # Масштаб устройства (1 = 100%)
            "pixel_ratio": "1",  # Соотношение пикселей
            "zoom_level": "0",  # Уровень масштабирования (0 = 100%)
            
            # WebGL Vendor для реалистичности
            "webgl_vendor": random.choice([
                "Google Inc. (Intel)",
                "Google Inc. (NVIDIA Corporation)",
                "Google Inc. (AMD)",
                "Google Inc. (Intel Inc.)"
            ]),
            
            # WebGL Renderer для реалистичности
            "webgl_renderer": random.choice([
                "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11-27.20.100.8336)",
                "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11-30.0.14.7111)",
                "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11-30.0.14.7111)",
                "ANGLE (Intel, Intel(R) Iris Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11-30.0.14.7111)"
            ])
        }
    }
    
    print(f"Создаю профиль: {profile_config['name']}")
    
    # Логируем куки
    cookies_count = len(profile_config.get("cookies", []))
    print(f"🍪 Добавляю {cookies_count} куки в профиль")
    
    # Логируем ключевые настройки фингерпринта
    fingerprint = profile_data["fingerprint_config"]
    print(f"🔍 ОТПРАВЛЯЕМ В ADSPOWER:")
    print(f"   OS: {fingerprint['os']}")
    print(f"   Platform: {fingerprint['platform']}")
    print(f"   Mobile: {fingerprint['mobile']}")
    print(f"   Touch: {fingerprint['touch']}")
    print(f"   Device Type: {fingerprint['device_type']}")
    
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
                print(f"   MAC-адрес: {mac_address}")
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
    api_url = get_adspower_api_url()
    
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
    api_url = get_adspower_api_url()
    
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
