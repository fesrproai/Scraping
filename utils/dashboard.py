#!/usr/bin/env python3
"""
Dashboard en consola para el sistema de scraping de descuentos
Muestra estadísticas, rankings y gráficos simples
"""

import os
from typing import List, Dict
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Para usar sin interfaz gráfica

class Dashboard:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def show_main_dashboard(self):
        """Muestra el dashboard principal"""
        print("\n" + "=" * 80)
        print("📊 DASHBOARD - SISTEMA DE SCRAPING DE DESCUENTOS")
        print("=" * 80)
        
        # Obtener estadísticas
        stats = self.data_manager.get_statistics()
        
        if not stats:
            print("❌ No hay datos disponibles")
            return
        
        # Mostrar estadísticas generales
        self.show_general_stats(stats)
        
        # Mostrar ranking de descuentos
        self.show_discount_ranking(stats)
        
        # Mostrar productos por tienda
        self.show_store_stats(stats)
        
        # Mostrar ofertas extremas
        self.show_extreme_offers()
        
        print("\n" + "=" * 80)
    
    def show_general_stats(self, stats: Dict):
        """Muestra estadísticas generales"""
        print(f"\n📈 ESTADÍSTICAS GENERALES:")
        print("-" * 40)
        print(f"   🛍️  Total productos: {stats.get('total_products', 0)}")
        print(f"   📊 Promedio descuento: {stats.get('average_discount', 0)}%")
        print(f"   🏪 Tiendas activas: {len(stats.get('products_by_store', {}))}")
        print(f"   📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def show_discount_ranking(self, stats: Dict):
        """Muestra ranking de descuentos"""
        print(f"\n🏆 TOP 5 - MAYORES DESCUENTOS:")
        print("-" * 40)
        
        top_discounts = stats.get('top_discounts', [])
        if not top_discounts:
            print("   No hay productos con descuentos registrados")
            return
        
        for i, (name, discount, store) in enumerate(top_discounts, 1):
            name_short = name[:50] + "..." if len(name) > 50 else name
            print(f"   {i}. {name_short}")
            print(f"      💰 {discount} | 🏪 {store}")
            print()
    
    def show_store_stats(self, stats: Dict):
        """Muestra estadísticas por tienda"""
        print(f"\n🏪 PRODUCTOS POR TIENDA:")
        print("-" * 40)
        
        products_by_store = stats.get('products_by_store', {})
        if not products_by_store:
            print("   No hay datos por tienda")
            return
        
        for store, count in products_by_store.items():
            print(f"   {store}: {count} productos")
    
    def show_extreme_offers(self, min_discount: int = 85):
        """Muestra ofertas extremas (85% o más de descuento)"""
        print(f"\n🔥 OFERTAS EXTREMAS ({min_discount}% o más):")
        print("-" * 40)
        
        extreme_offers = self.data_manager.get_products_by_discount_range(min_discount, 100)
        
        if not extreme_offers:
            print(f"   No hay ofertas con {min_discount}% o más de descuento")
            return
        
        for i, product in enumerate(extreme_offers[:10], 1):
            name = product.get('name', '')[:40] + "..." if len(product.get('name', '')) > 40 else product.get('name', '')
            discount = product.get('discount', '')
            store = product.get('store', '')
            current_price = product.get('current_price', '')
            
            print(f"   {i}. {name}")
            print(f"      💰 {current_price} | 🔥 {discount} | 🏪 {store}")
            print()
    
    def show_search_results(self, query: str, results: List[Dict]):
        """Muestra resultados de búsqueda"""
        print(f"\n🔍 RESULTADOS DE BÚSQUEDA: '{query}'")
        print("-" * 50)
        
        if not results:
            print("   No se encontraron productos que coincidan con la búsqueda")
            return
        
        print(f"   Encontrados {len(results)} productos:")
        print()
        
        for i, product in enumerate(results[:20], 1):  # Limitar a 20 resultados
            name = product.get('name', '')[:50] + "..." if len(product.get('name', '')) > 50 else product.get('name', '')
            current_price = product.get('current_price', '')
            original_price = product.get('original_price', '')
            discount = product.get('discount', '')
            store = product.get('store', '')
            
            print(f"   {i}. {name}")
            print(f"      💰 {current_price} (antes: {original_price}) | 🔥 {discount} | 🏪 {store}")
            print()
    
    def show_comparison_results(self, product_name: str, comparisons: List[Dict]):
        """Muestra resultados de comparación entre tiendas"""
        print(f"\n⚖️  COMPARACIÓN: '{product_name}'")
        print("-" * 50)
        
        if not comparisons:
            print("   No se encontraron productos similares en otras tiendas")
            return
        
        print(f"   Productos similares encontrados:")
        print()
        
        # Ordenar por precio (más barato primero)
        sorted_comparisons = sorted(comparisons, key=lambda x: self.extract_price_value(x.get('current_price', '')))
        
        for i, product in enumerate(sorted_comparisons, 1):
            name = product.get('name', '')[:50] + "..." if len(product.get('name', '')) > 50 else product.get('name', '')
            current_price = product.get('current_price', '')
            original_price = product.get('original_price', '')
            discount = product.get('discount', '')
            store = product.get('store', '')
            
            print(f"   {i}. {name}")
            print(f"      💰 {current_price} (antes: {original_price}) | 🔥 {discount} | 🏪 {store}")
            print()
    
    def extract_price_value(self, price_str: str) -> float:
        """Extrae el valor numérico del precio para ordenamiento"""
        try:
            if not price_str:
                return float('inf')
            
            # Remover símbolos y convertir a número
            price_clean = price_str.replace('$', '').replace('.', '').replace(',', '')
            return float(price_clean)
        except:
            return float('inf')
    
    def generate_discount_chart(self, save_path: str = "data/discount_chart.png"):
        """Genera un gráfico simple de descuentos"""
        try:
            # Obtener productos con descuentos
            products = self.data_manager.get_products_by_discount_range(0, 100)
            
            if not products:
                print("❌ No hay datos para generar el gráfico")
                return False
            
            # Preparar datos para el gráfico
            discounts = []
            for product in products:
                discount_str = product.get('discount', '')
                if discount_str:
                    try:
                        discount_value = int(discount_str.replace('%', '').replace('-', ''))
                        discounts.append(discount_value)
                    except:
                        continue
            
            if not discounts:
                print("❌ No hay descuentos válidos para el gráfico")
                return False
            
            # Crear el gráfico
            plt.figure(figsize=(10, 6))
            plt.hist(discounts, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            plt.title('Distribución de Descuentos', fontsize=14, fontweight='bold')
            plt.xlabel('Porcentaje de Descuento (%)', fontsize=12)
            plt.ylabel('Número de Productos', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Agregar estadísticas al gráfico
            avg_discount = sum(discounts) / len(discounts)
            plt.axvline(avg_discount, color='red', linestyle='--', 
                       label=f'Promedio: {avg_discount:.1f}%')
            plt.legend()
            
            # Guardar el gráfico
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Gráfico guardado en: {save_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error generando gráfico: {e}")
            return False
    
    def show_quick_stats(self):
        """Muestra estadísticas rápidas"""
        stats = self.data_manager.get_statistics()
        
        if not stats:
            return
        
        total_products = stats.get('total_products', 0)
        avg_discount = stats.get('average_discount', 0)
        stores_count = len(stats.get('products_by_store', {}))
        
        print(f"📊 {total_products} productos | 📈 {avg_discount}% promedio | 🏪 {stores_count} tiendas") 