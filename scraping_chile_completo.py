#!/usr/bin/env python3
"""
Sistema de Scraping de Descuentos Chile - Versión Completa
12 tiendas chilenas populares con scraping optimizado
"""

import os
import json
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

class ScrapingChileCompleto:
    def __init__(self):
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Headers más realistas para evitar detección
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-CL,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Configuración de 12 tiendas chilenas populares
        self.stores = {
            'falabella': {
                'name': 'Falabella',
                'base_url': 'https://www.falabella.com',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.falabella.com/falabella-cl/collection/ofertas'},
                    {'name': 'Tecnología', 'url': 'https://www.falabella.com/falabella-cl/category/cat20002/Tecnologia'},
                    {'name': 'Hogar', 'url': 'https://www.falabella.com/falabella-cl/category/cat20001/Hogar-y-Muebles'}
                ]
            },
            'paris': {
                'name': 'Paris',
                'base_url': 'https://www.paris.cl',
                'categories': [
                    {'name': 'Página Principal', 'url': 'https://www.paris.cl'},
                    {'name': 'Ofertas', 'url': 'https://www.paris.cl/ofertas'}
                ]
            },
            'ripley': {
                'name': 'Ripley',
                'base_url': 'https://www.ripley.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.ripley.cl/ofertas'},
                    {'name': 'Tecnología', 'url': 'https://www.ripley.cl/tecnologia'},
                    {'name': 'Hogar', 'url': 'https://www.ripley.cl/hogar'}
                ]
            },
            'sodimac': {
                'name': 'Sodimac',
                'base_url': 'https://www.sodimac.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.sodimac.cl/sodimac-cl/ofertas'},
                    {'name': 'Herramientas', 'url': 'https://www.sodimac.cl/sodimac-cl/category/cat20002/Herramientas'},
                    {'name': 'Jardín', 'url': 'https://www.sodimac.cl/sodimac-cl/category/cat20001/Jardin-y-Aire-Libre'}
                ]
            },
            'easy': {
                'name': 'Easy',
                'base_url': 'https://www.easy.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.easy.cl/easy-cl/ofertas'},
                    {'name': 'Herramientas', 'url': 'https://www.easy.cl/easy-cl/category/cat20002/Herramientas'},
                    {'name': 'Hogar', 'url': 'https://www.easy.cl/easy-cl/category/cat20001/Hogar-y-Decoracion'}
                ]
            },
            'lider': {
                'name': 'Líder',
                'base_url': 'https://www.lider.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.lider.cl/supermercado/category/Ofertas'},
                    {'name': 'Tecnología', 'url': 'https://www.lider.cl/supermercado/category/Tecnologia'},
                    {'name': 'Hogar', 'url': 'https://www.lider.cl/supermercado/category/Hogar'}
                ]
            },
            'jumbo': {
                'name': 'Jumbo',
                'base_url': 'https://www.jumbo.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.jumbo.cl/ofertas'},
                    {'name': 'Tecnología', 'url': 'https://www.jumbo.cl/tecnologia'},
                    {'name': 'Hogar', 'url': 'https://www.jumbo.cl/hogar'}
                ]
            },
            'santa_isabel': {
                'name': 'Santa Isabel',
                'base_url': 'https://www.santaisabel.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.santaisabel.cl/ofertas'},
                    {'name': 'Tecnología', 'url': 'https://www.santaisabel.cl/tecnologia'},
                    {'name': 'Hogar', 'url': 'https://www.santaisabel.cl/hogar'}
                ]
            },
            'alcampo': {
                'name': 'Alcampo',
                'base_url': 'https://www.alcampo.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.alcampo.cl/ofertas'},
                    {'name': 'Tecnología', 'url': 'https://www.alcampo.cl/tecnologia'},
                    {'name': 'Hogar', 'url': 'https://www.alcampo.cl/hogar'}
                ]
            },
            'unimarc': {
                'name': 'Unimarc',
                'base_url': 'https://www.unimarc.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.unimarc.cl/ofertas'},
                    {'name': 'Tecnología', 'url': 'https://www.unimarc.cl/tecnologia'},
                    {'name': 'Hogar', 'url': 'https://www.unimarc.cl/hogar'}
                ]
            },
            'walmart': {
                'name': 'Walmart',
                'base_url': 'https://www.walmart.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.walmart.cl/ofertas'},
                    {'name': 'Tecnología', 'url': 'https://www.walmart.cl/tecnologia'},
                    {'name': 'Hogar', 'url': 'https://www.walmart.cl/hogar'}
                ]
            },
            'tottus': {
                'name': 'Tottus',
                'base_url': 'https://www.tottus.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.tottus.cl/ofertas'},
                    {'name': 'Tecnología', 'url': 'https://www.tottus.cl/tecnologia'},
                    {'name': 'Hogar', 'url': 'https://www.tottus.cl/hogar'}
                ]
            }
        }
    
    def get_page_content(self, url):
        """Obtiene el contenido de una página web con headers mejorados"""
        try:
            print(f"📡 Cargando: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"❌ Error cargando página {url}: {e}")
            return None
    
    def extract_products_from_html(self, html_content, store_name):
        """Extrae productos usando múltiples técnicas específicas por tienda"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        
        # Selectores específicos por tienda
        store_selectors = {
            'falabella': [
                '.pod-item', '.pod-details', '.product-item', '.product-card',
                '[data-pod-type]', '.pod', '.product', '.item'
            ],
            'paris': [
                '.product-item', '.product-card', '.product-grid-item',
                '.product-tile', '.product-container', '.product-box',
                '.product', '.item', '.card', '.producto'
            ],
            'ripley': [
                '.product-item', '.product-card', '.product-grid-item',
                '.product-tile', '.product-container', '.product-box',
                '.product', '.item', '.card'
            ],
            'sodimac': [
                '.product-item', '.product-card', '.product-grid-item',
                '.product-tile', '.product-container', '.product-box',
                '.product', '.item', '.card'
            ],
            'easy': [
                '.product-item', '.product-card', '.product-grid-item',
                '.product-tile', '.product-container', '.product-box',
                '.product', '.item', '.card'
            ],
            'lider': [
                '.product-item', '.product-card', '.product-grid-item',
                '.product-tile', '.product-container', '.product-box',
                '.product', '.item', '.card'
            ],
            'jumbo': [
                '.product-item', '.product-card', '.product-grid-item',
                '.product-tile', '.product-container', '.product-box',
                '.product', '.item', '.card'
            ],
            'santa_isabel': [
                '.product-item', '.product-card', '.product-grid-item',
                '.product-tile', '.product-container', '.product-box',
                '.product', '.item', '.card'
            ],
            'alcampo': [
                '.product-item', '.product-card', '.product-grid-item',
                '.product-tile', '.product-container', '.product-box',
                '.product', '.item', '.card'
            ],
            'unimarc': [
                '.product-item', '.product-card', '.product-grid-item',
                '.product-tile', '.product-container', '.product-box',
                '.product', '.item', '.card'
            ],
            'walmart': [
                '.product-item', '.product-card', '.product-grid-item',
                '.product-tile', '.product-container', '.product-box',
                '.product', '.item', '.card'
            ],
            'tottus': [
                '.product-item', '.product-card', '.product-grid-item',
                '.product-tile', '.product-container', '.product-box',
                '.product', '.item', '.card'
            ]
        }
        
        # Usar selectores específicos de la tienda o genéricos
        selectors = store_selectors.get(store_name, [
            '.product-item', '.product-card', '.product-grid-item',
            '.product-tile', '.product-container', '.product-box',
            '.product', '.item', '.card', '[data-product]',
            '[class*="product"]', '[class*="item"]', '[class*="card"]'
        ])
        
        product_elements = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                product_elements.extend(elements)
                break  # Si encontramos elementos, no necesitamos más selectores
        
        # Extraer información de cada producto
        for element in product_elements[:20]:  # Limitar a 20 productos por página
            product_info = self.extract_product_info(element, store_name)
            if product_info and product_info.get('name'):
                products.append(product_info)
        
        return products
    
    def extract_product_info(self, element, store_name):
        """Extrae información completa de un producto"""
        try:
            name = self.extract_product_name(element, store_name)
            current_price, original_price = self.extract_prices(element)
            discount_percentage = self.extract_discount(element)
            link = self.extract_product_link(element, store_name)
            image = self.extract_product_image(element, store_name)
            
            if name and current_price:
                return {
                    'name': name,
                    'current_price': current_price,
                    'original_price': original_price,
                    'discount_percentage': discount_percentage,
                    'link': link,
                    'image': image,
                    'store': store_name,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"❌ Error extrayendo producto: {e}")
        
        return None
    
    def extract_product_name(self, element, store_name):
        """Extrae el nombre del producto"""
        name_selectors = [
            '.product-name', '.product-title', '.name', '.title',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            '[class*="name"]', '[class*="title"]',
            'a', 'span', 'div'
        ]
        
        for selector in name_selectors:
            name_elem = element.select_one(selector)
            if name_elem:
                name = name_elem.get_text(strip=True)
                if name and len(name) > 3:
                    return name[:200]  # Limitar longitud
        
        return None
    
    def extract_prices(self, element):
        """Extrae precios usando regex mejorado"""
        text = element.get_text()
        
        # Patrones para precios chilenos
        price_patterns = [
            r'\$\s*([\d,]+(?:\.\d{3})*(?:,\d{2})?)',  # $1.000,00
            r'(\d+(?:\.\d{3})*(?:,\d{2})?)\s*pesos',  # 1.000,00 pesos
            r'CLP\s*([\d,]+(?:\.\d{3})*(?:,\d{2})?)',  # CLP 1.000,00
            r'(\d+(?:\.\d{3})*(?:,\d{2})?)\s*CLP',    # 1.000,00 CLP
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Limpiar y convertir precio
                price_str = match.replace('.', '').replace(',', '.')
                try:
                    price = float(price_str)
                    if price > 0:
                        prices.append(price)
                except:
                    continue
        
        if len(prices) >= 2:
            return min(prices), max(prices)  # Precio actual, precio original
        elif len(prices) == 1:
            return prices[0], None
        else:
            return None, None
    
    def extract_discount(self, element):
        """Extrae porcentaje de descuento"""
        text = element.get_text()
        
        # Patrones para descuentos
        discount_patterns = [
            r'(\d+)%\s*off',
            r'(\d+)%\s*descuento',
            r'(\d+)%\s*menos',
            r'-(\d+)%',
            r'(\d+)%\s*de\s*descuento',
            r'ahorra\s*(\d+)%',
            r'(\d+)%\s*rebaja'
        ]
        
        for pattern in discount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    discount = int(match.group(1))
                    if 0 < discount <= 100:
                        return discount
                except:
                    continue
        
        return None
    
    def extract_product_link(self, element, store_name):
        """Extrae el enlace del producto"""
        # Buscar enlaces en el elemento
        link_elem = element.find('a')
        if link_elem and link_elem.get('href'):
            href = link_elem.get('href')
            if href.startswith('http'):
                return href
            else:
                # Construir URL completa
                base_url = self.stores[store_name]['base_url']
                return base_url + href if href.startswith('/') else base_url + '/' + href
        
        return None
    
    def extract_product_image(self, element, store_name):
        """Extrae la imagen del producto"""
        # Buscar imágenes en el elemento
        img_elem = element.find('img')
        if img_elem and img_elem.get('src'):
            src = img_elem.get('src')
            if src.startswith('http'):
                return src
            else:
                # Construir URL completa
                base_url = self.stores[store_name]['base_url']
                return base_url + src if src.startswith('/') else base_url + '/' + src
        
        return None
    
    def scrape_store(self, store_name):
        """Scraping de una tienda específica"""
        if store_name not in self.stores:
            print(f"❌ Tienda {store_name} no configurada")
            return []
        
        store_config = self.stores[store_name]
        all_products = []
        
        print(f"\n🏪 Scraping {store_config['name']}...")
        
        for category in store_config['categories']:
            print(f"  📂 Categoría: {category['name']}")
            
            html_content = self.get_page_content(category['url'])
            if html_content:
                products = self.extract_products_from_html(html_content, store_name)
                all_products.extend(products)
                print(f"    ✅ {len(products)} productos encontrados")
                
                # Pausa entre categorías para evitar bloqueos
                time.sleep(2)
            else:
                print(f"    ❌ Error cargando categoría")
        
        return all_products
    
    def save_products(self, products, store_name):
        """Guarda productos usando el data manager si está disponible"""
        if not products:
            return None
        
        try:
            # Guardar en base de datos si hay data manager
            saved_count = 0
            for product in products:
                if hasattr(self, 'data_manager') and self.data_manager:
                    if self.data_manager.save_product_to_db(product):
                        saved_count += 1
                else:
                    # Fallback: guardar en JSON
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
            
            if saved_count > 0:
                print(f"✅ {saved_count} productos guardados en base de datos")
                
                # También guardar en JSON y CSV si hay data manager
                if hasattr(self, 'data_manager') and self.data_manager:
                    self.data_manager.save_products_to_json(products, store_name)
                    self.data_manager.save_products_to_csv(products, store_name)
                
                return f"database_{saved_count}_products"
            
            return None
            
        except Exception as e:
            print(f"❌ Error guardando productos: {e}")
            return None
    
    def run_scraping(self, stores_to_scrape=None):
        """Ejecuta el scraping de todas las tiendas o las especificadas"""
        if stores_to_scrape is None:
            stores_to_scrape = list(self.stores.keys())
        
        results = {}
        total_products = 0
        
        print("🚀 Iniciando scraping de tiendas chilenas...")
        print(f"📊 Tiendas a procesar: {len(stores_to_scrape)}")
        print("=" * 50)
        
        for store_name in stores_to_scrape:
            if store_name in self.stores:
                products = self.scrape_store(store_name)
                if products:
                    results[store_name] = products
                    total_products += len(products)
                    self.save_products(products, store_name)
                
                # Pausa entre tiendas
                time.sleep(3)
        
        print("\n" + "=" * 50)
        print(f"✅ Scraping completado!")
        print(f"📦 Total de productos encontrados: {total_products}")
        print(f"🏪 Tiendas con productos: {len(results)}")
        
        return results

def main():
    """Función principal para testing"""
    scraper = ScrapingChileCompleto()
    results = scraper.run_scraping()
    
    if results:
        print("\n📊 Resumen por tienda:")
        for store, products in results.items():
            print(f"🏪 {store}: {len(products)} productos")

if __name__ == "__main__":
    main() 