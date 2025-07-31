#!/usr/bin/env python3
"""
DESCUENTOS RATA - App de Scraping de Ofertas Chilenas
Versión 1.0 - Scraping automático de productos con 70%+ de descuento
"""

import os
import sys
import json
import time
import requests
import sqlite3
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
import hashlib

# Configuración
MIN_DISCOUNT_PERCENTAGE = 70  # Solo productos con 70%+ de descuento
TELEGRAM_ALERT_THRESHOLD = 85  # Alerta Telegram para 85%+ de descuento
MAX_PRODUCTS_PER_STORE = 50   # Límite de productos por tienda

class DescuentosRata:
    def __init__(self):
        self.data_dir = "data"
        self.db_path = os.path.join(self.data_dir, "descuentos_rata.db")
        self.json_path = os.path.join(self.data_dir, "productos.json")
        
        # Crear directorio de datos si no existe
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Headers para evitar bloqueos
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
        
        # Configuración de tiendas chilenas (solo las que funcionan)
        self.stores = {
            'paris': {
                'name': 'Paris',
                'base_url': 'https://www.paris.cl',
                'categories': [
                    {'name': 'Página Principal', 'url': 'https://www.paris.cl'}
                ]
            },
            'hites': {
                'name': 'Hites',
                'base_url': 'https://www.hites.com',
                'categories': [
                    {'name': 'Liquidación', 'url': 'https://www.hites.com/liquidacion'},
                    {'name': 'Tecnología', 'url': 'https://www.hites.com/tecnologia'},
                    {'name': 'Hogar', 'url': 'https://www.hites.com/hogar'},
                    {'name': 'Deportes', 'url': 'https://www.hites.com/deportes'},
                    {'name': 'Página Principal', 'url': 'https://www.hites.com'}
                ]
            },
            'falabella': {
                'name': 'Falabella',
                'base_url': 'https://www.falabella.com',
                'categories': [
                    {'name': 'Liquidación', 'url': 'https://www.falabella.com/falabella-cl/collection/liquidacion'},
                    {'name': 'Ofertas', 'url': 'https://www.falabella.com/falabella-cl/collection/ofertas'},
                    {'name': 'Tecnología', 'url': 'https://www.falabella.com/falabella-cl/category/cat20002/Tecnologia'}
                ]
            },
            'sodimac': {
                'name': 'Sodimac',
                'base_url': 'https://www.sodimac.cl',
                'categories': [
                    {'name': 'Liquidación', 'url': 'https://www.sodimac.cl/sodimac-cl/collection/liquidacion'},
                    {'name': 'Ofertas', 'url': 'https://www.sodimac.cl/sodimac-cl/ofertas'},
                    {'name': 'Herramientas', 'url': 'https://www.sodimac.cl/sodimac-cl/category/cat20002/Herramientas'}
                ]
            },
            'easy': {
                'name': 'Easy',
                'base_url': 'https://www.easy.cl',
                'categories': [
                    {'name': 'Liquidación', 'url': 'https://www.easy.cl/easy-cl/collection/liquidacion'},
                    {'name': 'Ofertas', 'url': 'https://www.easy.cl/easy-cl/ofertas'},
                    {'name': 'Herramientas', 'url': 'https://www.easy.cl/easy-cl/category/cat20002/Herramientas'}
                ]
            }
        }
        
        # Inicializar base de datos
        self.init_database()
        
        # Configuración de Telegram (opcional)
        self.telegram_config = {
            'enabled': False,
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID', '')
        }
    
    def init_database(self):
        """Inicializa la base de datos SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash_id TEXT UNIQUE,
                nombre TEXT NOT NULL,
                precio_actual REAL NOT NULL,
                precio_original REAL,
                descuento_porcentaje REAL,
                enlace TEXT,
                imagen TEXT,
                tienda TEXT NOT NULL,
                categoria TEXT,
                confiabilidad_score REAL DEFAULT 1.0,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de historial de precios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial_precios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_hash TEXT,
                precio REAL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (producto_hash) REFERENCES productos (hash_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_page_content(self, url: str) -> Optional[str]:
        """Obtiene el contenido de una página web con retry"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"📡 Cargando: {url} (intento {attempt + 1})")
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
                print(f"❌ Error cargando página {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponencial
                else:
                    return None
        return None
    
    def extract_products_from_html(self, html_content: str, store_name: str) -> List[Dict]:
        """Extrae productos del HTML usando selectores específicos por tienda"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        
        # Selectores específicos por tienda (solo las que funcionan)
        store_selectors = {
            'paris': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container', '.product-box'],
            'hites': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container', '.product-box'],
            'falabella': ['.pod-item', '.pod-details', '.product-item', '.product-card', '.product-grid-item'],
            'sodimac': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container'],
            'easy': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container']
        }
        
        selectors = store_selectors.get(store_name, ['.product-item', '.product-card'])
        
        product_elements = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                product_elements.extend(elements)
                break
        
        # Extraer información de cada producto
        for element in product_elements[:MAX_PRODUCTS_PER_STORE]:
            product_info = self.extract_product_info(element, store_name)
            if product_info and self.is_valid_discount(product_info):
                products.append(product_info)
        
        return products
    
    def extract_product_info(self, element, store_name: str) -> Optional[Dict]:
        """Extrae información completa de un producto"""
        try:
            name = self.extract_product_name(element)
            current_price, original_price = self.extract_prices(element)
            link = self.extract_product_link(element, store_name)
            image = self.extract_product_image(element, store_name)
            category = self.extract_category(element)
            
            if name and current_price:
                # Calcular descuento si no viene
                discount_percentage = self.calculate_discount_percentage(current_price, original_price)
                
                # Solo incluir si cumple el descuento mínimo
                if discount_percentage >= MIN_DISCOUNT_PERCENTAGE:
                    # Generar hash único
                    hash_id = self.generate_product_hash(name, store_name)
                    
                    # Calcular score de confiabilidad
                    confiabilidad_score = self.calculate_reliability_score(current_price, original_price, discount_percentage)
                    
                    return {
                        'hash_id': hash_id,
                        'nombre': name,
                        'precio_actual': current_price,
                        'precio_original': original_price,
                        'descuento_porcentaje': discount_percentage,
                        'enlace': link,
                        'imagen': image,
                        'tienda': store_name,
                        'categoria': category,
                        'confiabilidad_score': confiabilidad_score,
                        'fecha_creacion': datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"❌ Error extrayendo producto: {e}")
        
        return None
    
    def extract_product_name(self, element) -> Optional[str]:
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
    
    def extract_prices(self, element) -> tuple:
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
    
    def extract_product_link(self, element, store_name: str) -> Optional[str]:
        """Extrae el enlace del producto"""
        link_elem = element.find('a')
        if link_elem and link_elem.get('href'):
            href = link_elem.get('href')
            if href.startswith('http'):
                return href
            else:
                base_url = self.stores[store_name]['base_url']
                return base_url + href if href.startswith('/') else base_url + '/' + href
        return None
    
    def extract_product_image(self, element, store_name: str) -> Optional[str]:
        """Extrae la imagen del producto"""
        img_elem = element.find('img')
        if img_elem and img_elem.get('src'):
            src = img_elem.get('src')
            if src.startswith('http'):
                return src
            else:
                base_url = self.stores[store_name]['base_url']
                return base_url + src if src.startswith('/') else base_url + '/' + src
        return None
    
    def extract_category(self, element) -> Optional[str]:
        """Extrae la categoría del producto"""
        # Buscar elementos que puedan contener categoría
        category_selectors = ['.category', '.breadcrumb', '[class*="category"]']
        for selector in category_selectors:
            cat_elem = element.select_one(selector)
            if cat_elem:
                return cat_elem.get_text(strip=True)[:100]
        return None
    
    def calculate_discount_percentage(self, current_price: float, original_price: Optional[float]) -> float:
        """Calcula el porcentaje de descuento"""
        if not original_price or original_price <= 0:
            return 0.0
        
        discount = ((original_price - current_price) / original_price) * 100
        return round(discount, 2)
    
    def is_valid_discount(self, product: Dict) -> bool:
        """Verifica si el producto cumple con el descuento mínimo"""
        return product.get('descuento_porcentaje', 0) >= MIN_DISCOUNT_PERCENTAGE
    
    def generate_product_hash(self, name: str, store: str) -> str:
        """Genera un hash único para el producto"""
        text = f"{name.lower().strip()}_{store.lower()}"
        return hashlib.md5(text.encode()).hexdigest()
    
    def calculate_reliability_score(self, current_price: float, original_price: Optional[float], discount: float) -> float:
        """Calcula un score de confiabilidad del descuento"""
        score = 1.0
        
        # Penalizar descuentos muy altos (posible precio inflado)
        if discount > 90:
            score -= 0.3
        elif discount > 80:
            score -= 0.1
        
        # Penalizar si no hay precio original
        if not original_price:
            score -= 0.2
        
        # Penalizar precios muy bajos
        if current_price < 1000:
            score -= 0.1
        
        return max(0.1, score)
    
    def save_product_to_db(self, product: Dict) -> bool:
        """Guarda un producto en la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insertar o actualizar producto
            cursor.execute('''
                INSERT OR REPLACE INTO productos 
                (hash_id, nombre, precio_actual, precio_original, descuento_porcentaje, 
                 enlace, imagen, tienda, categoria, confiabilidad_score, fecha_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product['hash_id'], product['nombre'], product['precio_actual'],
                product['precio_original'], product['descuento_porcentaje'],
                product['enlace'], product['imagen'], product['tienda'],
                product['categoria'], product['confiabilidad_score'],
                datetime.now().isoformat()
            ))
            
            # Guardar en historial de precios
            cursor.execute('''
                INSERT INTO historial_precios (producto_hash, precio, fecha)
                VALUES (?, ?, ?)
            ''', (product['hash_id'], product['precio_actual'], datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error guardando producto en DB: {e}")
            return False
    
    def save_to_json(self, products: List[Dict]):
        """Guarda productos en archivo JSON"""
        try:
            data = {
                'fecha_actualizacion': datetime.now().isoformat(),
                'total_productos': len(products),
                'descuento_minimo': MIN_DISCOUNT_PERCENTAGE,
                'productos': products
            }
            
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {len(products)} productos guardados en {self.json_path}")
            
        except Exception as e:
            print(f"❌ Error guardando JSON: {e}")
    
    def send_telegram_alert(self, product: Dict):
        """Envía alerta por Telegram si el descuento es muy alto"""
        if not self.telegram_config['enabled'] or not self.telegram_config['bot_token']:
            return
        
        if product.get('descuento_porcentaje', 0) >= TELEGRAM_ALERT_THRESHOLD:
            try:
                message = f"""
🚨 ¡OFERTA EXTREMA DETECTADA! 🚨

🏪 {product['tienda'].upper()}
📦 {product['nombre']}
💰 ${product['precio_actual']:,} (antes ${product['precio_original']:,})
🎯 {product['descuento_porcentaje']}% DE DESCUENTO
🔗 {product['enlace']}
⭐ Confiabilidad: {product['confiabilidad_score']:.1f}/1.0
                """.strip()
                
                url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
                data = {
                    'chat_id': self.telegram_config['chat_id'],
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, data=data)
                if response.status_code == 200:
                    print(f"📱 Alerta Telegram enviada para {product['nombre']}")
                
            except Exception as e:
                print(f"❌ Error enviando alerta Telegram: {e}")
    
    def scrape_store(self, store_name: str) -> List[Dict]:
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
                print(f"    ✅ {len(products)} productos con {MIN_DISCOUNT_PERCENTAGE}%+ descuento")
                
                # Pausa entre categorías
                time.sleep(2)
            else:
                print(f"    ❌ Error cargando categoría")
        
        return all_products
    
    def run_scraping(self, stores_to_scrape: Optional[List[str]] = None) -> Dict:
        """Ejecuta el scraping de todas las tiendas o las especificadas"""
        if stores_to_scrape is None:
            stores_to_scrape = list(self.stores.keys())
        
        results = {}
        total_products = 0
        all_products = []
        
        print("🚀 Iniciando scraping de ofertas chilenas...")
        print(f"📊 Tiendas a procesar: {len(stores_to_scrape)}")
        print(f"🎯 Descuento mínimo: {MIN_DISCOUNT_PERCENTAGE}%")
        print("=" * 60)
        
        for store_name in stores_to_scrape:
            if store_name in self.stores:
                products = self.scrape_store(store_name)
                if products:
                    results[store_name] = products
                    total_products += len(products)
                    all_products.extend(products)
                    
                    # Guardar productos en DB
                    for product in products:
                        self.save_product_to_db(product)
                        self.send_telegram_alert(product)
                
                # Pausa entre tiendas
                time.sleep(3)
        
        # Guardar en JSON
        if all_products:
            self.save_to_json(all_products)
        
        print("\n" + "=" * 60)
        print(f"✅ Scraping completado!")
        print(f"📦 Total de productos con {MIN_DISCOUNT_PERCENTAGE}%+ descuento: {total_products}")
        print(f"🏪 Tiendas con ofertas: {len(results)}")
        
        return results
    
    def get_latest_offers(self, limit: int = 20) -> List[Dict]:
        """Obtiene las últimas ofertas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM productos 
            ORDER BY fecha_actualizacion DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        products = []
        
        for row in cursor.fetchall():
            product = dict(zip(columns, row))
            products.append(product)
        
        conn.close()
        return products
    
    def get_top_offers(self, limit: int = 10) -> List[Dict]:
        """Obtiene las mejores ofertas por descuento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM productos 
            ORDER BY descuento_porcentaje DESC, confiabilidad_score DESC
            LIMIT ?
        ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        products = []
        
        for row in cursor.fetchall():
            product = dict(zip(columns, row))
            products.append(product)
        
        conn.close()
        return products
    
    def search_products(self, query: str) -> List[Dict]:
        """Busca productos por palabra clave"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM productos 
            WHERE nombre LIKE ? 
            ORDER BY descuento_porcentaje DESC
        ''', (f'%{query}%',))
        
        columns = [description[0] for description in cursor.description]
        products = []
        
        for row in cursor.fetchall():
            product = dict(zip(columns, row))
            products.append(product)
        
        conn.close()
        return products
    
    def show_menu(self):
        """Muestra el menú principal"""
        while True:
            self.clear_screen()
            print("🐀 DESCUENTOS RATA - Ofertas Chilenas")
            print("=" * 50)
            
            # Mostrar estadísticas rápidas
            latest_offers = self.get_latest_offers(5)
            print(f"📊 Últimas ofertas: {len(latest_offers)}")
            if latest_offers:
                avg_discount = sum(p['descuento_porcentaje'] for p in latest_offers) / len(latest_offers)
                print(f"🎯 Descuento promedio: {avg_discount:.1f}%")
            print()
            
            print("OPCIONES DISPONIBLES:")
            print("1. 📦 Ver últimas ofertas")
            print("2. 🏆 Ver top 10 mejores ofertas")
            print("3. 🔍 Buscar producto")
            print("4. 🚀 Forzar scraping")
            print("5. 📊 Ver estadísticas")
            print("6. ❌ Salir")
            print()
            
            try:
                option = input("Selecciona una opción (1-6): ").strip()
                
                if option == "1":
                    self.show_latest_offers()
                elif option == "2":
                    self.show_top_offers()
                elif option == "3":
                    self.show_search()
                elif option == "4":
                    self.show_scraping()
                elif option == "5":
                    self.show_stats()
                elif option == "6":
                    print("\n👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción inválida. Presiona Enter para continuar...")
                    input()
                    
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Presiona Enter para continuar...")
    
    def show_latest_offers(self):
        """Muestra las últimas ofertas"""
        self.clear_screen()
        print("📦 ÚLTIMAS OFERTAS")
        print("=" * 30)
        
        offers = self.get_latest_offers(20)
        if offers:
            for i, offer in enumerate(offers, 1):
                print(f"{i}. {offer['nombre'][:50]}...")
                print(f"   💰 ${offer['precio_actual']:,} | 🏪 {offer['tienda']}")
                print(f"   🎯 {offer['descuento_porcentaje']}% descuento | ⭐ {offer['confiabilidad_score']:.1f}")
                print()
        else:
            print("❌ No hay ofertas disponibles")
        
        input("Presiona Enter para continuar...")
    
    def show_top_offers(self):
        """Muestra las mejores ofertas"""
        self.clear_screen()
        print("🏆 TOP 10 MEJORES OFERTAS")
        print("=" * 35)
        
        offers = self.get_top_offers(10)
        if offers:
            for i, offer in enumerate(offers, 1):
                print(f"{i}. {offer['nombre'][:45]}...")
                print(f"   💰 ${offer['precio_actual']:,} | 🏪 {offer['tienda']}")
                print(f"   🎯 {offer['descuento_porcentaje']}% descuento | ⭐ {offer['confiabilidad_score']:.1f}")
                if offer['enlace']:
                    print(f"   🔗 {offer['enlace']}")
                print()
        else:
            print("❌ No hay ofertas disponibles")
        
        input("Presiona Enter para continuar...")
    
    def show_search(self):
        """Muestra búsqueda de productos"""
        self.clear_screen()
        print("🔍 BÚSQUEDA DE PRODUCTOS")
        print("=" * 30)
        
        query = input("Ingresa el producto a buscar: ").strip()
        if not query:
            print("❌ Debes ingresar un término de búsqueda")
            input("Presiona Enter para continuar...")
            return
        
        print(f"\n🔍 Buscando: {query}")
        results = self.search_products(query)
        
        if results:
            print(f"\n✅ Encontrados {len(results)} productos:")
            for i, product in enumerate(results[:10], 1):
                print(f"{i}. {product['nombre'][:50]}...")
                print(f"   💰 ${product['precio_actual']:,} | 🏪 {product['tienda']}")
                print(f"   🎯 {product['descuento_porcentaje']}% descuento")
                print()
        else:
            print("❌ No se encontraron productos")
        
        input("Presiona Enter para continuar...")
    
    def show_scraping(self):
        """Muestra el scraping"""
        self.clear_screen()
        print("🚀 FORZAR SCRAPING")
        print("=" * 25)
        
        print("📡 Iniciando búsqueda de ofertas...")
        print("⏳ Esto puede tomar varios minutos...")
        print("🏪 Tiendas: Paris, Hites, Falabella, Sodimac, Easy")
        print()
        
        try:
            results = self.run_scraping()
            
            if results:
                total_products = sum(len(products) for products in results.values())
                print(f"\n✅ Scraping completado!")
                print(f"📦 Total de productos con {MIN_DISCOUNT_PERCENTAGE}%+ descuento: {total_products}")
                
                for store, products in results.items():
                    if products:
                        print(f"🏪 {store}: {len(products)} ofertas")
            else:
                print("\n❌ No se encontraron ofertas")
                
        except Exception as e:
            print(f"\n❌ Error durante el scraping: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def show_stats(self):
        """Muestra estadísticas"""
        self.clear_screen()
        print("📊 ESTADÍSTICAS")
        print("=" * 20)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de productos
        cursor.execute("SELECT COUNT(*) FROM productos")
        total_products = cursor.fetchone()[0]
        
        # Promedio de descuento
        cursor.execute("SELECT AVG(descuento_porcentaje) FROM productos")
        avg_discount = cursor.fetchone()[0] or 0
        
        # Mejor oferta
        cursor.execute("SELECT MAX(descuento_porcentaje) FROM productos")
        max_discount = cursor.fetchone()[0] or 0
        
        # Productos por tienda
        cursor.execute("SELECT tienda, COUNT(*) FROM productos GROUP BY tienda")
        store_stats = cursor.fetchall()
        
        conn.close()
        
        print(f"📦 Total de productos: {total_products}")
        print(f"🎯 Descuento promedio: {avg_discount:.1f}%")
        print(f"🏆 Mejor descuento: {max_discount:.1f}%")
        print()
        print("🏪 Productos por tienda:")
        for store, count in store_stats:
            print(f"   {store}: {count}")
        
        input("\nPresiona Enter para continuar...")
    
    def clear_screen(self):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Función principal"""
    try:
        app = DescuentosRata()
        app.show_menu()
    except Exception as e:
        print(f"❌ Error iniciando la aplicación: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main() 