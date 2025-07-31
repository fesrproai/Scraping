#!/usr/bin/env python3
"""
Script para crear el ejecutable de DescuentosGO
Versión 2.0 - Scanner automático infinito con Telegram
"""

import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    """Instala PyInstaller si no está disponible"""
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
        return True
    except ImportError:
        print("📦 Instalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller instalado correctamente")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error al instalar PyInstaller")
            return False

def build_executable():
    """Construye el ejecutable"""
    print("🔨 Construyendo ejecutable de DescuentosGO...")
    
    # Comando de PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Un solo archivo
        "--console",                    # Aplicación de consola
        "--name=DescuentosGO",  # Nombre del ejecutable
        "--add-data=data;data",         # Incluir directorio de datos
        "--hidden-import=requests",
        "--hidden-import=beautifulsoup4", 
        "--hidden-import=lxml",
        "--hidden-import=sqlite3",
        "--hidden-import=json",
        "--hidden-import=datetime",
        "--hidden-import=hashlib",
        "--hidden-import=re",
        "--hidden-import=threading",
        "--hidden-import=time",
        "--hidden-import=os",
        "--hidden-import=sys",
        "--hidden-import=typing",
        "descuentosgo.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ Ejecutable construido correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al construir ejecutable: {e}")
        return False

def copy_to_desktop():
    """Copia el ejecutable al escritorio"""
    desktop_path = os.path.expanduser("~/Desktop")
    source_path = "dist/DescuentosGO.exe"
    dest_path = os.path.join(desktop_path, "DescuentosGO.exe")
    
    try:
        shutil.copy2(source_path, dest_path)
        print(f"✅ Ejecutable copiado al escritorio: {dest_path}")
        return True
    except Exception as e:
        print(f"❌ Error al copiar al escritorio: {e}")
        return False

def create_data_directory():
    """Crea el directorio de datos si no existe"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print("✅ Directorio de datos creado")

def main():
    """Función principal"""
    print("🎯 DESCUENTOSGO - Constructor de Ejecutable")
    print("=" * 60)
    
    # Verificar que el archivo principal existe
    if not os.path.exists("descuentosgo.py"):
        print("❌ Error: No se encuentra descuentosgo.py")
        return False
    
    # Crear directorio de datos
    create_data_directory()
    
    # Instalar PyInstaller
    if not install_pyinstaller():
        return False
    
    # Construir ejecutable
    if not build_executable():
        return False
    
    # Copiar al escritorio
    if not copy_to_desktop():
        return False
    
    print("\n🎉 ¡Ejecutable creado exitosamente!")
    print("📁 Ubicación: ~/Desktop/DescuentosGO.exe")
    print("\n🚀 Características incluidas:")
    print("   • Scanner automático infinito")
    print("   • 12 tiendas chilenas")
    print("   • Gestión de categorías con checkboxes")
    print("   • Bot de Telegram integrado")
    print("   • Base de datos SQLite")
    print("   • Notificaciones automáticas")
    print("   • Menú interactivo completo")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Proceso completado. Puedes ejecutar el programa desde el escritorio.")
    else:
        print("\n❌ Error en el proceso de construcción.")
    
    input("\nPresiona Enter para salir...") 