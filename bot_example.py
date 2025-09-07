import time
import os
import random
import string
import requests
import json
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import tempfile
import shutil
import sys
import argparse as _argparse
from selenium.webdriver.common.keys import Keys


# Функция для получения debug port от AdsPower
def get_adspower_debug_port():
	"""Получает debug port запущенного браузера AdsPower"""
	import os
	
	# Сначала проверяем переменную окружения
	debug_port = os.environ.get('ADSPOWER_DEBUG_PORT')
	if debug_port:
		print(f"✅ Использую debug port из переменной окружения: {debug_port}")
		return debug_port
	
	api_url = "http://127.0.0.1:50325"
	
	# Попробуем разные endpoints для получения активных браузеров
	endpoints = [
		"/api/v1/browser/active",
		"/api/v2/browser-profile/active", 
		"/api/v1/user/list",
		"/api/v2/browser-profile/list"
	]
	
	for endpoint in endpoints:
		try:
			print(f"🔍 Пробую получить активные браузеры: {endpoint}")
			response = requests.get(f"{api_url}{endpoint}")
			
			if response.status_code == 200:
				result = response.json()
				print(f"   📄 Ответ: {result}")
				
				if result.get("code") == 0:
					# Попробуем разные структуры данных
					data = result.get("data", {})
					active_browsers = data.get("list", []) or data.get("browsers", []) or data.get("data", [])
					
					if active_browsers:
						# Берем первый активный браузер
						browser = active_browsers[0]
						debug_port = browser.get("debug_port")
						
						if debug_port:
							print(f"✅ Найден активный браузер AdsPower с debug port: {debug_port}")
							return debug_port
						else:
							print("❌ Debug port не найден в активном браузере")
					else:
						print("❌ Нет активных браузеров в ответе")
				else:
					print(f"❌ Ошибка API: {result.get('msg')}")
			else:
				print(f"❌ HTTP ошибка: {response.status_code}")
				
		except Exception as e:
			print(f"❌ Ошибка для {endpoint}: {e}")
	
	print("❌ Не удалось найти активные браузеры")
	return None


def get_adspower_webdriver_path():
	"""Получает путь к WebDriver от AdsPower"""
	import os
	
	# Сначала проверяем переменную окружения
	webdriver_path = os.environ.get('ADSPOWER_WEBDRIVER_PATH')
	if webdriver_path:
		print(f"✅ Использую WebDriver path из переменной окружения: {webdriver_path}")
		return webdriver_path
	
	# Если не найден, возвращаем None (будет использован автоматический)
	return None


# Данные пользователя теперь передаются из главного файла

# Генерация случайного email
def generate_email(name, last_name):
	# Генерируем 4 случайные буквы
	prefix = ''.join(random.choices(string.ascii_letters, k=4))
	# Генерируем случайное число от 10 до 99
	number = random.randint(10, 99)
	# Генерируем 7 случайных букв
	suffix = ''.join(random.choices(string.ascii_letters, k=7))
	return f"{prefix}{name}{last_name}{number}{suffix}@gmail.com"

# Генерация случайного пароля
def generate_password():
	return ''.join(random.choices(string.ascii_letters + string.digits, k=14))

# Фиксированный адрес для всех регистраций (ОАЭ)
ADDRESS = "Apt4208,42 floor"
ADDRESS_LINE2 = "PrincessTower"

# Фиксированные данные для всех регистраций
CITY = "Dubai"
PROVINCE = "Dubai Marina"
POSTAL_CODE = "00000"  # В Дубае может не требоваться; используем 00000 при необходимости
PHONE = "+971508698540"

# Массив карт (номер, срок действия, CVC)
# Массивы карт и имен теперь в главном файле

# Фиксированные данные
password = "TestPassword123!"

# Данные теперь передаются из главного файла

# Функции для работы с данными удалены - данные передаются извне

# Файлы логов
LOG_FILE = "reports.log"
SUCCESS_FILE = "successful_registrations.txt"

# Функция для записи в лог
def log_message(message):
	timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	with open(LOG_FILE, "a", encoding="utf-8") as log:
		log.write(f"\n[{timestamp}] {message}\n")
	print(message)

# Функция для сохранения успешной регистрации
def save_successful_registration(user_data, order_status_link, order_number=None):
	timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	success_data = {
		"timestamp": timestamp,
		"email": user_data["email"],
		"password": user_data["password"],
		"first_name": user_data["first_name"],
		"last_name": user_data["last_name"],
		"card_number": user_data["card_number"],
		"order_status_link": order_status_link,
		"order_number": order_number
	}
	
	# Сохраняем в файл успешных регистраций
	with open(SUCCESS_FILE, "a", encoding="utf-8") as f:
		f.write(f"\n{'='*50}\n")
		f.write(f"УСПЕШНАЯ РЕГИСТРАЦИЯ - {timestamp}\n")
		f.write(f"{'='*50}\n")
		f.write(f"Email: {success_data['email']}\n")
		f.write(f"Password: {success_data['password']}\n")
		f.write(f"Name: {success_data['first_name']} {success_data['last_name']}\n")
		f.write(f"Card: {success_data['card_number']}\n")
		f.write(f"Order Link: {success_data['order_status_link']}\n")
		if order_number:
			f.write(f"Order Number: {order_number}\n")
		f.write(f"{'='*50}\n")
	
	# Также логируем в основной лог
	log_message(f"[SUCCESS] Сохранена успешная регистрация: {user_data['email']}")


def save_artifacts(driver, prefix: str) -> None:
	ts = datetime.now().strftime("%Y%m%d_%H%M%S")
	html_name = f"{prefix}_{ts}.html"
	png_name = f"{prefix}_{ts}.png"
	try:
		with open(html_name, "w", encoding="utf-8") as f:
			f.write(driver.page_source)
	except Exception:
		pass
	try:
		driver.save_screenshot(png_name)
	except Exception:
		pass
	try:
		log_message(f"[DEBUG] Saved artifacts: {html_name}, {png_name}")
	except Exception:
		pass

def save_successful_order(user_data, order_details=None):
	"""Сохраняет данные успешного заказа в файл"""
	try:
		# Создаем папку для успешных заказов
		success_dir = "successful_orders"
		if not os.path.exists(success_dir):
			os.makedirs(success_dir)
		
		# Создаем имя файла с датой и временем
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		filename = f"{success_dir}/order_{timestamp}.txt"
		
		# Подготавливаем данные для сохранения
		order_info = {
			"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
			"email": user_data.get("email", "N/A"),
			"password": user_data.get("password", "N/A"),
			"first_name": user_data.get("first_name", "N/A"),
			"last_name": user_data.get("last_name", "N/A"),
			"address": user_data.get("address", "N/A"),
			"city": user_data.get("city", "N/A"),
			"province": user_data.get("province", "N/A"),
			"phone": user_data.get("phone", "N/A"),
			"card_number": user_data.get("card_number", "N/A"),
			"card_expiry": user_data.get("card_expiry", "N/A"),
			"card_cvc": user_data.get("card_cvc", "N/A"),
			"card_name": user_data.get("card_name", "N/A")
		}
		
		# Добавляем дополнительные детали заказа если есть
		if order_details:
			order_info.update(order_details)
		
		# Сохраняем в текстовый файл
		with open(filename, 'w', encoding='utf-8') as f:
			f.write("=== УСПЕШНЫЙ ЗАКАЗ WHOOP ===\n")
			f.write(f"Дата и время: {order_info['timestamp']}\n")
			f.write("=" * 50 + "\n\n")
			
			f.write("ДАННЫЕ АККАУНТА:\n")
			f.write(f"Email: {order_info['email']}\n")
			f.write(f"Пароль: {order_info['password']}\n\n")
			
			f.write("ДАННЫЕ ДОСТАВКИ:\n")
			f.write(f"Имя: {order_info['first_name']}\n")
			f.write(f"Фамилия: {order_info['last_name']}\n")
			f.write(f"Адрес: {order_info['address']}\n")
			f.write(f"Город: {order_info['city']}\n")
			f.write(f"Область: {order_info['province']}\n")
			f.write(f"Телефон: {order_info['phone']}\n\n")
			
			f.write("ДАННЫЕ КАРТЫ:\n")
			f.write(f"Номер карты: {order_info['card_number']}\n")
			f.write(f"Срок действия: {order_info['card_expiry']}\n")
			f.write(f"CVC: {order_info['card_cvc']}\n")
			f.write(f"Имя на карте: {order_info['card_name']}\n\n")
			
			if order_details:
				f.write("ДОПОЛНИТЕЛЬНЫЕ ДЕТАЛИ:\n")
				for key, value in order_details.items():
					f.write(f"{key}: {value}\n")
		
		print(f"✅ Успешный заказ сохранен: {filename}")
		return filename
		
	except Exception as e:
		print(f"❌ Ошибка сохранения успешного заказа: {e}")
		return None


def click_safely(driver, wait, locators, name: str = "button"):
	for locator in locators:
		try:
			el = wait.until(EC.presence_of_element_located(locator))
			
			# Закрываем баннер куки если он есть
			try:
				cookie_banner = driver.find_element(By.CSS_SELECTOR, "#onetrust-accept-btn-handler, .ot-sdk-show-settings, [data-testid*='cookie']")
				if cookie_banner.is_displayed():
					print(f"-------Закрываем баннер куки перед кликом по {name}...-------")
					cookie_banner.click()
					time.sleep(2)
			except:
				pass
			
			try:
				driver.execute_script(
					"arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
					el,
				)
			except Exception:
				pass
			time.sleep(2)
			el = wait.until(EC.visibility_of_element_located(locator))

			try:
				attrs = []
				for a in ["id", "name", "data-testid", "aria-disabled", "disabled"]:
					try:
						attrs.append(f"{a}={el.get_attribute(a)}")
					except Exception:
						pass
				log_message(
					f"[DEBUG] Try click {name} via {locator}: displayed={el.is_displayed()} enabled={el.is_enabled()} attrs={' '.join(attrs)}"
				)
			except Exception:
				pass

			# Пробуем обычный клик
			try:
				el.click()
				print(f"✅ Обычный клик по {name} прошел!")
				return True
			except Exception as e:
				print(f"❌ Обычный клик по {name} не прошел: {e}")
				# Пробуем клик через JavaScript
				try:
					driver.execute_script("arguments[0].click();", el)
					print(f"✅ JavaScript клик по {name} прошел!")
					return True
				except Exception as e2:
					print(f"❌ JavaScript клик по {name} не прошел: {e2}")
					# Пробуем ActionChains
					try:
						ActionChains(driver).move_to_element(el).click().perform()
						print(f"✅ ActionChains клик по {name} прошел!")
						return True
					except Exception as e3:
						print(f"❌ ActionChains клик по {name} не прошел: {e3}")
						save_artifacts(driver, f"whoop_click_failed_{name}")
						continue
		except Exception as e:
			try:
				log_message(f"[DEBUG] Locator not clickable {name} via {locator}: {e}")
			except Exception:
				pass
			save_artifacts(driver, f"whoop_locator_unavailable_{name}")
		finally:
			try:
				driver.switch_to.default_content()
			except Exception:
				pass
	return False


# Функция выполнения регистрации
def attempt_registration(reg_num, attempt=0, order_data=None):
	if order_data:
		user_data = order_data
	else:
		# Если данные не переданы, создаем тестовые данные
		user_data = {
			"email": f"test{random.randint(1000, 9999)}@example.com",
			"password": "password123",
			"first_name": "John",
			"last_name": "Doe",
			"address": "123 Main Street",
			"city": "Dubai",
			"province": "Dubai",
			"phone": "+971501234567",
			"card_number": "4111111111111111",
			"card_expiry": "12/25",
			"card_cvc": "123",
			"card_name": "John Doe"
		}
	
	# Подключаемся к уже запущенному браузеру AdsPower
	debug_port = get_adspower_debug_port()
	if not debug_port:
		print("❌ Не удалось получить debug port от AdsPower!")
		return False
	
	options = webdriver.ChromeOptions()
	# Подключаемся к удаленному браузеру AdsPower
	options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
	
	# Получаем путь к WebDriver от AdsPower
	webdriver_path = get_adspower_webdriver_path()
	
	if webdriver_path:
		print(f"🔧 Использую WebDriver от AdsPower: {webdriver_path}")
		from selenium.webdriver.chrome.service import Service as ChromeService
		service = ChromeService(executable_path=webdriver_path)
		driver = webdriver.Chrome(service=service, options=options)
	else:
		print("⚠️ WebDriver от AdsPower не найден, используем автоматический")
		from selenium.webdriver.chrome.service import Service as ChromeService
		from webdriver_manager.chrome import ChromeDriverManager
		service = ChromeService(ChromeDriverManager().install())
		driver = webdriver.Chrome(service=service, options=options)
	wait = WebDriverWait(driver, 10)

	try:
		print(f"-------Начинаем регистрацию #{reg_num}-------")
		log_message(f"Используем данные: {user_data['email']} - {user_data['first_name']} {user_data['last_name']}")

		print("-------Открываем сайт Whoop...-------")
		driver.get("https://join.whoop.com/uae/en/")
		time.sleep(18)  # Увеличиваем время ожидания

		print("-------Нажимаем кнопку 'Start with PEAK'...-------")
		
		# Ждем появления кнопки
		start_peak_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@data-testid='membership-PEAK-card-cta']")))
		print("✅ Кнопка найдена!")
		
		# Закрываем баннер куки если он есть
		try:
			cookie_banner = driver.find_element(By.CSS_SELECTOR, "#onetrust-accept-btn-handler, .ot-sdk-show-settings, [data-testid*='cookie']")
			if cookie_banner.is_displayed():
				print("-------Закрываем баннер куки...-------")
				cookie_banner.click()
				time.sleep(5)
		except:
			pass
		
		# Прокручиваем к кнопке
		driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", start_peak_button)
		time.sleep(5)
		
		# Пробуем обычный клик
		try:
			start_peak_button.click()
			print("✅ Обычный клик прошел!")
		except Exception as e:
			print(f"❌ Обычный клик не прошел: {e}")
			# Пробуем клик через JavaScript
			try:
				driver.execute_script("arguments[0].click();", start_peak_button)
				print("✅ JavaScript клик прошел!")
			except Exception as e2:
				print(f"❌ JavaScript клик не прошел: {e2}")
				# Пробуем ActionChains
				try:
					from selenium.webdriver.common.action_chains import ActionChains
					ActionChains(driver).move_to_element(start_peak_button).click().perform()
					print("✅ ActionChains клик прошел!")
				except Exception as e3:
					print(f"❌ ActionChains клик не прошел: {e3}")
					raise Exception("Все способы клика не сработали")
		
		time.sleep(15)

		print("-------Нажимаем 'Continue'...-------")
		
		# Используем универсальную функцию клика
		continue_locators = [
			(By.XPATH, "//button[contains(text(), 'Continue')]")
		]
		
		if not click_safely(driver, wait, continue_locators, name="continue-button"):
			raise Exception("Кнопка Continue не найдена или не кликабельна")
		
		time.sleep(15)

		print("-------Выбираем Trial-membership...-------")
		
		# Используем универсальную функцию клика
		trial_locators = [
			(By.XPATH, "//button[@data-testid='trial-membership']")
		]
		
		if not click_safely(driver, wait, trial_locators, name="trial-membership"):
			raise Exception("Кнопка Trial-membership не найдена или не кликабельна")
		
		time.sleep(15)

		print("-------Нажимаем Check Out...-------")
		
		# Используем универсальную функцию клика
		checkout_locators = [
			(By.XPATH, "//button[@data-testid='cart-continueButton']")
		]
		
		if not click_safely(driver, wait, checkout_locators, name="checkout-button"):
			raise Exception("Кнопка Check Out не найдена или не кликабельна")
		
		time.sleep(15)

		print("-------Заполняем форму регистрации...-------")
		email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
		email_field.send_keys(user_data["email"])
		log_message(f"Email: {user_data['email']}")
		time.sleep(1)

		password_field = driver.find_element(By.NAME, "password")
		password_field.send_keys(user_data["password"])
		time.sleep(1)

		confirm_password = driver.find_element(By.NAME, "confirm")
		confirm_password.send_keys(user_data["password"])
		time.sleep(1)

		print("-------Нажимаем 'Next' после регистрации...-------")
		
		# Используем универсальную функцию клика
		next_locators = [
			(By.XPATH, "//button[@data-testid='next-button-create-account']")
		]
		
		if not click_safely(driver, wait, next_locators, name="next-button"):
			raise Exception("Кнопка Next не найдена или не кликабельна")
		
		time.sleep(15)

		print("-------Заполняем адрес доставки...-------")
		first_name = wait.until(EC.presence_of_element_located((By.ID, "first_name")))
		first_name.send_keys(user_data["first_name"])
		time.sleep(1)

		last_name = driver.find_element(By.ID, "last_name")
		last_name.send_keys(user_data["last_name"])
		time.sleep(1)

		print("-------Вводим адрес...-------")
		address = wait.until(EC.presence_of_element_located((By.ID, "line1")))
		address.send_keys(user_data["address"])
		time.sleep(1)

		try:
			address2 = driver.find_element(By.ID, "line2")
			address2.send_keys(user_data["address_line2"])
			time.sleep(1)
		except Exception:
			pass

		print("-------Вводим город...-------")
		city_el = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='City'][role='combobox']"))
		)
		city_el.click()
		city_el.send_keys(user_data["city"])
		city_el.send_keys(Keys.ENTER)
		time.sleep(1)

		print("-------Вводим Area/District...-------")
		try:
			# Поле Area/District (ищем по data-testid "Area/District")
			area_district = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='Area/District']")))
			area_district.clear()  # Очищаем поле
			area_district.send_keys(user_data["province"])  # Используем значение из province для Area/District
			print(f"✅ Введено в Area/District: {user_data['province']}")
		except Exception as e:
			print(f"❌ Ошибка ввода Area/District: {e}")
			# Пробуем альтернативные способы
			try:
				area_district = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='province']")))
				area_district.clear()
				area_district.send_keys(user_data["province"])
				print(f"✅ Введено в Area/District (через province): {user_data['province']}")
			except Exception as e2:
				print(f"❌ Через province не сработал: {e2}")
				try:
					area_district = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Command input']")))
					area_district.clear()
					area_district.send_keys(user_data["province"])
					print(f"✅ Введено в Area/District (через aria-label): {user_data['province']}")
				except Exception as e3:
					print(f"❌ Все способы не сработали: {e3}")
		time.sleep(1)

		print("-------Вводим телефон...-------")
		phone = wait.until(EC.presence_of_element_located((By.ID, "phone")))
		phone.send_keys(user_data["phone"])
		time.sleep(1)

		print("-------Нажимаем 'Next' после ввода адреса...-------")
		try:
			# Используем универсальную функцию клика
			next_address_locators = [
				(By.XPATH, "//button[@data-testid='next-button-shipping-address']")
			]
			
			if not click_safely(driver, wait, next_address_locators, name="next-address-button"):
				raise Exception("Кнопка Next Address не найдена или не кликабельна")
			
			time.sleep(15)
		except Exception:
			pass

		# Проверяем, что перешли к следующему шагу; иначе — робастный клик и диагностика
		try:
			# Ищем любую из двух кнопок
			WebDriverWait(driver, 5).until(
				EC.any_of(
					EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='next-button-shipping-method']")),
					EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='confirm-address']"))
				)
			)
		except Exception:
			print("-------Повторный надёжный клик 'Next' адреса...-------")
			next_locators = [
				(By.XPATH, "//button[@data-testid='next-button-shipping-address']"),
				(By.XPATH, "//button[@type='submit' and .//span[contains(., 'Next')]]"),
				(By.XPATH, "//button[contains(., 'Next')]")
			]
			if not click_safely(driver, wait, next_locators, name="next-shipping-address"):
				# Диагностика: какие поля невалидны
				for fld in driver.find_elements(By.CSS_SELECTOR, "[aria-invalid='true'], .aria-[invalid=true]"):
					fid = fld.get_attribute("id") or fld.get_attribute("name") or "<no-id>"
					log_message(f"[ADDRESS_INVALID] {fid}")
				raise Exception("Next after address not clickable")
			time.sleep(15)

		# СНАЧАЛА проверяем, есть ли кнопка confirm-address (подтверждение адреса)
		print("-------Проверяем, нужно ли подтвердить адрес...-------")
		try:
			confirm_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='confirm-address']")))
			print("✅ Найдена кнопка confirm-address - подтверждаем адрес!")
			
			driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", confirm_button)
			time.sleep(2)
			
			driver.execute_script("arguments[0].click();", confirm_button)
			print("✅ JavaScript клик по confirm-address прошел!")
			time.sleep(15)
			
		except Exception as e:
			print(f"ℹ️ Кнопка confirm-address не найдена: {e}")

		# ТЕПЕРЬ выбираем метод доставки
		print("-------Выбираем метод доставки и нажимаем 'Weiter'...-------")
		
		# Специальная обработка для кнопки shipping method (она отправляет форму)
		try:
			shipping_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='next-button-shipping-method']")))
			print("✅ Кнопка shipping method найдена!")
			
			# Прокручиваем к кнопке
			driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", shipping_button)
			time.sleep(15)
			
			# Пробуем обычный клик
			try:
				shipping_button.click()
				print("✅ Обычный клик по shipping method прошел!")
			except Exception as e:
				print(f"❌ Обычный клик не прошел: {e}")
				# Пробуем клик через JavaScript
				try:
					driver.execute_script("arguments[0].click();", shipping_button)
					print("✅ JavaScript клик по shipping method прошел!")
				except Exception as e2:
					print(f"❌ JavaScript клик не прошел: {e2}")
					# Пробуем отправить форму напрямую
					try:
						driver.execute_script("document.getElementById('shipping-method-form').submit();")
						print("✅ Отправка формы shipping method прошел!")
					except Exception as e3:
						print(f"❌ Отправка формы не прошел: {e3}")
						raise Exception("Все способы клика по shipping method не сработали")
			
		except Exception as e:
			print(f"❌ Кнопка shipping method не найдена: {e}")
			raise Exception("Кнопка shipping method не найдена")
		
		time.sleep(15)

		print("-------Ищем iframe с полями карты-------")
		iframe_index = None
		iframes = driver.find_elements(By.TAG_NAME, "iframe")

		for index, iframe in enumerate(iframes):
			try:
				driver.switch_to.frame(iframe)
				inner_html = driver.execute_script("return document.body.innerHTML")

				if "cardnumber" in inner_html and "exp-date" in inner_html and "cvc" in inner_html:
					iframe_index = index
					print(f"Найден нужный iframe: #{iframe_index}")
					driver.switch_to.default_content()
					break

				driver.switch_to.default_content()
			except Exception as e:
				print(f"Ошибка при проверке iframe[{index}]: {e}")
				driver.switch_to.default_content()

		if iframe_index is None:
			log_message("Не удалось найти iframe с полями карты")
			return  # Прерываем попытку

		# Вводим данные карты
		try:
			driver.switch_to.frame(iframes[iframe_index])

			wait.until(EC.presence_of_element_located((By.NAME, "cardnumber"))).send_keys(user_data["card_number"])
			print("Ввел номер карты")

			wait.until(EC.presence_of_element_located((By.NAME, "exp-date"))).send_keys(user_data["card_expiry"])
			print("Ввел срок действия")

			wait.until(EC.presence_of_element_located((By.NAME, "cvc"))).send_keys(user_data["card_cvc"])
			print("Ввел CVC")

			driver.switch_to.default_content()
		except Exception as e:
			log_message(f"Ошибка при вводе данных карты: {e}")
			driver.switch_to.default_content()

		print("-------Нажимаем 'Place Order'...-------")
		try:
			# Используем универсальную функцию клика
			place_order_locators = [
				(By.XPATH, "//button[@data-testid='complete-purchase']")
			]
			
			if click_safely(driver, wait, place_order_locators, name="place-order-button"):
				log_message("Кнопка Place Order нажата")
			else:
				raise Exception("Кнопка Place Order не найдена")
			time.sleep(20)  # Ждём обработку платежа
		except Exception as e:
			log_message(f"Ошибка нажатия Place Order: {e}")
			# Пробуем альтернативные селекторы
			try:
				# Используем универсальную функцию клика
				alt_place_order_locators = [
					(By.XPATH, "//button[contains(text(), 'Place Order')]")
				]
				
				if click_safely(driver, wait, alt_place_order_locators, name="alt-place-order-button"):
					log_message("Place Order нажат альтернативным способом")
				else:
					raise Exception("Альтернативная кнопка Place Order не найдена")
				time.sleep(3)
			except:
				log_message("Не удалось нажать Place Order")
				# Робастная попытка клика с диагностикой
				click_safely(
					driver,
					wait,
					[
						(By.XPATH, "//button[@data-testid='complete-purchase']"),
						(By.XPATH, "//button[contains(text(), 'Place Order')]")
					],
					name="complete-purchase"
				)

		try:
			# Ждём появления ошибки на сайте (если она есть)
			error_message = WebDriverWait(driver, 5).until(
				EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'text-red-a400')]"))
			).text

			# Логируем ошибку
			log_message(f"[UNSUCCESSFUL] Ошибка при оплате: {error_message}, Карта: {user_data['card_number']}")

		except:
			# Если ошибка не появилась, значит всё нормально
			log_message("[SUCCESSFUL]Ошибок при оплате не обнаружено")

		print("-------Проверяем, прошёл ли платеж...-------")
		try:
			order_status_link = wait.until(
				EC.presence_of_element_located(
					(By.XPATH, "//a[contains(@href, 'orderstatus.whoop.com')]"))).get_attribute(
				"href")
			log_message(f"[SUCCESSFUL]Платёж успешен!Email: {user_data['email']}, Pass:{user_data['password']}, Карта: {user_data['card_number']}, Ссылка на заказ: {order_status_link}")
			
			# Сохраняем успешную регистрацию
			save_successful_registration(user_data, order_status_link)
			
			# Сохраняем успешный заказ в отдельную папку
			order_details = {
				"order_status_link": order_status_link,
				"payment_status": "SUCCESS",
				"transaction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			}
			save_successful_order(user_data, order_details)

			print("-------Переходим на страницу заказа...25 сек-------")
			driver.get(order_status_link)
			time.sleep(20)

			print("-------Ищем номер заказа...-------")
			order_number_element = None

			# Пробуем сначала найти по классу
			try:
				order_number_element = WebDriverWait(driver, 10).until(
					EC.presence_of_element_located((By.CLASS_NAME, "gpSbjZ"))
				)
			except:
				pass  # Если не нашли по классу, пробуем другой способ

			# Если не нашли по классу, ищем по тексту
			if not order_number_element:
				try:
					order_number_element = WebDriverWait(driver, 10).until(
						EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Order number:')]"))
					)
				except:
					pass

			# Если номер заказа не найден, пробуем кликнуть Детали
			if not order_number_element:
				print("Номер заказа не найден, пробуем нажать Детали...")
				try:
					quittung_button = wait.until(
						EC.element_to_be_clickable((By.XPATH, "//a[@data-test-id='view-order-details']"))
					)
					quittung_button.click()
					time.sleep(10)  # Ждем 3 секунды

					print("-------Пробуем найти номер заказа в новом блоке...-------")
					order_number_element = wait.until(
						EC.presence_of_element_located((By.CLASS_NAME, "order-details_shipItem__ln8a9"))
					)
				except:
					pass

			# Если нашли, логируем и обновляем данные
			if order_number_element:
				order_number = order_number_element.text.split(":")[-1].strip()
				log_message(f"[SUCCESSFUL]Номер заказа: {order_number}")
				# Обновляем данные успешной регистрации с номером заказа
				save_successful_registration(user_data, order_status_link, order_number)
				
				# Обновляем файл заказа с номером заказа
				order_details = {
					"order_status_link": order_status_link,
					"order_number": order_number,
					"payment_status": "SUCCESS",
					"transaction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				}
				save_successful_order(user_data, order_details)
			else:
				print("Номер заказа не найден! Сохраняем HTML для отладки.")
				page_source = driver.page_source
				with open("whoop_order_status.html", "w", encoding="utf-8") as f:
					f.write(page_source)
				log_message(f"[BUT]: номер заказа не найден!")

		except Exception:
			log_message(f"[UNSUCCESSFUL]Ошибка: Регистрация не прошла. Карта: {user_data['card_number']}")
			return False  # Неудачная регистрация

		log_message(f"Регистрация #{reg_num + 1} завершена для {user_data['email']}")
		return True  # Успешная регистрация

	except Exception as e:
		print(f"-------Произошла ошибка: {e}-------")
		try:
			with open("whoop_error_page.html", "w", encoding="utf-8") as f:
				f.write(driver.page_source)
			log_message("[DEBUG] Saved whoop_error_page.html")
		except Exception:
			pass
		try:
			driver.save_screenshot("whoop_error_page.png")
			log_message("[DEBUG] Saved whoop_error_page.png")
		except Exception:
			pass
		return False  # Неудачная регистрация

	finally:
		print("-------Закрываем браузер...-------")
		time.sleep(1)
		try:
			driver.quit()
		finally:
			# НЕ удаляем профиль - он управляется AdsPower
			pass


def run_single_registration(order_data):
	"""Запускает одну регистрацию с переданными данными"""
	print(f"🚀 Запуск регистрации с данными:")
	print(f"📧 Email: {order_data['email']}")
	print(f"💳 Карта: {order_data['card_number']}")
	print(f"👤 Имя: {order_data['first_name']} {order_data['last_name']}")
	
	try:
		success = attempt_registration(1, 0, order_data)
		return success
	except Exception as e:
		print(f"❌ Ошибка в run_single_registration: {e}")
		return False

def run_flow(card_index: int | None = None) -> None:
	try:
		# Данные теперь передаются извне, проверка не нужна

		if card_index is not None:
			print("🚀 РЕЖИМ ОДНОЙ КАРТЫ - 3 попытки")
			print("=" * 50)
			total_registrations = 0
			successful_registrations = 0

			print(f"\n🔄 КАРТА #{card_index + 1}")
			print("-" * 40)
			card_success = False
			for attempt in range(3):
				print(f"-------Попытка {attempt + 1}/3 для карты #{card_index + 1}-------")
				# set_user_index больше не нужен
				success = attempt_registration(total_registrations, attempt)
				total_registrations += 1
				if success:
					print(f"✅ УСПЕХ! Карта #{card_index + 1}, Попытка {attempt + 1}")
					successful_registrations += 1
					card_success = True
					break
				else:
					print(f"❌ НЕУДАЧА! Карта #{card_index + 1}, Попытка {attempt + 1}")
					if attempt < 2:
						print("⏳ Ждем 5 секунд перед следующей попыткой...")
						time.sleep(10)

			if not card_success:
				print(f"💥 КАРТА #{card_index + 1} ИСЧЕРПАНА - все 3 попытки неудачны")

			print("\n" + "=" * 50)
			print("📊 ИТОГОВАЯ СТАТИСТИКА:")
			print(f"Всего попыток: {total_registrations}")
			print(f"Успешных регистраций: {successful_registrations}")
			print(f"Успешность: {(successful_registrations/total_registrations)*100:.1f}%")
			print("=" * 50)
			log_message(
				f"СЕССИЯ ЗАВЕРШЕНА: {successful_registrations}/{total_registrations} успешных регистраций (single card)"
			)
			return

		print("🚀 ЗАПУСК ПОЛНОЙ ЛОГИКИ - 3 попытки на карту!")
		print("=" * 50)

		total_registrations = 0
		successful_registrations = 0

		# Проходим по всем картам
		for idx in range(3):  # 3 карты по умолчанию
			print(f"\n🔄 КАРТА #{idx + 1}")
			print("-" * 40)

			card_success = False

			# 3 попытки для каждой карты
			for attempt in range(3):
				print(f"-------Попытка {attempt + 1}/3 для карты #{idx + 1}-------")

				# Устанавливаем текущий индекс карты
				# set_user_index больше не нужен

				# Пытаемся зарегистрироваться
				success = attempt_registration(total_registrations, attempt)
				total_registrations += 1

				if success:
					print(f"✅ УСПЕХ! Карта #{idx + 1}, Попытка {attempt + 1}")
					successful_registrations += 1
					card_success = True
					break  # Переходим к следующей карте
				else:
					print(f"❌ НЕУДАЧА! Карта #{idx + 1}, Попытка {attempt + 1}")
					if attempt < 2:  # Если это не последняя попытка
						print("⏳ Ждем 5 секунд перед следующей попыткой...")
						time.sleep(5)

			if not card_success:
				print(f"💥 КАРТА #{idx + 1} ИСЧЕРПАНА - все 3 попытки неудачны")

			# Пауза между картами
			if idx < 2:  # 3 карты, последняя с индексом 2
				print("⏳ Ждем 10 секунд перед следующей картой...")
				time.sleep(10)

		# Итоговая статистика
		print("\n" + "=" * 50)
		print("📊 ИТОГОВАЯ СТАТИСТИКА:")
		print(f"Всего попыток: {total_registrations}")
		print(f"Успешных регистраций: {successful_registrations}")
		print(f"Успешность: {(successful_registrations/total_registrations)*100:.1f}%")
		print("=" * 50)

		log_message(f"СЕССИЯ ЗАВЕРШЕНА: {successful_registrations}/{total_registrations} успешных регистраций")

	except Exception as e:
		print(f"-------Произошла ошибка: {e}-------")
		log_message(f"Критическая ошибка: {e}")


if __name__ == "__main__":
	parser = _argparse.ArgumentParser(description="Whoop bot runner")
	parser.add_argument("--card-index", type=int, default=None, help="Run only this card index (0-based) with 3 attempts")
	cli_args = parser.parse_args()
	run_flow(cli_args.card_index)
