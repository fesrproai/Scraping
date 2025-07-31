#!/usr/bin/env python3
"""
Demo del Sistema de Scraping de Descuentos - Sin Firebase
"""

import time
import random
from datetime import datetime

class DemoScraper:
    def __init__(self, store_name):
        self.store_name = store_name
        self.errors = []
        
    def scrape_category(self, category_url):
        """Simula el scraping de una categoría"""
        print(f"   🔍 Scraping: {category_url}")
        
        # Simular tiempo de scraping
        time.sleep(random.uniform(1, 3))
        
        # Simular productos encontrados
        num_products = random.randint(50, 200)
        products = []
        
        for i in range(num_products):
            # Simular descuento aleatorio
            discount = random.randint(0, 90)
            
            product = {
                'name': f'Producto Demo {i+1} - {self.store_name.title()}',
                'original_price': random.randint(10000, 500000),
                'current_price': random.randint(5000, 200000),
                'discount_percentage': discount,
                'url': f'https://{self.store_name}.cl/producto/{i+1}',
                'image_url': f'https://via.placeholder.com/300x300?text={self.store_name}',
                'store': self.store_name,
                'category': 'demo'
            }
            
            # Calcular precio actual basado en descuento
            if discount > 0:
                product['current_price'] = int(product['original_price'] * (1 - discount/100))
            
            products.append(product)
        
        return products

def main():
    print("🚀 Sistema de Scraping de Descuentos - DEMO")
    print("=" * 60)
    
    # Configuración de tiendas demo
    stores_config = {
        'falabella': {
            'name': 'Falabella',
            'base_url': 'https://www.falabella.com',
            'categories': ['/ropa-y-zapatos', '/tecnologia', '/hogar-y-muebles']
        },
        'paris': {
            'name': 'Paris',
            'base_url': 'https://www.paris.cl',
            'categories': ['/ropa-y-accesorios', '/tecnologia', '/hogar-y-jardin']
        },
        'ripley': {
            'name': 'Ripley',
            'base_url': 'https://www.ripley.cl',
            'categories': ['/ropa-y-zapatos', '/tecnologia', '/hogar-y-muebles']
        }
    }
    
    min_discount = 70
    total_products_scraped = 0
    high_discount_products = 0
    
    print(f"💰 Descuento mínimo: {min_discount}%")
    print(f"🔧 Modo: DEMO (sin Firebase)")
    print("-" * 60)
    
    # Ejecutar scraping demo
    for store_name, config in stores_config.items():
        print(f"\n🏪 Scraping {config['name'].upper()}...")
        scraper = DemoScraper(store_name)
        
        for category in config['categories']:
            print(f"  📂 Categoría: {category}")
            
            # Construir URL de categoría
            category_url = config['base_url'] + category
            
            # Realizar scraping
            start_time = time.time()
            products = scraper.scrape_category(category_url)
            end_time = time.time()
            
            if products:
                # Filtrar por descuento mínimo
                filtered_products = [p for p in products if p.get('discount_percentage', 0) >= min_discount]
                
                # Contar productos
                total_products_scraped += len(products)
                high_discount_products += len(filtered_products)
                
                print(f"    ✅ {len(products)} productos encontrados")
                print(f"    🎯 {len(filtered_products)} con descuento ≥{min_discount}%")
                print(f"    ⏱️  Tiempo: {end_time - start_time:.2f}s")
                
                # Mostrar algunos productos de ejemplo
                if filtered_products:
                    print(f"    📦 Ejemplos de productos con alto descuento:")
                    for i, product in enumerate(filtered_products[:3]):
                        print(f"      {i+1}. {product['name'][:50]}...")
                        print(f"         💰 ${product.get('current_price', 'N/A'):,} "
                              f"({product.get('discount_percentage', 0)}% descuento)")
                        print(f"         🔗 {product['url']}")
            else:
                print(f"    ⚠️  No se encontraron productos en esta categoría")
            
            # Pausa entre categorías
            time.sleep(1)
    
    # Mostrar resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL - DEMO")
    print("=" * 60)
    print(f"🏪 Tiendas procesadas: {len(stores_config)}")
    print(f"📦 Total productos encontrados: {total_products_scraped}")
    print(f"🎯 Productos con descuento ≥{min_discount}%: {high_discount_products}")
    print(f"⏱️  Tiempo total: {time.time() - time.time():.2f}s")
    
    if high_discount_products > 0:
        print(f"🎉 ¡Se encontraron {high_discount_products} productos con excelentes descuentos!")
    
    print("\n🔧 FUNCIONALIDADES DISPONIBLES EN EL SISTEMA COMPLETO:")
    print("   ✅ Scraping real de tiendas chilenas")
    print("   ✅ Almacenamiento en Firebase Firestore")
    print("   ✅ Sistema de cache inteligente")
    print("   ✅ Análisis de precios y tendencias")
    print("   ✅ Filtros avanzados personalizables")
    print("   ✅ Alertas inteligentes por Telegram")
    print("   ✅ Predicción de precios con ML")
    print("   ✅ Dashboard web en React")
    print("   ✅ API REST completa")
    print("   ✅ Ejecutables para Windows")
    
    return 0

if __name__ == "__main__":
    main() 