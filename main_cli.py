#!/usr/bin/env python3
"""
Sistema de Scraping de Descuentos - Menú CLI Interactivo
Interfaz principal con todas las funcionalidades
"""

import os
import sys
from datetime import datetime
from typing import List, Dict

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager
from utils.dashboard import Dashboard
from utils.search_engine import SearchEngine
from scraping_avanzado import ScrapingAvanzado

class ScrapingCLI:
    def __init__(self):
        self.data_manager = DataManager()
        self.dashboard = Dashboard(self.data_manager)
        self.search_engine = SearchEngine(self.data_manager)
        self.scraper = ScrapingAvanzado()
        
        # Configurar scraper para usar el data manager
        self.scraper.data_manager = self.data_manager
    
    def show_main_menu(self):
        """Muestra el menú principal"""
        while True:
            self.clear_screen()
            print("🚀 SISTEMA DE SCRAPING DE DESCUENTOS")
            print("=" * 50)
            print("📊 Menú Principal")
            print("=" * 50)
            
            # Mostrar estadísticas rápidas
            self.dashboard.show_quick_stats()
            print()
            
            print("OPCIONES DISPONIBLES:")
            print("1. 📊 Ver Dashboard completo")
            print("2. 🔍 Buscar productos")
            print("3. ⚖️  Comparar entre tiendas")
            print("4. 🏆 Ver mejores ofertas")
            print("5. 🔥 Ver ofertas extremas")
            print("6. 🚀 Ejecutar scraping")
            print("7. 📈 Generar gráfico de descuentos")
            print("8. 🧹 Limpiar productos antiguos")
            print("9. 📁 Ver archivos generados")
            print("0. ❌ Salir")
            print()
            
            try:
                option = input("Selecciona una opción (0-9): ").strip()
                
                if option == "1":
                    self.show_dashboard()
                elif option == "2":
                    self.search_products()
                elif option == "3":
                    self.compare_stores()
                elif option == "4":
                    self.show_best_deals()
                elif option == "5":
                    self.show_extreme_offers()
                elif option == "6":
                    self.run_scraping()
                elif option == "7":
                    self.generate_chart()
                elif option == "8":
                    self.clean_old_products()
                elif option == "9":
                    self.show_generated_files()
                elif option == "0":
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
    
    def show_dashboard(self):
        """Muestra el dashboard completo"""
        self.clear_screen()
        self.dashboard.show_main_dashboard()
        input("\nPresiona Enter para volver al menú principal...")
    
    def search_products(self):
        """Búsqueda de productos"""
        self.clear_screen()
        print("🔍 BÚSQUEDA DE PRODUCTOS")
        print("=" * 40)
        
        query = input("Ingresa palabras clave: ").strip()
        if not query:
            print("❌ Debes ingresar palabras clave")
            input("Presiona Enter para continuar...")
            return
        
        # Opciones de filtro
        print("\nFiltros opcionales:")
        store = input("Tienda específica (Enter para todas): ").strip() or None
        
        try:
            min_discount = int(input("Descuento mínimo % (Enter para 0): ").strip() or "0")
        except ValueError:
            min_discount = 0
        
        # Realizar búsqueda
        print(f"\n🔍 Buscando '{query}'...")
        results = self.search_engine.search_products(
            query=query,
            store=store,
            min_discount=min_discount,
            max_results=50
        )
        
        # Mostrar resultados
        self.dashboard.show_search_results(query, results)
        
        input("\nPresiona Enter para volver al menú principal...")
    
    def compare_stores(self):
        """Comparación entre tiendas"""
        self.clear_screen()
        print("⚖️  COMPARACIÓN ENTRE TIENDAS")
        print("=" * 40)
        
        product_name = input("Ingresa el nombre del producto a comparar: ").strip()
        if not product_name:
            print("❌ Debes ingresar un nombre de producto")
            input("Presiona Enter para continuar...")
            return
        
        # Buscar productos similares
        print(f"\n🔍 Buscando productos similares a '{product_name}'...")
        similar_products = self.search_engine.find_similar_products(product_name)
        
        # Mostrar resultados
        self.dashboard.show_comparison_results(product_name, similar_products)
        
        input("\nPresiona Enter para volver al menú principal...")
    
    def show_best_deals(self):
        """Muestra las mejores ofertas"""
        self.clear_screen()
        print("🏆 MEJORES OFERTAS")
        print("=" * 40)
        
        try:
            min_discount = int(input("Descuento mínimo % (Enter para 20): ").strip() or "20")
        except ValueError:
            min_discount = 20
        
        # Obtener mejores ofertas
        best_deals = self.search_engine.get_best_deals(limit=20, min_discount=min_discount)
        
        if not best_deals:
            print(f"❌ No hay ofertas con {min_discount}% o más de descuento")
        else:
            print(f"\n🏆 TOP {len(best_deals)} - MEJORES OFERTAS ({min_discount}% o más):")
            print("-" * 50)
            
            for i, product in enumerate(best_deals, 1):
                name = product.get('name', '')[:50] + "..." if len(product.get('name', '')) > 50 else product.get('name', '')
                current_price = product.get('current_price', '')
                original_price = product.get('original_price', '')
                discount = product.get('discount', '')
                store = product.get('store', '')
                
                print(f"   {i}. {name}")
                print(f"      💰 {current_price} (antes: {original_price}) | 🔥 {discount} | 🏪 {store}")
                print()
        
        input("Presiona Enter para volver al menú principal...")
    
    def show_extreme_offers(self):
        """Muestra ofertas extremas"""
        self.clear_screen()
        print("🔥 OFERTAS EXTREMAS")
        print("=" * 40)
        
        try:
            min_discount = int(input("Descuento mínimo % (Enter para 85): ").strip() or "85")
        except ValueError:
            min_discount = 85
        
        # Mostrar ofertas extremas
        self.dashboard.show_extreme_offers(min_discount)
        
        input("Presiona Enter para volver al menú principal...")
    
    def run_scraping(self):
        """Ejecuta el scraping"""
        self.clear_screen()
        print("🚀 EJECUTANDO SCRAPING")
        print("=" * 40)
        
        print("¿Qué tiendas quieres scrapear?")
        print("1. Todas las tiendas")
        print("2. Solo Paris")
        print("3. Solo Falabella")
        print("4. Cancelar")
        
        try:
            option = input("Selecciona una opción (1-4): ").strip()
            
            if option == "1":
                stores_to_scrape = None  # Todas las tiendas
            elif option == "2":
                stores_to_scrape = ['paris']
            elif option == "3":
                stores_to_scrape = ['falabella']
            elif option == "4":
                return
            else:
                print("❌ Opción inválida")
                input("Presiona Enter para continuar...")
                return
            
            print(f"\n🚀 Iniciando scraping...")
            self.scraper.run_scraping(stores_to_scrape)
            
        except Exception as e:
            print(f"❌ Error ejecutando scraping: {e}")
        
        input("\nPresiona Enter para volver al menú principal...")
    
    def generate_chart(self):
        """Genera gráfico de descuentos"""
        self.clear_screen()
        print("📈 GENERANDO GRÁFICO DE DESCUENTOS")
        print("=" * 40)
        
        print("Generando gráfico...")
        success = self.dashboard.generate_discount_chart()
        
        if success:
            print("✅ Gráfico generado exitosamente")
        else:
            print("❌ Error generando gráfico")
        
        input("Presiona Enter para volver al menú principal...")
    
    def clean_old_products(self):
        """Limpia productos antiguos"""
        self.clear_screen()
        print("🧹 LIMPIEZA DE PRODUCTOS ANTIGUOS")
        print("=" * 40)
        
        try:
            days_old = int(input("Productos más antiguos que X días (Enter para 30): ").strip() or "30")
        except ValueError:
            days_old = 30
        
        print(f"\n🧹 Limpiando productos más antiguos que {days_old} días...")
        self.data_manager.clean_old_products(days_old)
        
        input("Presiona Enter para volver al menú principal...")
    
    def show_generated_files(self):
        """Muestra archivos generados"""
        self.clear_screen()
        print("📁 ARCHIVOS GENERADOS")
        print("=" * 40)
        
        # Mostrar archivos JSON
        json_dir = os.path.join(self.data_manager.data_dir, "json")
        if os.path.exists(json_dir):
            json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
            if json_files:
                print(f"\n📄 Archivos JSON ({len(json_files)}):")
                for file in sorted(json_files, reverse=True)[:10]:  # Últimos 10
                    file_path = os.path.join(json_dir, file)
                    size = os.path.getsize(file_path)
                    size_kb = size / 1024
                    print(f"   • {file} ({size_kb:.1f} KB)")
            else:
                print("   No hay archivos JSON")
        
        # Mostrar archivos CSV
        csv_dir = os.path.join(self.data_manager.data_dir, "csv")
        if os.path.exists(csv_dir):
            csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
            if csv_files:
                print(f"\n📊 Archivos CSV ({len(csv_files)}):")
                for file in sorted(csv_files, reverse=True)[:10]:  # Últimos 10
                    file_path = os.path.join(csv_dir, file)
                    size = os.path.getsize(file_path)
                    size_kb = size / 1024
                    print(f"   • {file} ({size_kb:.1f} KB)")
            else:
                print("   No hay archivos CSV")
        
        # Mostrar base de datos
        if os.path.exists(self.data_manager.db_path):
            db_size = os.path.getsize(self.data_manager.db_path)
            db_size_kb = db_size / 1024
            print(f"\n🗄️  Base de datos: products.db ({db_size_kb:.1f} KB)")
        
        input("\nPresiona Enter para volver al menú principal...")
    
    def clear_screen(self):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Función principal"""
    try:
        cli = ScrapingCLI()
        cli.show_main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main() 