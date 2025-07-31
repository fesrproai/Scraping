# -*- coding: utf-8 -*-
from .base_scraper import BaseScraper
from urllib.parse import urljoin

class LaPolarScraper(BaseScraper):
    def __init__(self):
        super().__init__('lapolar')

    async def scrape(self):
        all_products = []
        for category_url in self.get_categories():
            products = await self.scrape_category(category_url)
            all_products.extend(products)
        return self.remove_duplicates(all_products)

    async def scrape_category(self, category_url):
        self.logger.info(f"Scraping categoría de La Polar: {category_url}")
        try:
            content = await self.helper.make_request(category_url)
            if not content:
                return []

            soup = self.helper.get_soup(content)
            product_elements = soup.select('.product-item, .product-card, .item-card')
            
            products = []
            for element in product_elements:
                product = self._parse_product_element(element)
                if product:
                    products.append(product)
            return products
        except Exception as e:
            self.logger.error(f"Error en scraping de categoría de La Polar: {e}")
            return []

    def _parse_product_element(self, element):
        try:
            name = self.helper.clean_text(element.select_one('.product-name, .item-name').text)
            if not name:
                return None

            prices = self.helper.parse_price(element.select_one('.prices').text)
            original_price = prices.get('original')
            current_price = prices.get('current')

            if not original_price and current_price:
                original_price = current_price

            discount = self.helper.calculate_discount_percentage(original_price, current_price)

            product_url = urljoin(self.get_base_url(), element.find('a')['href'])
            image_url = urljoin(self.get_base_url(), element.find('img')['src'])

            return {
                'name': name,
                'original_price': original_price,
                'current_price': current_price,
                'discount_percentage': discount,
                'product_url': product_url,
                'image_url': image_url,
                'store': self.store_name
            }
        except Exception as e:
            self.logger.warning(f"Error parseando un producto de La Polar: {e}")
            return None