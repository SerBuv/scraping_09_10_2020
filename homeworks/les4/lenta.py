'''1) Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации.
2) Сложить собранные данные в БД
'''

from pprint import pprint
from lxml import html
import requests
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['db_news']


header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
url = 'https://lenta.ru/'
response = requests.get(url, headers=header)
dom = html.fromstring(response.text)

news = dom.xpath("//time[@class='g-time']/../..")

boxes = []
for box in news:

    data_box = {}

    names = box.xpath(".//time[@class='g-time']/../text()")
    links = box.xpath(".//time[@class='g-time']/../@href")
    date = box.xpath(".//time[@class='g-time']/@datetime")
    for i in range(len(names)):
        names[i] = names[i].replace(u'\xa0', u' ')

    data_box['sourse'] = 'lenta.ru'
    data_box['name'] = names[0]
    data_box['link'] = 'https://lenta.ru/' + links[0]
    data_box['date'] = date[0]

    boxes.append(data_box)

pprint(boxes)

db.data_lenta.insert_many(boxes)



