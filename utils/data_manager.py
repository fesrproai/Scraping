#!/usr/bin/env python3
"""
Gestor de datos para el sistema de scraping de descuentos
Maneja almacenamiento, validación y limpieza de datos
"""

import os
import json
import csv
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib

class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "products.db")
        
        # Crear directorios si no existen
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, "json"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "csv"), exist_ok=True)
        
        # Inicializar base de datos
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla de productos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_hash TEXT UNIQUE,
                    name TEXT NOT NULL,
                    current_price TEXT,
                    original_price TEXT,
                    discount TEXT,
                    store TEXT NOT NULL,
                    category TEXT,
                    product_link TEXT,
                    product_image TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Tabla de historial de precios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_hash TEXT,
                    price TEXT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_hash) REFERENCES products (product_hash)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Base de datos inicializada correctamente")
            
        except Exception as e:
            print(f"❌ Error inicializando base de datos: {e}")
    
    def generate_product_hash(self, product: Dict) -> str:
        """Genera un hash único para el producto"""
        # Usar nombre y tienda para generar hash
        hash_string = f"{product.get('name', '')}_{product.get('store', '')}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def validate_product(self, product: Dict) -> bool:
        """Valida que el producto tenga los datos mínimos requeridos"""
        required_fields = ['name', 'store']
        
        for field in required_fields:
            if not product.get(field):
                return False
        
        # Validar que el nombre tenga al menos 3 caracteres
        if len(product.get('name', '')) < 3:
            return False
        
        # Validar que el precio sea válido si existe
        if product.get('current_price'):
            price = product['current_price']
            if not price.startswith('$') or not any(char.isdigit() for char in price):
                return False
        
        return True
    
    def save_product_to_db(self, product: Dict) -> bool:
        """Guarda un producto en la base de datos"""
        try:
            if not self.validate_product(product):
                return False
            
            product_hash = self.generate_product_hash(product)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar si el producto ya existe
            cursor.execute('SELECT id FROM products WHERE product_hash = ?', (product_hash,))
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar producto existente
                cursor.execute('''
                    UPDATE products SET 
                        current_price = ?, original_price = ?, discount = ?,
                        product_link = ?, product_image = ?, scraped_at = CURRENT_TIMESTAMP
                    WHERE product_hash = ?
                ''', (
                    product.get('current_price'),
                    product.get('original_price'),
                    product.get('discount'),
                    product.get('product_link'),
                    product.get('product_image'),
                    product_hash
                ))
            else:
                # Insertar nuevo producto
                cursor.execute('''
                    INSERT INTO products (
                        product_hash, name, current_price, original_price, discount,
                        store, category, product_link, product_image
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product_hash,
                    product.get('name'),
                    product.get('current_price'),
                    product.get('original_price'),
                    product.get('discount'),
                    product.get('store'),
                    product.get('category'),
                    product.get('product_link'),
                    product.get('product_image')
                ))
            
            # Guardar en historial de precios
            if product.get('current_price'):
                cursor.execute('''
                    INSERT INTO price_history (product_hash, price)
                    VALUES (?, ?)
                ''', (product_hash, product.get('current_price')))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error guardando producto en DB: {e}")
            return False
    
    def save_products_to_json(self, products: List[Dict], store_name: str) -> Optional[str]:
        """Guarda productos en archivo JSON"""
        if not products:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.data_dir, "json", f"{store_name}_products_{timestamp}.json")
            
            data = {
                'store': store_name,
                'timestamp': datetime.now().isoformat(),
                'total_products': len(products),
                'method': 'avanzado',
                'products': products
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {len(products)} productos guardados en {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error guardando productos en JSON: {e}")
            return None
    
    def save_products_to_csv(self, products: List[Dict], store_name: str) -> Optional[str]:
        """Guarda productos en archivo CSV"""
        if not products:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.data_dir, "csv", f"{store_name}_products_{timestamp}.csv")
            
            # Definir campos del CSV
            fields = ['name', 'current_price', 'original_price', 'discount', 'store', 'category', 'product_link', 'scraped_at']
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                
                for product in products:
                    # Filtrar solo los campos que queremos en CSV
                    row = {field: product.get(field, '') for field in fields}
                    writer.writerow(row)
            
            print(f"✅ {len(products)} productos guardados en {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error guardando productos en CSV: {e}")
            return None
    
    def get_active_products(self, store: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Obtiene productos activos de la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if store:
                cursor.execute('''
                    SELECT * FROM products 
                    WHERE is_active = 1 AND store = ?
                    ORDER BY scraped_at DESC
                    LIMIT ?
                ''', (store, limit))
            else:
                cursor.execute('''
                    SELECT * FROM products 
                    WHERE is_active = 1
                    ORDER BY scraped_at DESC
                    LIMIT ?
                ''', (limit,))
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            products = []
            for row in rows:
                product = dict(zip(columns, row))
                products.append(product)
            
            conn.close()
            return products
            
        except Exception as e:
            print(f"❌ Error obteniendo productos: {e}")
            return []
    
    def get_products_by_discount_range(self, min_discount: int = 0, max_discount: int = 100) -> List[Dict]:
        """Obtiene productos por rango de descuento"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM products 
                WHERE is_active = 1 AND discount IS NOT NULL
                ORDER BY CAST(REPLACE(REPLACE(discount, '%', ''), '-', '') AS INTEGER) DESC
            ''')
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            products = []
            for row in rows:
                product = dict(zip(columns, row))
                
                # Extraer porcentaje de descuento
                discount_str = product.get('discount', '')
                if discount_str:
                    try:
                        discount_value = int(discount_str.replace('%', '').replace('-', ''))
                        if min_discount <= discount_value <= max_discount:
                            products.append(product)
                    except:
                        continue
            
            conn.close()
            return products
            
        except Exception as e:
            print(f"❌ Error obteniendo productos por descuento: {e}")
            return []
    
    def clean_old_products(self, days_old: int = 30):
        """Limpia productos antiguos de la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            cursor.execute('''
                UPDATE products 
                SET is_active = 0 
                WHERE scraped_at < ?
            ''', (cutoff_date,))
            
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"✅ {affected_rows} productos marcados como inactivos (más de {days_old} días)")
            
        except Exception as e:
            print(f"❌ Error limpiando productos antiguos: {e}")
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas de la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total de productos activos
            cursor.execute('SELECT COUNT(*) FROM products WHERE is_active = 1')
            total_products = cursor.fetchone()[0]
            
            # Productos por tienda
            cursor.execute('''
                SELECT store, COUNT(*) 
                FROM products 
                WHERE is_active = 1 
                GROUP BY store
            ''')
            products_by_store = dict(cursor.fetchall())
            
            # Promedio de descuento
            cursor.execute('''
                SELECT AVG(CAST(REPLACE(REPLACE(discount, '%', ''), '-', '') AS FLOAT))
                FROM products 
                WHERE is_active = 1 AND discount IS NOT NULL
            ''')
            avg_discount = cursor.fetchone()[0] or 0
            
            # Productos con mayor descuento
            cursor.execute('''
                SELECT name, discount, store 
                FROM products 
                WHERE is_active = 1 AND discount IS NOT NULL
                ORDER BY CAST(REPLACE(REPLACE(discount, '%', ''), '-', '') AS INTEGER) DESC
                LIMIT 5
            ''')
            top_discounts = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_products': total_products,
                'products_by_store': products_by_store,
                'average_discount': round(avg_discount, 2),
                'top_discounts': top_discounts
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {} 