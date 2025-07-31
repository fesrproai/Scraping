#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del sistema optimizado
"""

import sys
import os
from datetime import datetime

def test_imports():
    """Prueba que todas las dependencias se importen correctamente"""
    print("🔍 Probando importaciones...")
    
    try:
        import requests
        print("✅ requests - OK")
    except ImportError as e:
        print(f"❌ requests - Error: {e}")
        return False
    
    try:
        import bs4
        print("✅ beautifulsoup4 - OK")
    except ImportError as e:
        print(f"❌ beautifulsoup4 - Error: {e}")
        return False
    
    try:
        import matplotlib
        print("✅ matplotlib - OK")
    except ImportError as e:
        print(f"❌ matplotlib - Error: {e}")
        return False
    
    try:
        import pandas
        print("✅ pandas - OK")
    except ImportError as e:
        print(f"❌ pandas - Error: {e}")
        return False
    
    try:
        import numpy
        print("✅ numpy - OK")
    except ImportError as e:
        print(f"❌ numpy - Error: {e}")
        return False
    
    try:
        import colorama
        print("✅ colorama - OK")
    except ImportError as e:
        print(f"❌ colorama - Error: {e}")
        return False
    
    try:
        import tqdm
        print("✅ tqdm - OK")
    except ImportError as e:
        print(f"❌ tqdm - Error: {e}")
        return False
    
    return True

def test_modules():
    """Prueba que los módulos del sistema se importen correctamente"""
    print("\n🔍 Probando módulos del sistema...")
    
    try:
        from scraping_avanzado import ScrapingAvanzado
        print("✅ scraping_avanzado - OK")
    except ImportError as e:
        print(f"❌ scraping_avanzado - Error: {e}")
        return False
    
    try:
        from utils.data_manager import DataManager
        print("✅ data_manager - OK")
    except ImportError as e:
        print(f"❌ data_manager - Error: {e}")
        return False
    
    try:
        from utils.dashboard import Dashboard
        print("✅ dashboard - OK")
    except ImportError as e:
        print(f"❌ dashboard - Error: {e}")
        return False
    
    try:
        from utils.search_engine import SearchEngine
        print("✅ search_engine - OK")
    except ImportError as e:
        print(f"❌ search_engine - Error: {e}")
        return False
    
    try:
        from main_cli import ScrapingCLI
        print("✅ main_cli - OK")
    except ImportError as e:
        print(f"❌ main_cli - Error: {e}")
        return False
    
    return True

def test_scraping_system():
    """Prueba el sistema de scraping básico"""
    print("\n🔍 Probando sistema de scraping...")
    
    try:
        from scraping_avanzado import ScrapingAvanzado
        
        # Crear instancia del scraper
        scraper = ScrapingAvanzado()
        print("✅ Instancia de ScrapingAvanzado creada - OK")
        
        # Verificar configuración
        if hasattr(scraper, 'stores') and scraper.stores:
            print(f"✅ Configuración de tiendas cargada - {len(scraper.stores)} tiendas")
        else:
            print("❌ No se encontró configuración de tiendas")
            return False
        
        # Verificar logging
        if hasattr(scraper, 'logger'):
            print("✅ Sistema de logging configurado - OK")
        else:
            print("❌ Sistema de logging no configurado")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando sistema de scraping: {e}")
        return False

def test_data_manager():
    """Prueba el gestor de datos"""
    print("\n🔍 Probando gestor de datos...")
    
    try:
        from utils.data_manager import DataManager
        
        # Crear instancia del data manager
        data_manager = DataManager()
        print("✅ Instancia de DataManager creada - OK")
        
        # Verificar directorios
        if os.path.exists("data"):
            print("✅ Directorio 'data' existe - OK")
        else:
            print("❌ Directorio 'data' no existe")
            return False
        
        # Verificar base de datos
        if os.path.exists("data/products.db"):
            print("✅ Base de datos existe - OK")
        else:
            print("⚠️ Base de datos no existe (se creará al primer uso)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando gestor de datos: {e}")
        return False

def test_cli_system():
    """Prueba el sistema CLI"""
    print("\n🔍 Probando sistema CLI...")
    
    try:
        from main_cli import ScrapingCLI
        
        # Crear instancia del CLI
        cli = ScrapingCLI()
        print("✅ Instancia de ScrapingCLI creada - OK")
        
        # Verificar componentes
        if hasattr(cli, 'data_manager') and cli.data_manager:
            print("✅ DataManager integrado - OK")
        else:
            print("⚠️ DataManager no integrado")
        
        if hasattr(cli, 'dashboard') and cli.dashboard:
            print("✅ Dashboard integrado - OK")
        else:
            print("⚠️ Dashboard no integrado")
        
        if hasattr(cli, 'search_engine') and cli.search_engine:
            print("✅ SearchEngine integrado - OK")
        else:
            print("⚠️ SearchEngine no integrado")
        
        if hasattr(cli, 'scraper') and cli.scraper:
            print("✅ Scraper integrado - OK")
        else:
            print("⚠️ Scraper no integrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando sistema CLI: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 SISTEMA DE PRUEBAS - SCRAPING DE DESCUENTOS")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")
    print("=" * 60)
    
    tests = [
        ("Importaciones", test_imports),
        ("Módulos del sistema", test_modules),
        ("Sistema de scraping", test_scraping_system),
        ("Gestor de datos", test_data_manager),
        ("Sistema CLI", test_cli_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            print(f"✅ {test_name} - PASÓ")
            passed += 1
        else:
            print(f"❌ {test_name} - FALLÓ")
    
    print(f"\n{'='*60}")
    print("📊 RESUMEN DE PRUEBAS")
    print(f"{'='*60}")
    print(f"✅ Pruebas pasadas: {passed}/{total}")
    print(f"❌ Pruebas fallidas: {total - passed}/{total}")
    
    if passed == total:
        print(f"\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ El sistema está funcionando correctamente")
        print("💡 Puedes ejecutar 'python main_cli.py' para usar el sistema")
    else:
        print(f"\n⚠️ ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revisa los errores anteriores y corrige los problemas")
    
    print(f"\n💡 Para ejecutar el sistema completo:")
    print("   • python main_cli.py")
    print("   • ejecutar_sistema.bat")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 