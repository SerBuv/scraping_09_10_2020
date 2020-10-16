'''
Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайтов Superjob и HH.
 Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
    1) Наименование вакансии.
    2) Предлагаемую зарплату (отдельно минимальную и максимальную).
    3) Ссылку на саму вакансию.
    4) Сайт, откуда собрана вакансия.
По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть одинаковая для вакансий с обоих сайтов.
Общий результат можно вывести с помощью dataFrame через pandas.
'''

import requests
import json
from pprint import pprint
from bs4 import BeautifulSoup as bs


# https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&no_magic=true&text=data+engineer&L_save_area=true&area=1&from=cluster_area&showClusters=true

main_url = 'https://hh.ru'

# position = input('Введите желаемую должность: ')
position = 'Data engineer'

params = {
    'clusters': 'true',
    'enable_snippets': 'true',
    'no_magic': 'true',
    'text': position,
    'L_save_area': 'true',
    'area': '1',
    'from': 'cluster_area',
    'showClusters': 'true'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
}


response = requests.get(main_url + '/search/vacancy', params=params, headers=headers)
soup = bs(response.text, 'html.parser')

position_list = soup.findAll('div', {'class': 'vacancy-serp-item'})

vacancies = []
for vacancy in position_list:
    vacancies_data = {}
    vacancy_name = vacancy.find('span').getText()
    vacancy_link = vacancy.find('a', {'class': 'bloko-link HH-LinkModifier'})['href']
    vacancy_salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
    if not vacancy_salary:
        salary_min = None
        salary_max = None
    else:
        vacancy_salary = vacancy_salary.getText()
        if vacancy_salary.find('от') != -1:
            vacancy_salary = vacancy_salary.split()
            for i in vacancy_salary:
                salary_min = vacancy_salary[1] + vacancy_salary[2]
        elif vacancy_salary.find('до') != -1:
            vacancy_salary = vacancy_salary.split()
            for i in vacancy_salary:
                salary_max = vacancy_salary[1] + vacancy_salary[2]
        elif vacancy_salary.find('-') != -1:
            vacancy_salary = vacancy_salary.split('-')
            for i in vacancy_salary:
                salary_min = vacancy_salary[0].replace('\xa0', '')
                salary_max = vacancy_salary[1].replace('\xa0', '')
                salary_max = salary_max[:-5]

    #print(1)
    vacancies_data['name'] = vacancy_name
    vacancies_data['link'] = vacancy_link
    vacancies_data['salary_min'] = salary_min
    vacancies_data['salary_max'] = salary_max

    vacancies.append(vacancies_data)

pprint(vacancies)