#!/usr/bin/env python3
"""
Script de prueba rápida para verificar el funcionamiento de los scrapers
"""

import sys
import time
import argparse
from utils.monitor import ScrapingMonitor
from scrapers.paris_scraper import ParisScraper
from scrapers.falabella_scraper import FalabellaScraper
from scrapers.ripley_scraper import RipleyScraper
from scrapers.lapolar_scraper import LaPolarScraper
from scrapers.hites_scraper import HitesScraper
from scrapers.sodimac_scraper import SodimacScraper

def test_scraper(scraper_class, store_name, monitor):
    """Prueba un scraper específico"""
    print(f"\n🔍 Probando {store_name}...")
    
    try:
        scraper = scraper_class()
        
        # Obtener la primera categoría para prueba
        categories = scraper.store_config['categories']
        if not categories:
            print(f"❌ No hay categorías configuradas para {store_name}")
            return False
        
        test_category = categories[0]
        category_url = scraper.store_config['base_url'] + test_category
        
        print(f"   📂 Categoría de prueba: {test_category}")
        print(f"   🔗 URL: {category_url}")
        
        # Realizar scraping
        start_time = time.time()
        products = scraper.scrape_category(category_url)
        end_time = time.time()
        
        # Filtrar productos con alto descuento
        high_discount_products = [
            p for p in products 
            if p.get('discount_percentage', 0) >= 70
        ]
        
        # Registrar estadísticas
        monitor.log_store_scraping(
            store_name=store_name,
            category=test_category,
            products_found=len(products),
            high_discount_count=len(high_discount_products),
            errors=scraper.errors
        )
        
        # Mostrar resultados
        print(f"   ✅ Productos encontrados: {len(products)}")
        print(f"   🎯 Con alto descuento (≥70%): {len(high_discount_products)}")
        print(f"   ⏱️  Tiempo: {end_time - start_time:.2f}s")
        
        if scraper.errors:
            print(f"   ⚠️  Errores: {len(scraper.errors)}")
            for error in scraper.errors[:3]:  # Mostrar solo los primeros 3
                print(f"      • {error}")
        
        # Mostrar ejemplo de producto
        if products:
            sample_product = products[0]
            print(f"   📦 Ejemplo: {sample_product['name'][:50]}...")
            print(f"      💰 ${sample_product.get('current_price', 'N/A')} "
                  f"({sample_product.get('discount_percentage', 0)}% descuento)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando {store_name}: {str(e)}")
        monitor.log_store_scraping(
            store_name=store_name,
            category="ERROR",
            products_found=0,
            high_discount_count=0,
            errors=[str(e)]
        )
        return False

def main():
    parser = argparse.ArgumentParser(description='Prueba rápida de scrapers')
    parser.add_argument('--store', choices=['paris', 'falabella', 'ripley', 'lapolar', 'hites', 'sodimac', 'all'],
                       default='all', help='Tienda específica a probar')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verbose')
    parser.add_argument('--save-report', action='store_true', help='Guardar reporte en archivo')
    
    args = parser.parse_args()
    
    # Configurar logging
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    # Inicializar monitor
    monitor = ScrapingMonitor()
    monitor.start_session()
    
    # Definir scrapers
    scrapers = {
        'paris': ParisScraper,
        'falabella': FalabellaScraper,
        'ripley': RipleyScraper,
        'lapolar': LaPolarScraper,
        'hites': HitesScraper,
        'sodimac': SodimacScraper
    }
    
    print("🧪 PRUEBA RÁPIDA DE SCRAPERS")
    print("=" * 50)
    
    if args.store == 'all':
        # Probar todos los scrapers
        results = {}
        for store_name, scraper_class in scrapers.items():
            results[store_name] = test_scraper(scraper_class, store_name, monitor)
            time.sleep(2)  # Pausa entre tiendas
    else:
        # Probar tienda específica
        if args.store in scrapers:
            test_scraper(scrapers[args.store], args.store, monitor)
        else:
            print(f"❌ Tienda '{args.store}' no encontrada")
            return 1
    
    # Finalizar y mostrar reporte
    monitor.end_session()
    monitor.print_summary()
    
    # Guardar reporte si se solicita
    if args.save_report:
        report_file = monitor.save_report()
        if report_file:
            print(f"\n📄 Reporte guardado en: {report_file}")
    
    # Mostrar alertas de rendimiento
    alerts = monitor.get_performance_alerts()
    if alerts:
        print("\n⚠️  ALERTAS DE RENDIMIENTO:")
        for alert in alerts:
            print(f"   {alert}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 