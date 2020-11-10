from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagram import settings
from instagram.spiders.insta_parser import InstaParserSpider
from pymongo import MongoClient

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstaParserSpider)
    process.start()
    print('_____________________________________')

    client = MongoClient('localhost', 27017)
    mongo_base = client.instagram
    collection = mongo_base['user_rel']

    report1 = collection.find({'parsed_username': 'a.i_programmer', 'relation': 'subscriber'})
    for row in report1:
        print(row)

    report2 = collection.find({'parsed_username': 'influence_coding', 'relation': 'subscribe'})
    for row in report2:
        print(row)