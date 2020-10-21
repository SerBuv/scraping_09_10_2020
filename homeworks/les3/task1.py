'''1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные вакансии в созданную БД.
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы. Запрос должен анализировать одновременно минимальную и максимальную зарплату.
3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.'''

from pymongo import MongoClient
import requests
import json
from pprint import pprint
from bs4 import BeautifulSoup as bs

client = MongoClient('localhost', 27017)

db = client['db_hh']
#vacancies = db.vacancies


# https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&no_magic=true&text=data+engineer&L_save_area=true&area=1&from=cluster_area&showClusters=true

main_url = 'https://hh.ru'

# position = input('Введите желаемую должность: ')
position = 'Big Data'

params = {
    'clusters': 'true',
    'enable_snippets': 'true',
    'no_magic': 'true',
    'text': position,
    'L_save_area': 'true',
    'area': '1',
    'from': 'cluster_area',
    'showClusters': 'true',
    'page': '0'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
}

vacancies = []
while True:
    response = requests.get(main_url + '/search/vacancy', params=params, headers=headers)
    soup = bs(response.text, 'html.parser')

    position_list = soup.findAll('div', {'class': 'vacancy-serp-item'})

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

    next_link = soup.find('a', {'data-qa': ['pager-next']})
    if next_link:
        params['page'] = str(int(params['page']) + 1)
    else:
        break

# --- 1 ---
def vac():
    db.vacancies.insert_many(vacancies)

# --- 2 ---
def res():
    for i in vacancies:
        if db.vacancies.find(i).count() < 1:
            db.vacancies.insert_one(i)

# --- 3 ---
def salary(count):
    for i in db.vacancies.find({'$or': [{'salary_max': {'$gt': count}}, {'salary_min': {'$gt': count}}]}):
        pprint(i)
