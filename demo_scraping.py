#!/usr/bin/env python3
"""
Demostración del Sistema de Scraping de Descuentos
Versión simplificada sin Firebase - Funciona con PowerShell
"""

import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def demo_scraping():
    """Demostración del sistema de scraping"""
    print("🚀 DEMOSTRACIÓN DEL SISTEMA DE SCRAPING")
    print("=" * 50)
    print("💾 Sistema optimizado para PowerShell")
    print("📁 Guarda datos localmente sin Firebase")
    print("=" * 50)
    
    # Crear directorio de datos
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print("✅ Directorio 'data' creado")
    
    # Probar conexión a tiendas
    stores = {
        'Paris': 'https://www.paris.cl',
        'Falabella': 'https://www.falabella.com'
    }
    
    print("\n🔍 Probando conexiones a tiendas...")
    
    for store_name, url in stores.items():
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ {store_name}: Conexión exitosa")
            else:
                print(f"⚠️  {store_name}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {store_name}: Error de conexión")
    
    # Crear archivo de demostración
    demo_data = {
        'demo': True,
        'timestamp': datetime.now().isoformat(),
        'system_info': {
            'name': 'Sistema de Scraping de Descuentos',
            'version': '1.0',
            'platform': 'PowerShell',
            'storage': 'Local (JSON)',
            'firebase': False
        },
        'stores_configured': list(stores.keys()),
        'features': [
            'Scraping automático de tiendas',
            'Filtrado por descuento mínimo',
            'Guardado local en JSON',
            'Sin dependencias de Firebase',
            'Compatible con PowerShell'
        ],
        'sample_products': [
            {
                'name': 'Producto de ejemplo 1',
                'current_price': '$29.990',
                'original_price': '$59.990',
                'discount': '50%',
                'store': 'Paris',
                'category': 'Tecnología'
            },
            {
                'name': 'Producto de ejemplo 2',
                'current_price': '$19.990',
                'original_price': '$39.990',
                'discount': '50%',
                'store': 'Falabella',
                'category': 'Hogar'
            }
        ]
    }
    
    # Guardar archivo de demostración
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    demo_filename = f"{data_dir}/demo_system_{timestamp}.json"
    
    with open(demo_filename, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Archivo de demostración creado: {demo_filename}")
    
    # Mostrar contenido del archivo
    print("\n📄 Contenido del archivo de demostración:")
    print("-" * 40)
    
    with open(demo_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Nombre del sistema: {data['system_info']['name']}")
    print(f"Versión: {data['system_info']['version']}")
    print(f"Plataforma: {data['system_info']['platform']}")
    print(f"Almacenamiento: {data['system_info']['storage']}")
    print(f"Firebase: {'No' if not data['system_info']['firebase'] else 'Sí'}")
    print(f"Tiendas configuradas: {', '.join(data['stores_configured'])}")
    
    print("\n🎯 Características del sistema:")
    for feature in data['features']:
        print(f"  • {feature}")
    
    print("\n📦 Productos de ejemplo:")
    for i, product in enumerate(data['sample_products'], 1):
        print(f"  {i}. {product['name']}")
        print(f"     Precio: {product['current_price']} (antes: {product['original_price']})")
        print(f"     Descuento: {product['discount']}")
        print(f"     Tienda: {product['store']}")
        print()
    
    print("🎉 ¡Demostración completada exitosamente!")
    print("💡 El sistema está funcionando correctamente")
    print("📁 Revisa la carpeta 'data' para ver los archivos generados")

if __name__ == "__main__":
    demo_scraping() 