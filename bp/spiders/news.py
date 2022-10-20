import json
import re

import scrapy

from .consent_utils import get_request
from ..items import News


class NewsSpider(scrapy.Spider):
    name = "news_sp"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state = {'news': set()}

    def start_requests(self):
        if 'news' not in self.state.keys():
            self.state['news'] = set()

        yield get_request('https://finance.yahoo.com/news/', self.parse)

    def parse(self, response, **kwargs):
        main_list = 0
        side_list = 1

        news_script = response.xpath('//script[contains(text(),"root.App.main")]').get()
        news_json = re.search('{.*};', news_script).group(0)[:-1]
        news_parser = json.loads(news_json)
        streams = news_parser['context']['dispatcher']['stores']['StreamStore']['streams']
        news = list(streams.values())[main_list]['data']['stream_items']
        articles = [x for x in news if x.get('type') == 'article']

        for x in articles:
            news = News(url=x.get('url'),
                        ticker='ALL',
                        title=x.get('title'),
                        summary=x.get('summary'),
                        date=x.get('pubtime'),
                        category=x.get('categoryLabel'))

            if news.title not in self.state['news']:
                self.state['news'].add(news.title)
                yield news
