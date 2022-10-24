import json
import re

import scrapy

from .consent_utils import get_request
from ..items import Price


class TickerPriceSpider(scrapy.Spider):
    name = "price_sp"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state = {'prices': {}}

    def start_requests(self):
        tickers = ['META', 'AMZN', 'AAPL', 'NFLX', 'GOOGL']

        if 'prices' not in self.state.keys():
            self.state['prices'] = dict()

        for ticker in tickers:
            if ticker not in self.state['prices'].keys():
                self.state['prices'][ticker] = set()

            yield get_request(f'https://finance.yahoo.com/quote/{ticker}/news?p={ticker}', self.parse)

    def parse(self, response, **kwargs):
        ticker_news_script = response.xpath('//script[contains(text(),"root.App.main")]').get()
        print(response.text)
        ticker_news_json = re.search('{.*};', ticker_news_script).group(0)[:-1]
        ticker_news_parser = json.loads(ticker_news_json)
        stores = ticker_news_parser['context']['dispatcher']['stores']

        price = stores['QuoteSummaryStore']['price']['regularMarketPrice']['raw']
        symbol = stores['QuoteSummaryStore']['symbol']
        date = stores['QuoteSummaryStore']['price']['regularMarketTime']

        if date not in self.state['prices'][symbol]:
            self.state['prices'][symbol].add(date)
            yield Price(ticker=symbol, price=price, date=date)
