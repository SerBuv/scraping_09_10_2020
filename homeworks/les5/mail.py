'''1) Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные о письмах в базу данных
(от кого, дата отправки, тема письма, текст письма полный)
Логин тестового ящика: study.ai_172@mail.ru
Пароль тестового ящика: NextPassword172
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

login = "study.ai_172"
password = "NextPassword172"
url = "https://account.mail.ru/login/"

chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)

driver.get(url)

# Логин
login_field = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.NAME,'username'))
)
login_field.send_keys(login)
login_field.submit()

# Пароль
password_field = WebDriverWait(driver, 15).until(
    EC.visibility_of_element_located((By.NAME,'password'))
)
password_field.send_keys(password)
password_field.submit()

# Количество писем
inbox_element = WebDriverWait(driver, 15).until(
    EC.visibility_of_element_located((By.CLASS_NAME,'nav__item_active'))
)
title = inbox_element.get_attribute('title')
title = title.split()
count_emails = int(title[1])

# Список ссылок
urls_marker = WebDriverWait(driver, 15).until(
    EC.visibility_of_element_located((By.CLASS_NAME,'js-letter-list-item'))
)
url_list = driver.find_elements_by_class_name('js-letter-list-item')
url_href = []
for i in url_list:
     url_href.append(i.get_attribute('href'))

# Добавляем ссылки
while len(url_href) != count_emails:
    actions = ActionChains(driver)
    actions.move_to_element(url_list[-1])
    actions.perform()
    time.sleep(1)
    url_list = driver.find_elements_by_class_name('js-letter-list-item')
    for i in url_list:
        url_href.append(i.get_attribute('href'))

emails = []
for i in url_href:
    driver.get(i)
    letter_author_wrapper = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'letter__author'))
    )
    email = {
        'author': letter_author_wrapper.find_element_by_class_name('letter-contact').get_attribute('title'),
        'date': letter_author_wrapper.find_element_by_class_name('letter__date').text,
        'title': driver.find_element_by_class_name('thread__subject').text,
        'body': driver.find_element_by_class_name('letter-body').text
    }
    emails.append(email)

client = MongoClient('localhost', 27017)
db = client['db_emails']
db.box.insert_many(emails)


