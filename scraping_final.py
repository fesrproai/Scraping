#!/usr/bin/env python3
"""
Sistema de Scraping de Descuentos - Versión Final
Funciona directamente sin Firebase, guarda datos localmente
"""

import os
import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class ScrapingSystem:
    def __init__(self):
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Configuración de tiendas con URLs que funcionan
        self.stores = {
            'paris': {
                'name': 'Paris',
                'base_url': 'https://www.paris.cl',
                'categories': [
                    '',  # Página principal
                    '/linea-blanca/lavado-secado/?tipoProductoAll=Lavadoras-Secadoras%2CLavadoras%2CSecadoras'
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
    
    def get_page_content(self, url):
        """Obtiene el contenido de una página web"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return BeautifulSoup(response.content, 'html.parser')
            
        except Exception as e:
            print(f"❌ Error obteniendo página {url}: {e}")
            return None
    
    def extract_product_info(self, element, store_name):
        """Extrae información de un producto"""
        try:
            # Buscar nombre del producto
            name_selectors = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                '.title', '.name', '.product-name', '.product-title',
                '[data-product-name]', '.product-name', '.product-title',
                '.item-title', '.card-title'
            ]
            
            name = ""
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    if name and len(name) > 3:
                        break
            
            # Buscar precio actual
            price_selectors = [
                '.price', '.cost', '.value', '.current-price', '.price-current',
                '.price-now', '.price-new', '.price-sale', '.price-value',
                '.product-price', '.item-price'
            ]
            
            current_price = ""
            for selector in price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if '$' in price_text and any(char.isdigit() for char in price_text):
                        current_price = price_text
                        break
            
            # Buscar precio original
            original_price_selectors = [
                '.price-old', '.original-price', '.price-original',
                '.list-price', '.price-before', '.price-old-value'
            ]
            
            original_price = ""
            for selector in original_price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if '$' in price_text and any(char.isdigit() for char in price_text):
                        original_price = price_text
                        break
            
            # Buscar descuento
            discount_selectors = [
                '.discount', '.discount-badge', '.discount-percentage',
                '.discount-label', '.sale-badge', '.discount-tag'
            ]
            
            discount = ""
            for selector in discount_selectors:
                discount_elem = element.select_one(selector)
                if discount_elem:
                    discount = discount_elem.get_text(strip=True)
                    break
            
            # Buscar enlace del producto
            link_elem = element.find('a', href=True)
            product_link = ""
            if link_elem:
                product_link = link_elem.get('href')
                if not product_link.startswith('http'):
                    product_link = self.stores[store_name]['base_url'] + product_link
            
            # Buscar imagen del producto
            img_elem = element.find('img')
            product_image = ""
            if img_elem:
                product_image = img_elem.get('src', '')
                if not product_image.startswith('http'):
                    product_image = self.stores[store_name]['base_url'] + product_image
            
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
        """Scraping de una tienda específica"""
        print(f"\n🏪 Scraping {self.stores[store_name]['name']}...")
        
        store_config = self.stores[store_name]
        all_products = []
        
        for category in store_config['categories']:
            try:
                url = store_config['base_url'] + category
                category_name = category if category else "Página Principal"
                print(f"  📂 Categoría: {category_name}")
                
                soup = self.get_page_content(url)
                if not soup:
                    continue
                
                # Buscar productos con diferentes selectores
                product_selectors = [
                    '.product-item', '.product-card', '.item', '.product',
                    '[data-product]', '.card', '.producto', '.product-grid-item',
                    '.product-tile', '.product-container', '.product-box',
                    '.product-grid', '.product-list-item', '.product-item-grid'
                ]
                
                products_found = []
                
                for selector in product_selectors:
                    elements = soup.select(selector)
                    if elements:
                        print(f"    ✅ Encontrados {len(elements)} productos con selector: {selector}")
                        
                        for element in elements:
                            product = self.extract_product_info(element, store_name)
                            if product and product['name'] and product['current_price']:
                                products_found.append(product)
                        
                        break
                
                if products_found:
                    all_products.extend(products_found)
                    print(f"    📦 {len(products_found)} productos válidos extraídos")
                else:
                    print(f"    ⚠️  No se encontraron productos en esta categoría")
                
                # Delay entre categorías
                time.sleep(2)
                
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
            filename = f"{self.data_dir}/{store_name}_products_{timestamp}.json"
            
            data = {
                'store': store_name,
                'timestamp': datetime.now().isoformat(),
                'total_products': len(products),
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
        """Ejecuta el scraping completo"""
        print("🚀 Sistema de Scraping de Descuentos - Versión Final")
        print("=" * 60)
        print("💾 Los datos se guardarán localmente en la carpeta 'data'")
        print("=" * 60)
        
        if stores_to_scrape is None:
            stores_to_scrape = list(self.stores.keys())
        
        total_products = 0
        saved_files = []
        
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

def main():
    scraper = ScrapingSystem()
    scraper.run_scraping()

if __name__ == "__main__":
    main() 