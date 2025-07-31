#!/usr/bin/env python3
"""
DESCUENTOSGO - Scanner Automático Infinito
Versión 2.0 - Escaneo automático 24/7 de ofertas chilenas
"""

import os
import sys
import json
import time
import requests
import sqlite3
import threading
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional, Set
import hashlib

# Configuración
MIN_DISCOUNT_PERCENTAGE = 70  # Solo productos con 70%+ de descuento
TELEGRAM_ALERT_THRESHOLD = 85  # Alerta Telegram para 85%+ de descuento
MAX_PRODUCTS_PER_STORE = 100   # Límite de productos por tienda
SCAN_INTERVAL = 300  # 5 minutos entre escaneos

class DescuentosGO:
    def __init__(self):
        self.data_dir = "data"
        self.db_path = os.path.join(self.data_dir, "descuentosgo.db")
        self.json_path = os.path.join(self.data_dir, "productos_descuentosgo.json")
        
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
        
        # Configuración de tiendas chilenas expandida
        self.stores = {
            'paris': {
                'name': 'Paris',
                'base_url': 'https://www.paris.cl',
                'categories': [
                    {'name': 'Página Principal', 'url': 'https://www.paris.cl', 'enabled': True},
                    {'name': 'Tecnología', 'url': 'https://www.paris.cl/tecnologia', 'enabled': True},
                    {'name': 'Hogar', 'url': 'https://www.paris.cl/hogar', 'enabled': True},
                    {'name': 'Deportes', 'url': 'https://www.paris.cl/deportes', 'enabled': True},
                    {'name': 'Ropa', 'url': 'https://www.paris.cl/ropa', 'enabled': True}
                ]
            },
            'hites': {
                'name': 'Hites',
                'base_url': 'https://www.hites.com',
                'categories': [
                    {'name': 'Liquidación', 'url': 'https://www.hites.com/liquidacion', 'enabled': True},
                    {'name': 'Tecnología', 'url': 'https://www.hites.com/tecnologia', 'enabled': True},
                    {'name': 'Hogar', 'url': 'https://www.hites.com/hogar', 'enabled': True},
                    {'name': 'Deportes', 'url': 'https://www.hites.com/deportes', 'enabled': True},
                    {'name': 'Página Principal', 'url': 'https://www.hites.com', 'enabled': True}
                ]
            },
            'falabella': {
                'name': 'Falabella',
                'base_url': 'https://www.falabella.com',
                'categories': [
                    {'name': 'Liquidación', 'url': 'https://www.falabella.com/falabella-cl/collection/liquidacion', 'enabled': True},
                    {'name': 'Ofertas', 'url': 'https://www.falabella.com/falabella-cl/collection/ofertas', 'enabled': True},
                    {'name': 'Tecnología', 'url': 'https://www.falabella.com/falabella-cl/category/cat20002/Tecnologia', 'enabled': True},
                    {'name': 'Hogar', 'url': 'https://www.falabella.com/falabella-cl/category/cat20001/Hogar-y-Muebles', 'enabled': True},
                    {'name': 'Deportes', 'url': 'https://www.falabella.com/falabella-cl/category/cat20003/Deportes', 'enabled': True}
                ]
            },
            'sodimac': {
                'name': 'Sodimac',
                'base_url': 'https://www.sodimac.cl',
                'categories': [
                    {'name': 'Liquidación', 'url': 'https://www.sodimac.cl/sodimac-cl/collection/liquidacion', 'enabled': True},
                    {'name': 'Ofertas', 'url': 'https://www.sodimac.cl/sodimac-cl/ofertas', 'enabled': True},
                    {'name': 'Herramientas', 'url': 'https://www.sodimac.cl/sodimac-cl/category/cat20002/Herramientas', 'enabled': True},
                    {'name': 'Jardín', 'url': 'https://www.sodimac.cl/sodimac-cl/category/cat20001/Jardin-y-Aire-Libre', 'enabled': True},
                    {'name': 'Construcción', 'url': 'https://www.sodimac.cl/sodimac-cl/category/cat20003/Construccion', 'enabled': True}
                ]
            },
            'easy': {
                'name': 'Easy',
                'base_url': 'https://www.easy.cl',
                'categories': [
                    {'name': 'Liquidación', 'url': 'https://www.easy.cl/easy-cl/collection/liquidacion', 'enabled': True},
                    {'name': 'Ofertas', 'url': 'https://www.easy.cl/easy-cl/ofertas', 'enabled': True},
                    {'name': 'Herramientas', 'url': 'https://www.easy.cl/easy-cl/category/cat20002/Herramientas', 'enabled': True},
                    {'name': 'Jardín', 'url': 'https://www.easy.cl/easy-cl/category/cat20001/Jardin-y-Aire-Libre', 'enabled': True},
                    {'name': 'Hogar', 'url': 'https://www.easy.cl/easy-cl/category/cat20003/Hogar-y-Decoracion', 'enabled': True}
                ]
            },
            'lider': {
                'name': 'Líder',
                'base_url': 'https://www.lider.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.lider.cl/supermercado/category/Ofertas', 'enabled': True},
                    {'name': 'Tecnología', 'url': 'https://www.lider.cl/supermercado/category/Tecnologia', 'enabled': True},
                    {'name': 'Hogar', 'url': 'https://www.lider.cl/supermercado/category/Hogar', 'enabled': True},
                    {'name': 'Deportes', 'url': 'https://www.lider.cl/supermercado/category/Deportes', 'enabled': True},
                    {'name': 'Página Principal', 'url': 'https://www.lider.cl', 'enabled': True}
                ]
            },
            'jumbo': {
                'name': 'Jumbo',
                'base_url': 'https://www.jumbo.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.jumbo.cl/ofertas', 'enabled': True},
                    {'name': 'Tecnología', 'url': 'https://www.jumbo.cl/tecnologia', 'enabled': True},
                    {'name': 'Hogar', 'url': 'https://www.jumbo.cl/hogar', 'enabled': True},
                    {'name': 'Deportes', 'url': 'https://www.jumbo.cl/deportes', 'enabled': True},
                    {'name': 'Página Principal', 'url': 'https://www.jumbo.cl', 'enabled': True}
                ]
            },
            'santa_isabel': {
                'name': 'Santa Isabel',
                'base_url': 'https://www.santaisabel.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.santaisabel.cl/ofertas', 'enabled': True},
                    {'name': 'Tecnología', 'url': 'https://www.santaisabel.cl/tecnologia', 'enabled': True},
                    {'name': 'Hogar', 'url': 'https://www.santaisabel.cl/hogar', 'enabled': True},
                    {'name': 'Página Principal', 'url': 'https://www.santaisabel.cl', 'enabled': True}
                ]
            },
            'alcampo': {
                'name': 'Alcampo',
                'base_url': 'https://www.alcampo.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.alcampo.cl/ofertas', 'enabled': True},
                    {'name': 'Tecnología', 'url': 'https://www.alcampo.cl/tecnologia', 'enabled': True},
                    {'name': 'Hogar', 'url': 'https://www.alcampo.cl/hogar', 'enabled': True},
                    {'name': 'Página Principal', 'url': 'https://www.alcampo.cl', 'enabled': True}
                ]
            },
            'unimarc': {
                'name': 'Unimarc',
                'base_url': 'https://www.unimarc.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.unimarc.cl/ofertas', 'enabled': True},
                    {'name': 'Tecnología', 'url': 'https://www.unimarc.cl/tecnologia', 'enabled': True},
                    {'name': 'Hogar', 'url': 'https://www.unimarc.cl/hogar', 'enabled': True},
                    {'name': 'Página Principal', 'url': 'https://www.unimarc.cl', 'enabled': True}
                ]
            },
            'walmart': {
                'name': 'Walmart',
                'base_url': 'https://www.walmart.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.walmart.cl/ofertas', 'enabled': True},
                    {'name': 'Tecnología', 'url': 'https://www.walmart.cl/tecnologia', 'enabled': True},
                    {'name': 'Hogar', 'url': 'https://www.walmart.cl/hogar', 'enabled': True},
                    {'name': 'Página Principal', 'url': 'https://www.walmart.cl', 'enabled': True}
                ]
            },
            'tottus': {
                'name': 'Tottus',
                'base_url': 'https://www.tottus.cl',
                'categories': [
                    {'name': 'Ofertas', 'url': 'https://www.tottus.cl/ofertas', 'enabled': True},
                    {'name': 'Tecnología', 'url': 'https://www.tottus.cl/tecnologia', 'enabled': True},
                    {'name': 'Hogar', 'url': 'https://www.tottus.cl/hogar', 'enabled': True},
                    {'name': 'Página Principal', 'url': 'https://www.tottus.cl', 'enabled': True}
                ]
            }
        }
        
        # Variables de control del scanner
        self.scanner_running = False
        self.scanner_thread = None
        self.total_scans = 0
        self.total_products_found = 0
        self.last_scan_time = None
        
        # Inicializar base de datos
        self.init_database()
        
        # Configuración de Telegram
        self.telegram_config = {
            'enabled': True,  # Habilitado por defecto
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', '8442920382:AAG_FpAAoJoWwKt9YAGv0fe5skB8fT1T2xg'),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
            'notifications_sent': 0
        }
        
        # Productos ya notificados para evitar spam
        self.notified_products = set()
    
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
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notificado_telegram BOOLEAN DEFAULT FALSE
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
        
        # Tabla de logs del scanner
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scanner_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_number INTEGER,
                fecha_inicio TIMESTAMP,
                fecha_fin TIMESTAMP,
                productos_encontrados INTEGER,
                tiendas_escaneadas INTEGER,
                duracion_segundos INTEGER
            )
        ''')
        
        conn.commit()
        conn.close() 

    def get_page_content(self, url: str) -> Optional[str]:
        """Obtiene el contenido de una página web con retry"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
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
        
        # Selectores específicos por tienda
        store_selectors = {
            'paris': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container', '.product-box'],
            'hites': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container', '.product-box'],
            'falabella': ['.pod-item', '.pod-details', '.product-item', '.product-card', '.product-grid-item'],
            'sodimac': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container'],
            'easy': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container'],
            'lider': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container'],
            'jumbo': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container'],
            'santa_isabel': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container'],
            'alcampo': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container'],
            'unimarc': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container'],
            'walmart': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container'],
            'tottus': ['.product-item', '.product-card', '.product-grid-item', '.product-tile', '.product-container']
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
            pass
        
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
            
            # Verificar si el producto ya existe
            cursor.execute('SELECT hash_id FROM productos WHERE hash_id = ?', (product['hash_id'],))
            exists = cursor.fetchone()
            
            if exists:
                # Actualizar producto existente
                cursor.execute('''
                    UPDATE productos 
                    SET precio_actual = ?, precio_original = ?, descuento_porcentaje = ?,
                        confiabilidad_score = ?, fecha_actualizacion = ?
                    WHERE hash_id = ?
                ''', (
                    product['precio_actual'], product['precio_original'],
                    product['descuento_porcentaje'], product['confiabilidad_score'],
                    datetime.now().isoformat(), product['hash_id']
                ))
            else:
                # Insertar nuevo producto
                cursor.execute('''
                    INSERT INTO productos 
                    (hash_id, nombre, precio_actual, precio_original, descuento_porcentaje, 
                     enlace, imagen, tienda, categoria, confiabilidad_score, fecha_creacion)
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
            return False
    
    def send_telegram_alert(self, product: Dict) -> bool:
        """Envía alerta por Telegram si el descuento es muy alto"""
        if not self.telegram_config['enabled'] or not self.telegram_config['bot_token']:
            return False
        
        # Verificar si ya fue notificado
        if product['hash_id'] in self.notified_products:
            return False
        
        if product.get('descuento_porcentaje', 0) >= TELEGRAM_ALERT_THRESHOLD:
            try:
                message = f"""
🚨 ¡OFERTA EXTREMA DETECTADA! 🚨

🏪 {product['tienda'].upper()}
📦 {product['nombre']}

💰 Precio actual: ${product['precio_actual']:,}
💸 Precio original: ${product['precio_original']:,}
🎯 Descuento: {product['descuento_porcentaje']}%
⭐ Confiabilidad: {product['confiabilidad_score']:.1f}/1.0

🔗 {product['enlace']}

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}
                """.strip()
                
                url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
                data = {
                    'chat_id': self.telegram_config['chat_id'],
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, data=data, timeout=10)
                if response.status_code == 200:
                    # Marcar como notificado
                    self.notified_products.add(product['hash_id'])
                    self.telegram_config['notifications_sent'] += 1
                    
                    # Actualizar en base de datos
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE productos SET notificado_telegram = TRUE 
                        WHERE hash_id = ?
                    ''', (product['hash_id'],))
                    conn.commit()
                    conn.close()
                    
                    return True
                
            except Exception as e:
                pass
        
        return False
    
    def scrape_store(self, store_name: str) -> List[Dict]:
        """Scraping de una tienda específica"""
        if store_name not in self.stores:
            return []
        
        store_config = self.stores[store_name]
        all_products = []
        
        for category in store_config['categories']:
            if not category.get('enabled', True):
                continue
                
            html_content = self.get_page_content(category['url'])
            if html_content:
                products = self.extract_products_from_html(html_content, store_name)
                all_products.extend(products)
                
                # Pausa entre categorías
                time.sleep(1)
        
        return all_products
    
    def run_single_scan(self) -> Dict:
        """Ejecuta un escaneo completo de todas las tiendas"""
        scan_start = datetime.now()
        self.total_scans += 1
        
        results = {}
        total_products = 0
        all_products = []
        stores_scanned = 0
        
        for store_name in self.stores.keys():
            try:
                products = self.scrape_store(store_name)
                if products:
                    results[store_name] = products
                    total_products += len(products)
                    all_products.extend(products)
                    stores_scanned += 1
                    
                    # Guardar productos en DB y enviar notificaciones
                    for product in products:
                        self.save_product_to_db(product)
                        self.send_telegram_alert(product)
                
                # Pausa entre tiendas
                time.sleep(2)
                
            except Exception as e:
                continue
        
        # Guardar en JSON
        if all_products:
            self.save_to_json(all_products)
        
        # Registrar log del escaneo
        scan_end = datetime.now()
        duration = int((scan_end - scan_start).total_seconds())
        
        self.log_scan(self.total_scans, scan_start, scan_end, total_products, stores_scanned, duration)
        
        self.total_products_found += total_products
        self.last_scan_time = scan_end
        
        return results
    
    def log_scan(self, scan_number: int, start_time: datetime, end_time: datetime, 
                products_found: int, stores_scanned: int, duration: int):
        """Registra un log del escaneo en la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO scanner_logs 
                (scan_number, fecha_inicio, fecha_fin, productos_encontrados, tiendas_escaneadas, duracion_segundos)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (scan_number, start_time.isoformat(), end_time.isoformat(), 
                  products_found, stores_scanned, duration))
            
            conn.commit()
            conn.close()
        except:
            pass
    
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
                
        except Exception as e:
            pass
    
    def scanner_loop(self):
        """Bucle principal del scanner automático"""
        while self.scanner_running:
            try:
                print(f"\n🔄 Escaneo #{self.total_scans + 1} iniciado - {datetime.now().strftime('%H:%M:%S')}")
                results = self.run_single_scan()
                
                total_products = sum(len(products) for products in results.values())
                print(f"✅ Escaneo #{self.total_scans} completado - {total_products} productos encontrados")
                
                # Esperar antes del siguiente escaneo
                print(f"⏳ Esperando {SCAN_INTERVAL} segundos antes del siguiente escaneo...")
                time.sleep(SCAN_INTERVAL)
                
            except Exception as e:
                print(f"❌ Error en escaneo: {e}")
                time.sleep(60)  # Esperar 1 minuto en caso de error
    
    def start_scanner(self):
        """Inicia el scanner automático"""
        if not self.scanner_running:
            self.scanner_running = True
            self.scanner_thread = threading.Thread(target=self.scanner_loop, daemon=True)
            self.scanner_thread.start()
            print("🚀 Scanner automático iniciado!")
            return True
        return False
    
    def stop_scanner(self):
        """Detiene el scanner automático"""
        if self.scanner_running:
            self.scanner_running = False
            if self.scanner_thread:
                self.scanner_thread.join(timeout=5)
            print("⏹️ Scanner automático detenido!")
            return True
        return False 

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
    
    def toggle_category(self, store_name: str, category_name: str):
        """Activa/desactiva una categoría específica"""
        if store_name in self.stores:
            for category in self.stores[store_name]['categories']:
                if category['name'] == category_name:
                    category['enabled'] = not category.get('enabled', True)
                    return category['enabled']
        return False
    
    def toggle_store(self, store_name: str):
        """Activa/desactiva todas las categorías de una tienda"""
        if store_name in self.stores:
            current_state = any(cat.get('enabled', True) for cat in self.stores[store_name]['categories'])
            new_state = not current_state
            
            for category in self.stores[store_name]['categories']:
                category['enabled'] = new_state
            
            return new_state
        return False
    
    def get_enabled_categories_count(self) -> int:
        """Obtiene el número total de categorías habilitadas"""
        count = 0
        for store in self.stores.values():
            for category in store['categories']:
                if category.get('enabled', True):
                    count += 1
        return count
    
    def get_scanner_stats(self) -> Dict:
        """Obtiene estadísticas del scanner"""
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
        
        # Último escaneo
        cursor.execute("SELECT * FROM scanner_logs ORDER BY scan_number DESC LIMIT 1")
        last_scan = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_products': total_products,
            'avg_discount': avg_discount,
            'max_discount': max_discount,
            'store_stats': store_stats,
            'last_scan': last_scan,
            'total_scans': self.total_scans,
            'total_products_found': self.total_products_found,
            'last_scan_time': self.last_scan_time,
            'telegram_notifications': self.telegram_config['notifications_sent'],
            'enabled_categories': self.get_enabled_categories_count()
        }
    
    def show_menu(self):
        """Muestra el menú principal"""
        while True:
            self.clear_screen()
            print("🎯 DESCUENTOSGO - Scanner Automático")
            print("=" * 60)
            
            # Mostrar estado del scanner
            if self.scanner_running:
                print("🟢 Scanner: ACTIVO")
                print(f"📊 Escaneos completados: {self.total_scans}")
                if self.last_scan_time:
                    print(f"⏰ Último escaneo: {self.last_scan_time.strftime('%H:%M:%S')}")
            else:
                print("🔴 Scanner: INACTIVO")
            
            # Mostrar estadísticas rápidas
            stats = self.get_scanner_stats()
            print(f"📦 Total productos: {stats['total_products']}")
            print(f"🎯 Descuento promedio: {stats['avg_discount']:.1f}%")
            print(f"🏆 Mejor descuento: {stats['max_discount']:.1f}%")
            print(f"📱 Notificaciones Telegram: {stats['telegram_notifications']}")
            print(f"✅ Categorías activas: {stats['enabled_categories']}")
            print()
            
            print("OPCIONES DISPONIBLES:")
            print("1. 🚀 Iniciar/Detener Scanner")
            print("2. 📦 Ver últimas ofertas")
            print("3. 🏆 Ver top 10 mejores ofertas")
            print("4. 🔍 Buscar producto")
            print("5. ⚙️ Gestionar categorías")
            print("6. 📊 Ver estadísticas completas")
            print("7. 🔧 Configurar Telegram")
            print("8. ❌ Salir")
            print()
            
            try:
                option = input("Selecciona una opción (1-8): ").strip()
                
                if option == "1":
                    self.toggle_scanner()
                elif option == "2":
                    self.show_latest_offers()
                elif option == "3":
                    self.show_top_offers()
                elif option == "4":
                    self.show_search()
                elif option == "5":
                    self.show_category_manager()
                elif option == "6":
                    self.show_stats()
                elif option == "7":
                    self.show_telegram_config()
                elif option == "8":
                    if self.scanner_running:
                        print("⚠️ Deteniendo scanner antes de salir...")
                        self.stop_scanner()
                    print("\n👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción inválida. Presiona Enter para continuar...")
                    input()
                    
            except KeyboardInterrupt:
                if self.scanner_running:
                    print("\n⚠️ Deteniendo scanner antes de salir...")
                    self.stop_scanner()
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Presiona Enter para continuar...")
    
    def toggle_scanner(self):
        """Inicia o detiene el scanner"""
        if self.scanner_running:
            self.stop_scanner()
        else:
            self.start_scanner()
        
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
    
    def show_category_manager(self):
        """Muestra el gestor de categorías"""
        while True:
            self.clear_screen()
            print("⚙️ GESTOR DE CATEGORÍAS")
            print("=" * 30)
            print()
            
            # Mostrar tiendas y categorías
            for i, (store_key, store) in enumerate(self.stores.items(), 1):
                enabled_categories = sum(1 for cat in store['categories'] if cat.get('enabled', True))
                total_categories = len(store['categories'])
                status = "✅" if enabled_categories > 0 else "❌"
                
                print(f"{i}. {status} {store['name']} ({enabled_categories}/{total_categories})")
                
                # Mostrar categorías si la tienda está seleccionada
                for j, category in enumerate(store['categories'], 1):
                    checkbox = "☑️" if category.get('enabled', True) else "⬜"
                    print(f"   {checkbox} {category['name']}")
                print()
            
            print("OPCIONES:")
            print("1-12. Seleccionar tienda para gestionar")
            print("13. Activar todas las categorías")
            print("14. Desactivar todas las categorías")
            print("15. Volver al menú principal")
            print()
            
            try:
                option = input("Selecciona una opción (1-15): ").strip()
                
                if option.isdigit():
                    option_num = int(option)
                    if 1 <= option_num <= 12:
                        # Gestionar tienda específica
                        store_keys = list(self.stores.keys())
                        if option_num <= len(store_keys):
                            store_key = store_keys[option_num - 1]
                            self.manage_store_categories(store_key)
                    elif option_num == 13:
                        # Activar todas
                        for store in self.stores.values():
                            for category in store['categories']:
                                category['enabled'] = True
                        print("✅ Todas las categorías activadas")
                        input("Presiona Enter para continuar...")
                    elif option_num == 14:
                        # Desactivar todas
                        for store in self.stores.values():
                            for category in store['categories']:
                                category['enabled'] = False
                        print("❌ Todas las categorías desactivadas")
                        input("Presiona Enter para continuar...")
                    elif option_num == 15:
                        break
                    else:
                        print("❌ Opción inválida")
                        input("Presiona Enter para continuar...")
                else:
                    print("❌ Opción inválida")
                    input("Presiona Enter para continuar...")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Presiona Enter para continuar...")
    
    def manage_store_categories(self, store_key: str):
        """Gestiona las categorías de una tienda específica"""
        while True:
            self.clear_screen()
            store = self.stores[store_key]
            print(f"⚙️ GESTIONAR CATEGORÍAS - {store['name']}")
            print("=" * 40)
            print()
            
            for i, category in enumerate(store['categories'], 1):
                checkbox = "☑️" if category.get('enabled', True) else "⬜"
                print(f"{i}. {checkbox} {category['name']}")
            print()
            
            print("OPCIONES:")
            print("1-5. Toggle categoría específica")
            print("6. Activar todas las categorías")
            print("7. Desactivar todas las categorías")
            print("8. Volver")
            print()
            
            try:
                option = input("Selecciona una opción (1-8): ").strip()
                
                if option.isdigit():
                    option_num = int(option)
                    if 1 <= option_num <= 5:
                        # Toggle categoría específica
                        if option_num <= len(store['categories']):
                            category = store['categories'][option_num - 1]
                            new_state = self.toggle_category(store_key, category['name'])
                            status = "activada" if new_state else "desactivada"
                            print(f"✅ Categoría '{category['name']}' {status}")
                            input("Presiona Enter para continuar...")
                    elif option_num == 6:
                        # Activar todas
                        for category in store['categories']:
                            category['enabled'] = True
                        print("✅ Todas las categorías activadas")
                        input("Presiona Enter para continuar...")
                    elif option_num == 7:
                        # Desactivar todas
                        for category in store['categories']:
                            category['enabled'] = False
                        print("❌ Todas las categorías desactivadas")
                        input("Presiona Enter para continuar...")
                    elif option_num == 8:
                        break
                    else:
                        print("❌ Opción inválida")
                        input("Presiona Enter para continuar...")
                else:
                    print("❌ Opción inválida")
                    input("Presiona Enter para continuar...")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Presiona Enter para continuar...")
    
    def show_stats(self):
        """Muestra estadísticas completas"""
        self.clear_screen()
        print("📊 ESTADÍSTICAS COMPLETAS")
        print("=" * 30)
        
        stats = self.get_scanner_stats()
        
        print(f"📦 Total de productos: {stats['total_products']}")
        print(f"🎯 Descuento promedio: {stats['avg_discount']:.1f}%")
        print(f"🏆 Mejor descuento: {stats['max_discount']:.1f}%")
        print(f"🔄 Total de escaneos: {stats['total_scans']}")
        print(f"📱 Notificaciones Telegram: {stats['telegram_notifications']}")
        print(f"✅ Categorías activas: {stats['enabled_categories']}")
        print()
        
        if stats['last_scan']:
            print("📅 ÚLTIMO ESCANEO:")
            print(f"   Número: {stats['last_scan'][1]}")
            print(f"   Productos encontrados: {stats['last_scan'][4]}")
            print(f"   Tiendas escaneadas: {stats['last_scan'][5]}")
            print(f"   Duración: {stats['last_scan'][6]} segundos")
            print()
        
        print("🏪 PRODUCTOS POR TIENDA:")
        for store, count in stats['store_stats']:
            print(f"   {store}: {count}")
        
        input("\nPresiona Enter para continuar...")
    
    def show_telegram_config(self):
        """Muestra configuración de Telegram"""
        self.clear_screen()
        print("🔧 CONFIGURACIÓN TELEGRAM")
        print("=" * 30)
        
        if self.telegram_config['enabled']:
            print("✅ Telegram: HABILITADO")
            if self.telegram_config['bot_token']:
                print("✅ Bot Token: Configurado")
            else:
                print("❌ Bot Token: No configurado")
            
            if self.telegram_config['chat_id']:
                print("✅ Chat ID: Configurado")
            else:
                print("❌ Chat ID: No configurado")
            
            print(f"📱 Notificaciones enviadas: {self.telegram_config['notifications_sent']}")
        else:
            print("❌ Telegram: DESHABILITADO")
        
        print()
        print("Para configurar Telegram:")
        print("1. Habla con @BotFather en Telegram")
        print("2. Crea un bot con /newbot")
        print("3. Obtén el token del bot")
        print("4. Envía un mensaje al bot para obtener el chat_id")
        print("5. Configura las variables de entorno:")
        print("   TELEGRAM_BOT_TOKEN=tu_token_aqui")
        print("   TELEGRAM_CHAT_ID=tu_chat_id_aqui")
        
        print()
        print("OPCIONES:")
        print("1. Habilitar/Deshabilitar Telegram")
        print("2. Probar conexión")
        print("3. Volver")
        
        try:
            option = input("\nSelecciona una opción (1-3): ").strip()
            
            if option == "1":
                self.telegram_config['enabled'] = not self.telegram_config['enabled']
                status = "habilitado" if self.telegram_config['enabled'] else "deshabilitado"
                print(f"✅ Telegram {status}")
                input("Presiona Enter para continuar...")
            elif option == "2":
                self.test_telegram_connection()
            elif option == "3":
                pass
            else:
                print("❌ Opción inválida")
                input("Presiona Enter para continuar...")
                
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"❌ Error: {e}")
            input("Presiona Enter para continuar...")
    
    def test_telegram_connection(self):
        """Prueba la conexión con Telegram"""
        if not self.telegram_config['enabled']:
            print("❌ Telegram no está habilitado")
            input("Presiona Enter para continuar...")
            return
        
        if not self.telegram_config['bot_token'] or not self.telegram_config['chat_id']:
            print("❌ Bot Token o Chat ID no configurados")
            input("Presiona Enter para continuar...")
            return
        
        try:
            message = f"""
🧪 PRUEBA DE CONEXIÓN TELEGRAM

✅ DescuentosGO está funcionando correctamente
⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}

🎯 Las notificaciones están activas para ofertas con {TELEGRAM_ALERT_THRESHOLD}%+ de descuento.
            """.strip()
            
            url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
            data = {
                'chat_id': self.telegram_config['chat_id'],
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print("✅ Conexión con Telegram exitosa")
            else:
                print(f"❌ Error en la conexión: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error probando conexión: {e}")
        
        input("Presiona Enter para continuar...")
    
    def clear_screen(self):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Función principal"""
    try:
        print("🎯 DESCUENTOSGO - Scanner Automático")
        print("=" * 50)
        print("🚀 Iniciando aplicación...")
        
        app = DescuentosGO()
        
        # Iniciar scanner automáticamente
        print("🔄 Iniciando scanner automático...")
        app.start_scanner()
        
        # Mostrar menú
        app.show_menu()
        
    except Exception as e:
        print(f"❌ Error iniciando la aplicación: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main() 