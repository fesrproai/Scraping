#!/usr/bin/env python3
"""
Sistema de Scraping de Descuentos - Versión Mejorada
Usa Selenium para manejar JavaScript dinámico
"""

import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class ScrapingMejorado:
    def __init__(self):
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Configuración de tiendas
        self.stores = {
            'paris': {
                'name': 'Paris',
                'base_url': 'https://www.paris.cl',
                'categories': [
                    '',  # Página principal
                    '/linea-blanca/lavado-secado'
                ]
            },
            'falabella': {
                'name': 'Falabella',
                'base_url': 'https://www.falabella.com',
                'categories': [
                    '',  # Página principal
                    '/falabella-cl'
                ]
            }
        }
        
        # Configurar Chrome
        self.setup_driver()
    
    def setup_driver(self):
        """Configura el driver de Chrome"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ Driver de Chrome configurado correctamente")
            
        except Exception as e:
            print(f"❌ Error configurando Chrome: {e}")
            print("💡 Instala ChromeDriver desde: https://chromedriver.chromium.org/")
            self.driver = None
    
    def get_page_content(self, url):
        """Obtiene el contenido de una página web con Selenium"""
        if not self.driver:
            return None
        
        try:
            print(f"📡 Cargando: {url}")
            self.driver.get(url)
            
            # Esperar a que la página cargue completamente
            time.sleep(5)
            
            # Scroll para cargar contenido dinámico
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            return self.driver.page_source
            
        except Exception as e:
            print(f"❌ Error cargando página {url}: {e}")
            return None
    
    def extract_product_info(self, element, store_name):
        """Extrae información de un producto usando Selenium"""
        try:
            # Buscar nombre del producto
            name_selectors = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                '.title', '.name', '.product-name', '.product-title',
                '[data-product-name]', '.product-name', '.product-title',
                '.item-title', '.card-title', '.product-name'
            ]
            
            name = ""
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    name = name_elem.text.strip()
                    if name and len(name) > 3:
                        break
                except NoSuchElementException:
                    continue
            
            # Buscar precio actual
            price_selectors = [
                '.price', '.cost', '.value', '.current-price', '.price-current',
                '.price-now', '.price-new', '.price-sale', '.price-value',
                '.product-price', '.item-price', '.price'
            ]
            
            current_price = ""
            for selector in price_selectors:
                try:
                    price_elem = element.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_elem.text.strip()
                    if '$' in price_text and any(char.isdigit() for char in price_text):
                        current_price = price_text
                        break
                except NoSuchElementException:
                    continue
            
            # Buscar precio original
            original_price_selectors = [
                '.price-old', '.original-price', '.price-original',
                '.list-price', '.price-before', '.price-old-value'
            ]
            
            original_price = ""
            for selector in original_price_selectors:
                try:
                    price_elem = element.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_elem.text.strip()
                    if '$' in price_text and any(char.isdigit() for char in price_text):
                        original_price = price_text
                        break
                except NoSuchElementException:
                    continue
            
            # Buscar descuento
            discount_selectors = [
                '.discount', '.discount-badge', '.discount-percentage',
                '.discount-label', '.sale-badge', '.discount-tag'
            ]
            
            discount = ""
            for selector in discount_selectors:
                try:
                    discount_elem = element.find_element(By.CSS_SELECTOR, selector)
                    discount = discount_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Buscar enlace del producto
            product_link = ""
            try:
                link_elem = element.find_element(By.TAG_NAME, "a")
                product_link = link_elem.get_attribute("href")
                if not product_link.startswith('http'):
                    product_link = self.stores[store_name]['base_url'] + product_link
            except NoSuchElementException:
                pass
            
            # Buscar imagen del producto
            product_image = ""
            try:
                img_elem = element.find_element(By.TAG_NAME, "img")
                product_image = img_elem.get_attribute("src")
                if not product_image.startswith('http'):
                    product_image = self.stores[store_name]['base_url'] + product_image
            except NoSuchElementException:
                pass
            
            # Crear objeto producto
            product = {
                'name': name,
                'current_price': current_price,
                'original_price': original_price,
                'discount': discount,
                'product_link': product_link,
                'product_image': product_image,
                'store': store_name,
                'scraped_at': datetime.now().isoformat()
            }
            
            return product
            
        except Exception as e:
            print(f"❌ Error extrayendo información del producto: {e}")
            return None
    
    def scrape_store(self, store_name):
        """Scraping de una tienda específica con Selenium"""
        print(f"\n🏪 Scraping {self.stores[store_name]['name']} con Selenium...")
        
        store_config = self.stores[store_name]
        all_products = []
        
        for category in store_config['categories']:
            try:
                url = store_config['base_url'] + category
                category_name = category if category else "Página Principal"
                print(f"  📂 Categoría: {category_name}")
                
                page_source = self.get_page_content(url)
                if not page_source:
                    continue
                
                # Buscar productos con diferentes selectores
                product_selectors = [
                    '.product-item', '.product-card', '.item', '.product',
                    '[data-product]', '.card', '.producto', '.product-grid-item',
                    '.product-tile', '.product-container', '.product-box',
                    '.product-grid', '.product-list-item', '.product-item-grid',
                    '.product', '.producto', '.item'
                ]
                
                products_found = []
                
                for selector in product_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"    ✅ Encontrados {len(elements)} productos con selector: {selector}")
                            
                            for element in elements:
                                product = self.extract_product_info(element, store_name)
                                if product and product['name'] and product['current_price']:
                                    products_found.append(product)
                            
                            break
                    except Exception as e:
                        continue
                
                if products_found:
                    all_products.extend(products_found)
                    print(f"    📦 {len(products_found)} productos válidos extraídos")
                else:
                    print(f"    ⚠️  No se encontraron productos en esta categoría")
                
                # Delay entre categorías
                time.sleep(3)
                
            except Exception as e:
                print(f"    ❌ Error en categoría {category}: {e}")
                continue
        
        return all_products
    
    def save_products(self, products, store_name):
        """Guarda productos en archivo JSON"""
        if not products:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.data_dir}/{store_name}_products_selenium_{timestamp}.json"
            
            data = {
                'store': store_name,
                'timestamp': datetime.now().isoformat(),
                'total_products': len(products),
                'method': 'selenium',
                'products': products
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {len(products)} productos guardados en {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error guardando productos: {e}")
            return None
    
    def run_scraping(self, stores_to_scrape=None):
        """Ejecuta el scraping completo con Selenium"""
        print("🚀 Sistema de Scraping de Descuentos - Versión Mejorada")
        print("=" * 60)
        print("💾 Usando Selenium para JavaScript dinámico")
        print("📁 Los datos se guardarán localmente en la carpeta 'data'")
        print("=" * 60)
        
        if stores_to_scrape is None:
            stores_to_scrape = list(self.stores.keys())
        
        total_products = 0
        saved_files = []
        
        try:
            for store_name in stores_to_scrape:
                if store_name not in self.stores:
                    print(f"❌ Tienda '{store_name}' no configurada")
                    continue
                
                products = self.scrape_store(store_name)
                
                if products:
                    filename = self.save_products(products, store_name)
                    if filename:
                        saved_files.append(filename)
                    total_products += len(products)
            
            # Resumen final
            print("\n" + "=" * 60)
            print("📊 RESUMEN FINAL")
            print("=" * 60)
            print(f"✅ Total productos encontrados: {total_products}")
            print(f"📁 Archivos guardados: {len(saved_files)}")
            
            if saved_files:
                print("\n📂 Archivos creados:")
                for file in saved_files:
                    print(f"   • {file}")
            
            print("\n🎉 Scraping completado exitosamente!")
            print("💡 Revisa la carpeta 'data' para ver los resultados")
            
        finally:
            # Cerrar el driver
            if self.driver:
                self.driver.quit()
                print("🔒 Driver de Chrome cerrado")

def main():
    scraper = ScrapingMejorado()
    scraper.run_scraping()

if __name__ == "__main__":
    main() 