# -*- coding: utf-8 -*-
from .base_scraper import BaseScraper
from urllib.parse import urljoin
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class FalabellaScraper(BaseScraper):
    def __init__(self):
        super().__init__('falabella')
        self.driver = None

    def _setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'--user-agent={self.helper.get_random_user_agent()}')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
        except Exception as e:
            self.logger.error(f"Error configurando Selenium para Falabella: {e}")
            self.driver = None

    async def scrape(self):
        self._setup_driver()
        if not self.driver:
            return []

        all_products = []
        try:
            for category_url in self.get_categories():
                products = await self.scrape_category(category_url)
                all_products.extend(products)
        finally:
            if self.driver:
                self.driver.quit()
        
        return all_products

    async def scrape_category(self, category_url):
        self.logger.info(f"Scraping categoría de Falabella: {category_url}")
        try:
            self.driver.get(category_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-pod-type="product"]'))
            )
            self._scroll_to_load_more()
            products = self._extract_products_from_page()
            return self.remove_duplicates(products)
        except Exception as e:
            self.logger.error(f"Error en scraping de categoría de Falabella: {e}")
            return []

    def _scroll_to_load_more(self):
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            self.logger.warning(f"Error durante el scroll en Falabella: {e}")

    def _extract_products_from_page(self):
        products = []
        product_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-pod-type="product"]')
        for element in product_elements:
            product = self._parse_product_element(element)
            if product:
                products.append(product)
        return products

    def _parse_product_element(self, element):
        try:
            name = element.find_element(By.CSS_SELECTOR, '.pod-title, .product-name, h3').text.strip()
            if not name:
                return None

            original_price = self._extract_price(element, '.price-old, .list-price')
            current_price = self._extract_price(element, '.price-current, .price')
            if not original_price and current_price:
                original_price = current_price

            discount = self._extract_discount(element)
            if discount == 0 and original_price and current_price:
                discount = self.helper.calculate_discount_percentage(original_price, current_price)

            product_url = self._extract_link(element)
            image_url = self._extract_image(element)

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
            self.logger.warning(f"Error parseando un producto de Falabella: {e}")
            return None

    def _extract_price(self, element, selector):
        try:
            price_text = element.find_element(By.CSS_SELECTOR, selector).text.strip()
            return self.helper.parse_price(price_text)
        except NoSuchElementException:
            return None

    def _extract_discount(self, element):
        for selector in ['.discount-badge', '.discount-percentage', '.sale-badge']:
            try:
                discount_text = element.find_element(By.CSS_SELECTOR, selector).text.strip()
                discount = self.helper.parse_discount_percentage(discount_text)
                if discount > 0:
                    return discount
            except NoSuchElementException:
                continue
        return 0

    def _extract_link(self, element):
        try:
            href = element.find_element(By.TAG_NAME, 'a').get_attribute('href')
            return urljoin(self.get_base_url(), href)
        except NoSuchElementException:
            return None

    def _extract_image(self, element):
        try:
            src = element.find_element(By.TAG_NAME, 'img').get_attribute('src')
            return urljoin(self.get_base_url(), src)
        except NoSuchElementException:
            return None