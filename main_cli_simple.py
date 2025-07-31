#!/usr/bin/env python3
"""
Sistema de Scraping de Descuentos Chile - Menú CLI Simplificado
Versión optimizada con funciones esenciales y 12 tiendas chilenas
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager
from utils.dashboard import Dashboard
from utils.search_engine import SearchEngine
from scraping_chile_completo import ScrapingChileCompleto

class ScrapingCLISimple:
    def __init__(self):
        self.data_manager = DataManager()
        self.dashboard = Dashboard(self.data_manager)
        self.search_engine = SearchEngine(self.data_manager)
        self.scraper = ScrapingChileCompleto()
        
        # Configurar scraper para usar el data manager
        self.scraper.data_manager = self.data_manager
    
    def show_main_menu(self):
        """Muestra el menú principal simplificado"""
        while True:
            self.clear_screen()
            print("🚀 SISTEMA DE DESCUENTOS CHILE")
            print("=" * 40)
            
            # Mostrar estadísticas rápidas
            self.dashboard.show_quick_stats()
            print()
            
            print("OPCIONES PRINCIPALES:")
            print("1. 🔍 Buscar productos")
            print("2. 🏆 Ver mejores ofertas")
            print("3. 🚀 Ejecutar scraping (12 tiendas)")
            print("4. 📊 Ver estadísticas")
            print("5. 🏪 Ver tiendas disponibles")
            print("6. ❌ Salir")
            print()
            
            try:
                option = input("Selecciona una opción (1-6): ").strip()
                
                if option == "1":
                    self.search_products()
                elif option == "2":
                    self.show_best_deals()
                elif option == "3":
                    self.run_scraping()
                elif option == "4":
                    self.show_stats()
                elif option == "5":
                    self.show_stores()
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
    
    def search_products(self):
        """Búsqueda de productos simplificada"""
        self.clear_screen()
        print("🔍 BÚSQUEDA DE PRODUCTOS")
        print("=" * 30)
        
        query = input("Ingresa el producto a buscar: ").strip()
        if not query:
            print("❌ Debes ingresar un término de búsqueda")
            input("Presiona Enter para continuar...")
            return
        
        print(f"\n🔍 Buscando: {query}")
        results = self.search_engine.search_products(query)
        
        if results:
            print(f"\n✅ Encontrados {len(results)} productos:")
            for i, product in enumerate(results[:10], 1):  # Mostrar solo los primeros 10
                print(f"{i}. {product['name'][:50]}...")
                print(f"   💰 ${product['current_price']} | 🏪 {product['store']}")
                if product.get('discount_percentage'):
                    print(f"   🎯 {product['discount_percentage']}% de descuento")
                print()
        else:
            print("❌ No se encontraron productos")
        
        input("Presiona Enter para continuar...")
    
    def show_best_deals(self):
        """Muestra las mejores ofertas"""
        self.clear_screen()
        print("🏆 MEJORES OFERTAS")
        print("=" * 25)
        
        # Obtener productos con mayor descuento
        products = self.data_manager.get_all_products()
        if not products:
            print("❌ No hay productos disponibles")
            input("Presiona Enter para continuar...")
            return
        
        # Filtrar por descuento
        products_with_discount = [p for p in products if p.get('discount_percentage', 0) > 0]
        products_with_discount.sort(key=lambda x: x.get('discount_percentage', 0), reverse=True)
        
        if products_with_discount:
            print(f"🎯 Top {min(10, len(products_with_discount))} ofertas:")
            for i, product in enumerate(products_with_discount[:10], 1):
                print(f"{i}. {product['name'][:40]}...")
                print(f"   💰 ${product['current_price']} | 🏪 {product['store']}")
                print(f"   🎯 {product['discount_percentage']}% de descuento")
                print()
        else:
            print("❌ No hay ofertas disponibles")
        
        input("Presiona Enter para continuar...")
    
    def run_scraping(self):
        """Ejecuta el scraping de 12 tiendas"""
        self.clear_screen()
        print("🚀 EJECUTANDO SCRAPING DE 12 TIENDAS")
        print("=" * 40)
        
        print("📡 Iniciando búsqueda en tiendas chilenas...")
        print("⏳ Esto puede tomar varios minutos...")
        print("🏪 Tiendas: Falabella, Paris, Ripley, Sodimac, Easy, Líder,")
        print("           Jumbo, Santa Isabel, Alcampo, Unimarc, Walmart, Tottus")
        print()
        
        try:
            # Ejecutar scraping
            results = self.scraper.run_scraping()
            
            if results:
                total_products = sum(len(products) for products in results.values())
                print(f"\n✅ Scraping completado!")
                print(f"📦 Total de productos encontrados: {total_products}")
                print(f"🏪 Tiendas con productos: {len(results)}")
                
                for store, products in results.items():
                    if products:
                        print(f"🏪 {store}: {len(products)} productos")
            else:
                print("\n❌ No se encontraron productos")
                
        except Exception as e:
            print(f"\n❌ Error durante el scraping: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def show_stats(self):
        """Muestra estadísticas básicas"""
        self.clear_screen()
        print("📊 ESTADÍSTICAS")
        print("=" * 20)
        
        self.dashboard.show_main_dashboard()
        input("\nPresiona Enter para continuar...")
    
    def show_stores(self):
        """Muestra las tiendas disponibles"""
        self.clear_screen()
        print("🏪 TIENDAS DISPONIBLES")
        print("=" * 25)
        
        stores = self.scraper.stores
        print(f"📊 Total de tiendas: {len(stores)}")
        print()
        
        for i, (store_key, store_info) in enumerate(stores.items(), 1):
            print(f"{i}. 🏪 {store_info['name']}")
            print(f"   🌐 {store_info['base_url']}")
            print(f"   📂 Categorías: {len(store_info['categories'])}")
            for cat in store_info['categories']:
                print(f"      • {cat['name']}")
            print()
        
        input("Presiona Enter para continuar...")
    
    def clear_screen(self):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Función principal"""
    try:
        cli = ScrapingCLISimple()
        cli.show_main_menu()
    except Exception as e:
        print(f"❌ Error iniciando el sistema: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main() 