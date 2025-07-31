#!/usr/bin/env python3
"""
Script de prueba para verificar y optimizar el sistema de notificaciones de Telegram
"""

import os
import sys
from datetime import datetime

def test_telegram_import():
    """Prueba la importación del módulo de Telegram"""
    print("🔍 Probando importación del módulo Telegram...")
    
    try:
        from notifier.telegram_notifier import TelegramNotifier
        print("✅ Módulo Telegram importado correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error importando módulo Telegram: {e}")
        return False

def test_telegram_configuration():
    """Prueba la configuración de Telegram"""
    print("\n🔍 Probando configuración de Telegram...")
    
    # Verificar variables de entorno
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
    
    if bot_token:
        print(f"✅ TELEGRAM_BOT_TOKEN encontrado: {bot_token[:10]}...")
    else:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
    
    if chat_id:
        print(f"✅ TELEGRAM_CHAT_ID encontrado: {chat_id}")
    else:
        print("❌ TELEGRAM_CHAT_ID no configurado")
    
    return bool(bot_token and chat_id)

def test_telegram_connection():
    """Prueba la conexión con Telegram"""
    print("\n🔍 Probando conexión con Telegram...")
    
    try:
        from notifier.telegram_notifier import TelegramNotifier
        
        notifier = TelegramNotifier()
        
        if not notifier.enabled:
            print("❌ Telegram no está habilitado")
            return False
        
        # Probar conexión
        success = notifier.test_connection()
        
        if success:
            print("✅ Conexión con Telegram exitosa")
            return True
        else:
            print("❌ Error en la conexión con Telegram")
            return False
            
    except Exception as e:
        print(f"❌ Error probando conexión: {e}")
        return False

def test_telegram_message():
    """Prueba el envío de mensajes"""
    print("\n🔍 Probando envío de mensajes...")
    
    try:
        from notifier.telegram_notifier import TelegramNotifier
        
        notifier = TelegramNotifier()
        
        if not notifier.enabled:
            print("❌ Telegram no está habilitado")
            return False
        
        # Mensaje de prueba
        test_message = f"""
🧪 <b>PRUEBA DE MENSAJE</b>

✅ Sistema de notificaciones funcionando
⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}

🎯 Este es un mensaje de prueba del sistema optimizado.
        """.strip()
        
        success = notifier.send_message(test_message)
        
        if success:
            print("✅ Mensaje de prueba enviado correctamente")
            return True
        else:
            print("❌ Error enviando mensaje de prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        return False

def test_telegram_alert():
    """Prueba el envío de alertas de ofertas"""
    print("\n🔍 Probando alertas de ofertas...")
    
    try:
        from notifier.telegram_notifier import TelegramNotifier
        
        notifier = TelegramNotifier()
        
        if not notifier.enabled:
            print("❌ Telegram no está habilitado")
            return False
        
        # Producto de prueba
        test_product = {
            'nombre': 'Producto de Prueba - Sistema Optimizado',
            'precio_actual': 15000,
            'precio_original': 100000,
            'descuento_porcentaje': 85,
            'tienda': 'paris',
            'enlace': 'https://www.paris.cl',
            'confiabilidad_score': 0.9
        }
        
        success = notifier.send_offer_alert(test_product)
        
        if success:
            print("✅ Alerta de oferta enviada correctamente")
            return True
        else:
            print("❌ Error enviando alerta de oferta")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando alerta: {e}")
        return False

def create_env_file():
    """Crea un archivo .env con la configuración de Telegram"""
    print("\n🔧 Creando archivo de configuración...")
    
    env_content = """# Configuración de Telegram
# Obtén tu bot token de @BotFather en Telegram
TELEGRAM_BOT_TOKEN=tu_token_aqui

# Obtén tu chat ID de @userinfobot en Telegram
TELEGRAM_CHAT_ID=tu_chat_id_aqui

# Configuración del scraping
MIN_DISCOUNT_PERCENTAGE=70
SCRAPING_INTERVAL_HOURS=1
REQUEST_TIMEOUT=30
MIN_DELAY=1
MAX_DELAY=3
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Archivo .env creado")
        print("📝 Edita el archivo .env con tus credenciales de Telegram")
        return True
        
    except Exception as e:
        print(f"❌ Error creando archivo .env: {e}")
        return False

def show_telegram_setup_instructions():
    """Muestra instrucciones para configurar Telegram"""
    print("\n📱 INSTRUCCIONES PARA CONFIGURAR TELEGRAM:")
    print("=" * 50)
    print("1. 🛠️ Crear un bot de Telegram:")
    print("   • Busca @BotFather en Telegram")
    print("   • Envía /newbot")
    print("   • Sigue las instrucciones")
    print("   • Guarda el token que te da")
    print()
    print("2. 🆔 Obtener tu Chat ID:")
    print("   • Busca @userinfobot en Telegram")
    print("   • Envía cualquier mensaje")
    print("   • Guarda el ID que te responde")
    print()
    print("3. ⚙️ Configurar variables de entorno:")
    print("   • Edita el archivo .env")
    print("   • Reemplaza 'tu_token_aqui' con tu token")
    print("   • Reemplaza 'tu_chat_id_aqui' con tu chat ID")
    print()
    print("4. 🧪 Probar la configuración:")
    print("   • Ejecuta: python test_telegram.py")

def optimize_telegram_integration():
    """Optimiza la integración de Telegram en el sistema principal"""
    print("\n🔧 Optimizando integración de Telegram...")
    
    # Verificar si el sistema principal usa Telegram
    main_files = ['main_cli.py', 'scraping_avanzado.py', 'descuentosgo.py']
    
    for file in main_files:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'TelegramNotifier' not in content:
                    print(f"⚠️ {file} no tiene integración con Telegram")
                else:
                    print(f"✅ {file} tiene integración con Telegram")
                    
            except Exception as e:
                print(f"❌ Error leyendo {file}: {e}")
    
    print("\n💡 Para integrar Telegram en el sistema principal:")
    print("1. Importa: from notifier.telegram_notifier import TelegramNotifier")
    print("2. Crea instancia: self.telegram = TelegramNotifier()")
    print("3. Usa: self.telegram.send_offer_alert(product)")

def main():
    """Función principal de pruebas"""
    print("🚀 SISTEMA DE PRUEBAS - NOTIFICACIONES TELEGRAM")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Importación del módulo", test_telegram_import),
        ("Configuración", test_telegram_configuration),
        ("Conexión", test_telegram_connection),
        ("Envío de mensajes", test_telegram_message),
        ("Alertas de ofertas", test_telegram_alert)
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
        print("✅ El sistema de notificaciones Telegram está funcionando correctamente")
    else:
        print(f"\n⚠️ ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revisa la configuración de Telegram")
        
        # Mostrar instrucciones si no está configurado
        if not test_telegram_configuration():
            show_telegram_setup_instructions()
            create_env_file()
    
    # Optimizar integración
    optimize_telegram_integration()
    
    print(f"\n💡 Para usar Telegram en el sistema:")
    print("   • Configura las variables de entorno")
    print("   • Ejecuta: python test_telegram.py")
    print("   • Integra en el sistema principal")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 