# -*- coding: utf-8 -*-
import logging
from utils.helpers import ScrapingHelper
from config.settings import STORES_CONFIG

class BaseScraper:
    def __init__(self, store_name):
        self.store_name = store_name
        self.store_config = STORES_CONFIG.get(store_name, {})
        self.logger = logging.getLogger(self.__class__.__name__)
        self.helper = ScrapingHelper()

    def get_base_url(self):
        return self.store_config.get('base_url')

    def get_categories(self):
        return self.store_config.get('categories', [])

    def remove_duplicates(self, products):
        seen = set()
        unique_products = []
        for product in products:
            identifier = (product.get('name'), product.get('product_url'))
            if identifier not in seen:
                unique_products.append(product)
                seen.add(identifier)
        return unique_products

    async def scrape(self):
        raise NotImplementedError("El método 'scrape' debe ser implementado por las subclases.")