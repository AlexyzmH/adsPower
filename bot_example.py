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


# Данные пользователя - разделены по массивам для удобства
# Для каждой карты 3 попытки с разными вариантами имени
NAMES = [
	["Ihar", "Ihaar", "Iihar"],  # Различные варианты написания Ihar
	["Ihar", "Ihhar", "Ihaar"],
	["Iihar", "Ihar", "Ihhar"],
	["Ihaar", "Iihar", "Ihar"],
	["Ihhar", "Ihar", "Ihaar"],
	["Ihar", "Iihar", "Ihhar"],
	["Ihaar", "Ihhar", "Ihar"],
	["Iihar", "Ihaar", "Ihar"],
	["Ihhar", "Iihar", "Ihaar"],
	["Ihar", "Ihaar", "Iihar"],
	["Ihaar", "Ihar", "Ihhar"],
	["Iihar", "Ihhar", "Ihaar"],
	["Ihhar", "Ihar", "Iihar"],
	["Ihar", "Ihhar", "Ihaar"],
	["Ihaar", "Iihar", "Ihhar"],
	["Iihar", "Ihar", "Ihaar"],
	["Ihhar", "Ihaar", "Ihar"],
	["Ihar", "Iihar", "Ihhar"],
	["Ihaar", "Ihhar", "Ihar"],
	["Iihar", "Ihaar", "Ihhar"]
]

LAST_NAMES = [
	["Martsinkevich", "Martsinkevitch", "Martsinkevic"],  # Различные варианты написания Martsinkevich
	["Martsinkevich", "Martsinkevic", "Martsinkevitch"],
	["Martsinkevitch", "Martsinkevich", "Martsinkevic"],
	["Martsinkevic", "Martsinkevitch", "Martsinkevich"],
	["Martsinkevich", "Martsinkevic", "Martsinkevitch"],
	["Martsinkevitch", "Martsinkevic", "Martsinkevich"],
	["Martsinkevic", "Martsinkevich", "Martsinkevitch"],
	["Martsinkevich", "Martsinkevitch", "Martsinkevic"],
	["Martsinkevitch", "Martsinkevich", "Martsinkevic"],
	["Martsinkevic", "Martsinkevitch", "Martsinkevich"],
	["Martsinkevich", "Martsinkevic", "Martsinkevitch"],
	["Martsinkevitch", "Martsinkevic", "Martsinkevich"],
	["Martsinkevic", "Martsinkevich", "Martsinkevitch"],
	["Martsinkevich", "Martsinkevitch", "Martsinkevic"],
	["Martsinkevitch", "Martsinkevich", "Martsinkevic"],
	["Martsinkevic", "Martsinkevitch", "Martsinkevich"],
	["Martsinkevich", "Martsinkevic", "Martsinkevitch"],
	["Martsinkevitch", "Martsinkevic", "Martsinkevich"],
	["Martsinkevic", "Martsinkevich", "Martsinkevitch"],
	["Martsinkevic", "Martsinkevich", "Martsinkevitch"]
]

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
ADDRESS = "Al Mulla Warehouse B2"
ADDRESS_LINE2 = "Al Qusais Industrial Area"

# Фиксированные данные для всех регистраций
CITY = "Dubai"
PROVINCE = "Dubai"
POSTAL_CODE = "00000"  # В Дубае может не требоваться; используем 00000 при необходимости
PHONE = "+48575081614"

# Массив карт (номер, срок действия, CVC)
CARDS = [
	#("5573770013072743", "08/30", "165"),
	#("5573770013032259", "08/30", "065"),
	#("5573770013076520", "08/30", "515"),
	#("5573770013146513", "08/30", "865"),
	#("5573770013098995", "08/30", "172"),
	#("5573770013038330", "08/30", "694"),
	#("5573770013125723", "08/30", "530"),
	#("5573770013175074", "08/30", "160"),
	#("5573770014087963", "08/30", "053"),
	#("5573770013132307", "08/30", "903"),
	#("5573770013198662", "08/30", "979"),
	#("5573770013048776", "08/30", "266"),
	#("5573770013018696", "08/30", "864"),
	#("5573770013059013", "08/30", "647"),
	#("5573770013002831", "08/30", "398"),
	#("5573770013013911", "08/30", "511"),
	#("5573770013035419", "08/30", "010"),
	("5573770013046960", "08/30", "395"),
	("5573770013173517", "08/30", "655"),
	("5573770013075043", "08/30", "652")
]

NAMES = NAMES[:len(CARDS)]
LAST_NAMES = LAST_NAMES[:len(CARDS)]

# Фиксированные данные
password = "TestPassword123!"

# Индекс для выбора данных (можно менять для разных регистраций)
current_index = 0

# Проверяем, что все массивы имеют одинаковую длину
def validate_data_arrays():
	arrays = [NAMES, LAST_NAMES, CARDS]
	array_names = ["NAMES", "LAST_NAMES", "CARDS"]
	
	if len(set(len(arr) for arr in arrays)) > 1:
		print("ОШИБКА: Все массивы должны иметь одинаковую длину!")
		for i, arr in enumerate(arrays):
			print(f"{array_names[i]}: {len(arr)} элементов")
		return False
	else:
		print(f"Все массивы имеют одинаковую длину: {len(CARDS)} элементов")
		return True

# Функция для получения текущих данных пользователя
def get_current_user_data(attempt=0):
	card_number, exp_date, cvc = CARDS[current_index]
	first_name = NAMES[current_index][attempt]
	last_name = LAST_NAMES[current_index][attempt]
	
	return {
		"email": generate_email(first_name, last_name),
		"password": generate_password(),
		"first_name": first_name,
		"last_name": last_name,
		"address": ADDRESS,
		"address_line2": ADDRESS_LINE2,
		"city": CITY,
		"province": PROVINCE,
		"postal_code": POSTAL_CODE,
		"phone": PHONE,
		"card_number": card_number,
		"exp_date": exp_date,
		"cvc": cvc
	}

# Функция для перехода к следующему набору данных
def next_user_data():
	global current_index
	current_index = (current_index + 1) % len(CARDS)
	return get_current_user_data()

# Функция для установки конкретного индекса
def set_user_index(index):
	global current_index
	if 0 <= index < len(CARDS):
		current_index = index
	else:
		print(f"Индекс {index} вне диапазона. Используем индекс 0.")
		current_index = 0

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


def click_safely(driver, wait, locators, name: str = "button"):
	for locator in locators:
		try:
			el = wait.until(EC.presence_of_element_located(locator))
			try:
				driver.execute_script(
					"arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
					el,
				)
			except Exception:
				pass
			time.sleep(0.2)
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

			try:
				el.click()
				return True
			except ElementClickInterceptedException:
				try:
					rect = driver.execute_script(
						"const r = arguments[0].getBoundingClientRect();return {x: r.x + r.width/2, y: r.y + r.height/2};",
						el,
					)
					overlay = driver.execute_script(
						"return document.elementFromPoint(arguments[0].x, arguments[0].y);",
						rect,
					)
					overlay_desc = driver.execute_script(
						"const e=arguments[0]; if(!e) return '<null>'; const cls=(e.className||'').toString().replace(/\\s+/g,'.'); return e.tagName+'#'+(e.id||'')+(cls?'.'+cls:'');",
						overlay,
					)
					log_message(f"[DEBUG] Click intercepted by: {overlay_desc}")
				except Exception:
					pass
				try:
					driver.execute_script("arguments[0].click();", el)
					return True
				except Exception:
					pass
				try:
					ActionChains(driver).move_to_element(el).pause(0.1).click(el).perform()
					return True
				except Exception:
					pass
				save_artifacts(driver, f"whoop_click_intercepted_{name}")
			except StaleElementReferenceException:
				try:
					el = driver.find_element(*locator)
					driver.execute_script("arguments[0].click();", el)
					return True
				except Exception:
					pass
			except Exception as e:
				try:
					driver.execute_script("arguments[0].click();", el)
					return True
				except Exception:
					pass
				try:
					ActionChains(driver).move_to_element(el).pause(0.1).click(el).perform()
					return True
				except Exception:
					pass
				try:
					log_message(f"[DEBUG] Click failed for {name} via {locator}: {e}")
				except Exception:
					pass
				save_artifacts(driver, f"whoop_click_failed_{name}")
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
def attempt_registration(reg_num, attempt=0):
	user_data = get_current_user_data(attempt)
	
	# Подключаемся к уже запущенному браузеру AdsPower
	debug_port = get_adspower_debug_port()
	if not debug_port:
		print("❌ Не удалось получить debug port от AdsPower!")
		return False
	
	options = webdriver.ChromeOptions()
	# Подключаемся к удаленному браузеру AdsPower
	options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
	
	# Для Windows используем автоматическое определение ChromeDriver
	from selenium.webdriver.chrome.service import Service as ChromeService
	from webdriver_manager.chrome import ChromeDriverManager
	
	service = ChromeService(ChromeDriverManager().install())
	driver = webdriver.Chrome(service=service, options=options)
	wait = WebDriverWait(driver, 10)

	try:
		print(f"-------Начинаем регистрацию #{reg_num + 1}-------")
		log_message(f"Используем данные: {user_data['email']} - {user_data['first_name']} {user_data['last_name']}")

		print("-------Открываем сайт Whoop...-------")
		driver.get("https://join.whoop.com/uae/en/")
		time.sleep(1)

		print("-------Нажимаем кнопку 'Start with PEAK'...-------")
		start_peak_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='membership-PEAK-card-cta']")))
		start_peak_button.click()
		time.sleep(2)

		print("-------Нажимаем 'Continue'...-------")
		continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]")))
		continue_button.click()
		time.sleep(2)

		print("-------Выбираем Trial-membership...-------")
		trial_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='trial-membership']")))
		trial_button.click()
		time.sleep(2)

		print("-------Нажимаем Check Out...-------")
		checkout_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='cart-continueButton']")))
		checkout_button.click()
		time.sleep(2)

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
		next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='next-button-create-account']")))
		next_button.click()
		time.sleep(2)

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

		print("-------Вводим провинцию...-------")
		try:
			# Иногда это select
			province = wait.until(EC.presence_of_element_located((By.ID, "province")))
			province.send_keys(user_data["province"])
		except Exception:
			try:
				province_alt = wait.until(EC.presence_of_element_located((By.ID, "Area/District")))
				province_alt.send_keys(user_data["province"])
			except Exception:
				pass
		time.sleep(1)

		print("-------Вводим телефон...-------")
		phone = wait.until(EC.presence_of_element_located((By.ID, "phone")))
		phone.send_keys(user_data["phone"])
		time.sleep(1)

		print("-------Нажимаем 'Next' после ввода адреса...-------")
		try:
			next_address_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='next-button-shipping-address']")))
			next_address_button.click()
			time.sleep(2)
		except Exception:
			pass

		# Проверяем, что перешли к следующему шагу; иначе — робастный клик и диагностика
		try:
			WebDriverWait(driver, 5).until(
				EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='next-button-shipping-method']"))
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
			time.sleep(2)

		print("-------Выбираем метод доставки и нажимаем 'Weiter'...-------")
		weiter_button_shipping = wait.until(
			EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='next-button-shipping-method']")))
		weiter_button_shipping.click()
		time.sleep(1)

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

			wait.until(EC.presence_of_element_located((By.NAME, "exp-date"))).send_keys(user_data["exp_date"])
			print("Ввел срок действия")

			wait.until(EC.presence_of_element_located((By.NAME, "cvc"))).send_keys(user_data["cvc"])
			print("Ввел CVC")

			driver.switch_to.default_content()
		except Exception as e:
			log_message(f"Ошибка при вводе данных карты: {e}")
			driver.switch_to.default_content()

		print("-------Нажимаем 'Place Order'...-------")
		try:
			place_order_button = wait.until(
				EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='complete-purchase']")))
			place_order_button.click()
			log_message("Кнопка Place Order нажата")
			time.sleep(3)  # Ждём обработку платежа
		except Exception as e:
			log_message(f"Ошибка нажатия Place Order: {e}")
			# Пробуем альтернативные селекторы
			try:
				place_order_button = wait.until(
					EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Place Order')]")))
				place_order_button.click()
				log_message("Place Order нажат альтернативным способом")
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

			print("-------Переходим на страницу заказа...25 сек-------")
			driver.get(order_status_link)
			time.sleep(8)

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
					time.sleep(3)  # Ждем 3 секунды

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


def run_flow(card_index: int | None = None) -> None:
	try:
		# Проверяем данные перед началом
		if not validate_data_arrays():
			raise Exception("Неверная конфигурация данных")

		if card_index is not None:
			print("🚀 РЕЖИМ ОДНОЙ КАРТЫ - 3 попытки")
			print("=" * 50)
			total_registrations = 0
			successful_registrations = 0

			print(f"\n🔄 КАРТА #{card_index + 1} - {CARDS[card_index][0]}")
			print("-" * 40)
			card_success = False
			for attempt in range(3):
				print(f"-------Попытка {attempt + 1}/3 для карты #{card_index + 1}-------")
				set_user_index(card_index)
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
						time.sleep(5)

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
		for idx in range(len(CARDS)):
			print(f"\n🔄 КАРТА #{idx + 1} - {CARDS[idx][0]}")
			print("-" * 40)

			card_success = False

			# 3 попытки для каждой карты
			for attempt in range(3):
				print(f"-------Попытка {attempt + 1}/3 для карты #{idx + 1}-------")

				# Устанавливаем текущий индекс карты
				set_user_index(idx)

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
			if idx < len(CARDS) - 1:
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
