import requests
import os
import sys
import re
import settings
import json
from bs4 import BeautifulSoup
from typing import Any, Dict, Tuple
from collections import OrderedDict
from datetime import date

""" IDs of html elements """
ID_PRODUCT_NAME = 'productTitle'
ID_PRODUCT_PRICE = 'priceblock_ourprice'
ID_PRODUCT_SELLER = 'bylineInfo'


INVALID_PRICE = -1




class Product(OrderedDict):
    def __init__(self, **kwargs):
        super().__init__(kwargs)

class AmazonScraper:

    def __init__(self):
        
        # load application settings
        self.settings = settings.Settings()

        self.user_agent = 'MyApp/{} (Language=Python {}; Platform={})'.format(self.settings.version, sys.version.split()[0], os.uname().sysname)
        self.headers = {'User-Agent': self.user_agent}

        self.products = self.load_products()
        self.currency_rates = None
        

    def load_products(self):
        try:
            with open(os.path.join(self.settings.db_path, self.settings.db_name), 'r') as f:
                return OrderedDict(json.load(f))
        except:
            return OrderedDict()

    def store_products(self):
        with open(os.path.join(self.settings.db_path, self.settings.db_name), 'w') as f:
            json.dump(self.products, f)


    def get_seller(self, soup) -> float:
        try:
            return soup.find(id=ID_PRODUCT_SELLER).get_text().strip()
        except AttributeError:
            return ''

    def get_name(self, soup) -> float:
        try:
            return soup.find(id=ID_PRODUCT_NAME).get_text().strip()
        
        except AttributeError:
            return ''
        pass

    def get_price(self, soup) -> int:
        """
        Returns the price of the product.
        """
        try:
            price, currency = soup.find(id=ID_PRODUCT_PRICE).get_text().strip().split()
            price = int(float(price.translate(str.maketrans(',.','.,'))) * 100)
            if currency != self.settings.currency:
                price = self.convert_currency(price, currency, self.settings.currency)

            #TODO: english number formatting
            return int(float(price.translate(str.maketrans(',.','.,'))) * 100)

        except Exception as e:
            print(e)
            #TODO(daniel) log
            return INVALID_PRICE
        pass

    @staticmethod
    def convert_currency(price: float, from_currency: str, to_currency: str) -> float:
        #TODO(daniel) convert price to respective currency
        # symbol_map = {


        # }
        # if not isinstance(self.currency_rates, CurrencyRates):
        #     self.currency_rates = CurrencyRates()

        # try:

        # except KeyError:

        # return c.get_rate(from_currency, to_currency) * price
        return price


    def get_product(self, url: str) -> Dict[str, Any]:
        """ Adds a product or updates its information """
        page = requests.get(url, headers=self.headers)
        if page:
            soup = BeautifulSoup(page.content, 'html.parser')

            asin = self.get_asin(url)

            if asin in self.products:
                self.update_product(asin, soup)
            else:
                self.add_product(asin, soup)

        else:
            print("Could not get product information.")
            #TODO(daniel)  add logging
            return

    def add_product(self, asin: str, soup):
        """ Fetches product properties from url and adds it to the tracked products """
        price = self.get_price(soup)
        self.products[asin] = Product(
            asin   = asin,
            name   = self.get_name(soup),
            price  = price,
            seller = self.get_seller(soup),
            hist   = OrderedDict({self.get_date():price})
        )
        print(self.products[asin])

    def update_product(self, asin: str, soup):
        """ Fetches current price and updates price history of an already tracked product """
        price = self.get_price(soup)
        self.products[asin]['price'] = price
        self.products[asin]['hist'][self.get_date()] = price
        pass

    def get_date(self) -> str:
        """ Returns current date in the specified string format """
        print(date.today().strftime(self.settings.date_format))
        return date.today().strftime(self.settings.date_format)

    @staticmethod
    def get_product_url(asin: str) -> str:
        """ Assembles the url of a product page based on the ASIN (Amazon Standard Identification Number) """
        return '{base}.{tld}/dp/{asin}'.format(base=self.settings.base_url, tld=self.settings.tld, asin=asin)

    @staticmethod
    def get_asin(url: str) -> str:
        """ Get the product ASIN of length 10 from the url. """
        return re.search(r'(?<=\/dp\/)\w{10}', url).group(0)
