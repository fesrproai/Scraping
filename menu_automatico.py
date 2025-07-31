#!/usr/bin/env python3
"""
Menú Automático para DescuentosCL
Funciona inmediatamente sin configuración
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def clear_screen():
    """Limpia la pantalla"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_header():
    """Muestra el encabezado del menú"""
    print("=" * 60)
    print("    🛍️  DESCUENTOSCL - SISTEMA AUTOMÁTICO")
    print("    Encuentra las mejores ofertas en Chile")
    print("=" * 60)
    print()

def show_menu():
    """Muestra el menú principal"""
    print("🎯 SELECCIONA UNA OPCIÓN:")
    print()
    print("1. 🔍 Búsqueda Rápida (Paris)")
    print("2. 🏪 Todas las Tiendas")
    print("3. 🧪 Modo Prueba (Sin guardar)")
    print("4. 📊 Ver Estadísticas")
    print("5. ⚙️  Configurar Firebase")
    print("6. 📖 Ayuda")
    print("7. 🚪 Salir")
    print()

def run_scraping(store='all', dry_run=False, verbose=True):
    """Ejecuta el scraping"""
    print(f"\n🚀 Iniciando scraping automático...")
    print(f"🏪 Tienda: {store.upper()}")
    print(f"🔧 Modo: {'PRUEBA' if dry_run else 'PRODUCCIÓN'}")
    print("-" * 50)
    
    # Construir comando
    cmd = [sys.executable, 'main.py', '--store', store, '--verbose']
    if dry_run:
        cmd.append('--dry-run')
    
    try:
        # Ejecutar scraping
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ Scraping completado exitosamente!")
        else:
            print("\n❌ Error en el scraping")
            
    except Exception as e:
        print(f"\n❌ Error ejecutando scraping: {e}")
    
    input("\n⏸️  Presiona ENTER para continuar...")

def show_statistics():
    """Muestra estadísticas básicas"""
    print("\n📊 ESTADÍSTICAS DEL SISTEMA")
    print("-" * 30)
    
    # Verificar archivos de log
    log_files = ['scraping.log', 'scraping_report_*.json']
    
    for pattern in log_files:
        import glob
        files = glob.glob(pattern)
        if files:
            print(f"📄 Archivos de log encontrados: {len(files)}")
            for file in files[:3]:  # Mostrar solo los primeros 3
                size = os.path.getsize(file) / 1024  # KB
                print(f"   • {file} ({size:.1f} KB)")
        else:
            print(f"📄 No hay archivos de log ({pattern})")
    
    print("\n💡 Para ver estadísticas detalladas, ejecuta:")
    print("   python test_scrapers.py --save-report")

def configure_firebase():
    """Guía para configurar Firebase"""
    print("\n⚙️  CONFIGURACIÓN DE FIREBASE")
    print("-" * 30)
    print("1. Ve a https://console.firebase.google.com")
    print("2. Crea un nuevo proyecto")
    print("3. Ve a Configuración > Cuentas de servicio")
    print("4. Genera una nueva clave privada")
    print("5. Descarga el archivo JSON")
    print("6. Renómbralo como 'firebase-credentials.json'")
    print("7. Colócalo en la carpeta del proyecto")
    print("8. Edita el archivo .env con tus credenciales")
    print()
    print("📄 Archivo .env de ejemplo:")
    print("FIREBASE_PROJECT_ID=tu-proyecto-id")
    print("FIREBASE_PRIVATE_KEY_ID=tu-private-key-id")
    print("FIREBASE_PRIVATE_KEY=tu-private-key")
    print("FIREBASE_CLIENT_EMAIL=tu-client-email")
    print("FIREBASE_CLIENT_ID=tu-client-id")

def show_help():
    """Muestra ayuda del sistema"""
    print("\n📖 AYUDA - DESCUENTOSCL")
    print("=" * 40)
    print()
    print("🎯 ¿QUÉ HACE ESTE SISTEMA?")
    print("   • Busca productos con descuentos del 70% o más")
    print("   • Revisa las principales tiendas chilenas")
    print("   • Guarda los resultados automáticamente")
    print()
    print("🏪 TIENDAS SOPORTADAS:")
    print("   • Paris.cl - Ropa, tecnología, hogar")
    print("   • Falabella.com - Categorización excelente")
    print("   • Ripley.cl - Fácil scraping, muchos descuentos")
    print("   • La Polar.cl - Vestuario y hogar")
    print("   • Hites.com - Productos rebajados")
    print("   • Sodimac.cl - Hogar y construcción")
    print()
    print("🔧 COMANDOS MANUALES:")
    print("   python main.py --store paris --verbose")
    print("   python main.py --store all --dry-run")
    print("   python test_scrapers.py --store all")
    print()
    print("📞 SOPORTE:")
    print("   • Revisa README.md para documentación completa")
    print("   • Logs en scraping.log")
    print("   • Reportes en scraping_report_*.json")

def main():
    """Función principal del menú"""
    while True:
        clear_screen()
        show_header()
        show_menu()
        
        try:
            choice = input("👉 Ingresa tu opción (1-7): ").strip()
            
            if choice == '1':
                # Búsqueda rápida en Paris
                run_scraping(store='paris', dry_run=False, verbose=True)
                
            elif choice == '2':
                # Todas las tiendas
                print("\n⚠️  ADVERTENCIA: Esto puede tomar varios minutos")
                confirm = input("¿Continuar? (s/n): ").lower()
                if confirm in ['s', 'si', 'sí', 'y', 'yes']:
                    run_scraping(store='all', dry_run=False, verbose=True)
                
            elif choice == '3':
                # Modo prueba
                print("\n🧪 MODO PRUEBA - No se guardarán datos")
                run_scraping(store='paris', dry_run=True, verbose=True)
                
            elif choice == '4':
                # Ver estadísticas
                show_statistics()
                input("\n⏸️  Presiona ENTER para continuar...")
                
            elif choice == '5':
                # Configurar Firebase
                configure_firebase()
                input("\n⏸️  Presiona ENTER para continuar...")
                
            elif choice == '6':
                # Ayuda
                show_help()
                input("\n⏸️  Presiona ENTER para continuar...")
                
            elif choice == '7':
                # Salir
                print("\n👋 ¡Gracias por usar DescuentosCL!")
                print("🎉 ¡Que encuentres excelentes ofertas!")
                break
                
            else:
                print("\n❌ Opción inválida. Intenta de nuevo.")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("Presiona ENTER para continuar...")

if __name__ == "__main__":
    main() 