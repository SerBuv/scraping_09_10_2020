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
url = 'https://yandex.ru/news/?from=tabbar'
response = requests.get(url, headers=header)
dom = html.fromstring(response.text)

news = dom.xpath("//a[contains(@href,'rubric=index') and @class='news-card__link']/ancestor::article")

boxes = []
for box in news:

    data_box = {}

    names = box.xpath("//div[@class='mg-grid__row mg-grid__row_gap_8 news-top-stories news-app__top']//div[@class='news-card__annotation']/text()")
    links = box.xpath("//div[@class='mg-grid__row mg-grid__row_gap_8 news-top-stories news-app__top']//a[@target='_self']/@href")
    date = box.xpath("//div[@class='mg-grid__row mg-grid__row_gap_8 news-top-stories news-app__top']//span[@class='mg-card-source__time']/text()")
    sourse = box.xpath("//div[@class='mg-grid__row mg-grid__row_gap_8 news-top-stories news-app__top']//span[@class='mg-card-source__source']/a/text()")

    data_box['sourse'] = sourse[0]
    data_box['name'] = names[0]
    data_box['link'] = links[0]
    data_box['date'] = date[0]

    boxes.append(data_box)

pprint(boxes)

db.data_yandex.insert_many(boxes)