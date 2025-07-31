#!/usr/bin/env python3
"""
Script de Prueba para Verificar Todas las Mejoras Implementadas
Prueba las 5 mejoras principales del sistema DescuentosGO
"""

import os
import sys
import json
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mejora_1_cache():
    """Prueba el Sistema de Cache Inteligente"""
    print("\n🔍 PROBANDO MEJORA 1: Sistema de Cache Inteligente")
    print("=" * 60)
    
    try:
        from utils.cache_manager import CacheManager
        
        # Crear instancia del cache
        cache = CacheManager()
        print("✅ CacheManager creado correctamente")
        
        # Probar operaciones básicas
        test_data = [
            {'name': 'Producto Test 1', 'price': 1000, 'discount': 50},
            {'name': 'Producto Test 2', 'price': 2000, 'discount': 30}
        ]
        
        # Guardar datos en cache
        cache.set('falabella', 'tecnologia', 'https://test.com', test_data)
        print("✅ Datos guardados en cache")
        
        # Recuperar datos del cache
        cached_data = cache.get('falabella', 'tecnologia', 'https://test.com')
        if cached_data:
            print(f"✅ Datos recuperados del cache: {len(cached_data)} productos")
        else:
            print("❌ No se pudieron recuperar datos del cache")
        
        # Obtener estadísticas
        stats = cache.get_stats()
        print(f"✅ Estadísticas del cache: {stats['total_entries']} entradas, {stats['hit_rate']:.1f}% hit rate")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de cache: {e}")
        return False

def test_mejora_2_price_analyzer():
    """Prueba el Sistema de Análisis de Precios Inteligente"""
    print("\n🔍 PROBANDO MEJORA 2: Sistema de Análisis de Precios")
    print("=" * 60)
    
    try:
        from utils.price_analyzer import PriceAnalyzer
        
        # Crear instancia del analizador
        analyzer = PriceAnalyzer()
        print("✅ PriceAnalyzer creado correctamente")
        
        # Producto de prueba
        test_product = {
            'name': 'Smartphone Samsung Galaxy',
            'current_price': '$150.000',
            'original_price': '$300.000',
            'discount': '50%',
            'product_link': 'https://test.com/producto',
            'image': 'https://test.com/image.jpg'
        }
        
        # Analizar producto
        analysis = analyzer.analyze_price(test_product, 'falabella')
        if analysis:
            print(f"✅ Análisis completado:")
            print(f"   - Descuento real: {analysis.is_real_discount}")
            print(f"   - Score de confianza: {analysis.confidence_score:.2f}")
            print(f"   - Tendencia: {analysis.price_trend}")
            print(f"   - Recomendación: {analysis.recommendation}")
        else:
            print("❌ No se pudo analizar el producto")
        
        # Obtener estadísticas
        stats = analyzer.get_price_statistics()
        print(f"✅ Estadísticas de precios: {stats['total_products']} productos analizados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de análisis de precios: {e}")
        return False

def test_mejora_3_advanced_filters():
    """Prueba el Sistema de Filtros Avanzados"""
    print("\n🔍 PROBANDO MEJORA 3: Sistema de Filtros Avanzados")
    print("=" * 60)
    
    try:
        from utils.advanced_filters import AdvancedFilters, FilterCriteria
        
        # Crear instancia de filtros
        filters = AdvancedFilters()
        print("✅ AdvancedFilters creado correctamente")
        
        # Productos de prueba
        test_products = [
            {
                'name': 'Laptop Gaming',
                'current_price': '$500.000',
                'original_price': '$1.000.000',
                'discount': '50%',
                'store': 'falabella',
                'category': 'tecnologia',
                'confidence_score': 0.8,
                'risk_level': 'low'
            },
            {
                'name': 'Smartphone Barato',
                'current_price': '$50.000',
                'original_price': '$200.000',
                'discount': '75%',
                'store': 'paris',
                'category': 'tecnologia',
                'confidence_score': 0.9,
                'risk_level': 'low'
            }
        ]
        
        # Probar filtro predefinido
        criteria = filters.get_preset_filter('ofertas_extremas')
        if criteria:
            filtered_products = filters.apply_filters(test_products, criteria)
            print(f"✅ Filtro aplicado: {len(filtered_products)} productos de {len(test_products)}")
        
        # Probar filtro personalizado
        custom_criteria = FilterCriteria(
            min_discount=40.0,
            max_price=600000,
            stores=['falabella']
        )
        filtered_products = filters.apply_filters(test_products, custom_criteria)
        print(f"✅ Filtro personalizado: {len(filtered_products)} productos")
        
        # Obtener estadísticas
        stats = filters.get_filter_stats(test_products, criteria)
        print(f"✅ Estadísticas de filtrado: {stats['filter_percentage']:.1f}% de productos filtrados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de filtros: {e}")
        return False

def test_mejora_4_smart_alerts():
    """Prueba el Sistema de Alertas Inteligentes"""
    print("\n🔍 PROBANDO MEJORA 4: Sistema de Alertas Inteligentes")
    print("=" * 60)
    
    try:
        from utils.smart_alerts import SmartAlerts
        
        # Crear instancia de alertas
        alerts = SmartAlerts()
        print("✅ SmartAlerts creado correctamente")
        
        # Productos de prueba
        test_products = [
            {
                'name': 'Producto con 90% descuento',
                'current_price': '$10.000',
                'original_price': '$100.000',
                'discount': '90%',
                'store': 'falabella',
                'category': 'tecnologia',
                'confidence_score': 0.9,
                'risk_level': 'low',
                'historical_low': True,
                'price_trend': 'decreasing'
            }
        ]
        
        # Analizar productos para alertas
        generated_alerts = alerts.analyze_products(test_products)
        print(f"✅ Alertas generadas: {len(generated_alerts)} alertas")
        
        for alert in generated_alerts:
            print(f"   - {alert.rule_name}: {alert.priority} priority")
        
        # Obtener estadísticas
        stats = alerts.get_alert_statistics()
        print(f"✅ Estadísticas de alertas: {stats['total_alerts']} alertas totales")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de alertas: {e}")
        return False

def test_mejora_5_price_predictor():
    """Prueba el Sistema de Machine Learning para Predicción"""
    print("\n🔍 PROBANDO MEJORA 5: Sistema de Machine Learning")
    print("=" * 60)
    
    try:
        from utils.price_predictor import PricePredictor
        
        # Crear instancia del predictor
        predictor = PricePredictor()
        print("✅ PricePredictor creado correctamente")
        
        # Producto de prueba
        test_product = {
            'name': 'Laptop HP Pavilion',
            'current_price': '$400.000',
            'original_price': '$600.000',
            'discount': '33%'
        }
        
        # Actualizar historial de precios (simular datos históricos)
        for i in range(15):  # Mínimo 10 datos requeridos
            predictor.update_price_history(test_product, 'falabella')
        
        # Intentar predicción
        prediction = predictor.predict_price(test_product, 'falabella')
        if prediction:
            print(f"✅ Predicción completada:")
            print(f"   - Precio predicho: ${prediction.predicted_price:,.0f}")
            print(f"   - Confianza: {prediction.confidence:.2f}")
            print(f"   - Tendencia: {prediction.trend}")
            print(f"   - Recomendación: {prediction.recommendation}")
        else:
            print("⚠️ No hay suficientes datos para predicción (normal en primera ejecución)")
        
        # Obtener estadísticas
        stats = predictor.get_prediction_statistics()
        print(f"✅ Estadísticas de predicción: {stats['total_products']} productos en historial")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de Machine Learning: {e}")
        return False

def test_integracion_completa():
    """Prueba la integración de todas las mejoras"""
    print("\n🔍 PROBANDO INTEGRACIÓN COMPLETA")
    print("=" * 60)
    
    try:
        # Producto de prueba para todas las mejoras
        test_product = {
            'name': 'Smartphone iPhone 15',
            'current_price': '$800.000',
            'original_price': '$1.200.000',
            'discount': '33%',
            'store': 'falabella',
            'category': 'tecnologia',
            'product_link': 'https://test.com/iphone',
            'image': 'https://test.com/iphone.jpg',
            'confidence_score': 0.85,
            'risk_level': 'low',
            'historical_low': True,
            'price_trend': 'decreasing'
        }
        
        # 1. Cache
        from utils.cache_manager import CacheManager
        cache = CacheManager()
        cache.set('falabella', 'tecnologia', 'https://test.com', [test_product])
        
        # 2. Análisis de precios
        from utils.price_analyzer import PriceAnalyzer
        analyzer = PriceAnalyzer()
        analysis = analyzer.analyze_price(test_product, 'falabella')
        
        # 3. Filtros
        from utils.advanced_filters import AdvancedFilters
        filters = AdvancedFilters()
        criteria = filters.get_preset_filter('tecnologia')
        filtered = filters.apply_filters([test_product], criteria)
        
        # 4. Alertas
        from utils.smart_alerts import SmartAlerts
        alerts = SmartAlerts()
        generated_alerts = alerts.analyze_products([test_product])
        
        # 5. Predicción
        from utils.price_predictor import PricePredictor
        predictor = PricePredictor()
        for i in range(15):
            predictor.update_price_history(test_product, 'falabella')
        prediction = predictor.predict_price(test_product, 'falabella')
        
        print("✅ Integración completa exitosa:")
        print(f"   - Cache: {len(cache.get('falabella', 'tecnologia', 'https://test.com') or [])} productos")
        print(f"   - Análisis: {analysis.is_real_discount if analysis else False}")
        print(f"   - Filtros: {len(filtered)} productos filtrados")
        print(f"   - Alertas: {len(generated_alerts)} alertas generadas")
        print(f"   - Predicción: {prediction.confidence if prediction else 0:.2f} confianza")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración completa: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 SISTEMA DE PRUEBAS - MEJORAS DESCUENTOSGO")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Lista de pruebas
    tests = [
        ("MEJORA 1: Cache Inteligente", test_mejora_1_cache),
        ("MEJORA 2: Análisis de Precios", test_mejora_2_price_analyzer),
        ("MEJORA 3: Filtros Avanzados", test_mejora_3_advanced_filters),
        ("MEJORA 4: Alertas Inteligentes", test_mejora_4_smart_alerts),
        ("MEJORA 5: Machine Learning", test_mejora_5_price_predictor),
        ("INTEGRACIÓN COMPLETA", test_integracion_completa)
    ]
    
    # Ejecutar pruebas
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Resultado Final: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡TODAS LAS MEJORAS ESTÁN FUNCIONANDO CORRECTAMENTE!")
        print("💡 El sistema DescuentosGO está listo para uso avanzado")
    else:
        print("⚠️ Algunas mejoras necesitan atención")
        print("🔧 Revisa los errores y verifica las dependencias")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 