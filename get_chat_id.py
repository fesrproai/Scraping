#!/usr/bin/env python3
"""
Script para obtener el Chat ID correcto de Telegram
"""

import requests
import os

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_chat_id():
    """Obtiene información del bot y ayuda a encontrar el Chat ID"""
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        return
    
    print("🔍 Verificando bot de Telegram...")
    
    # Obtener información del bot
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info['ok']:
                bot_data = bot_info['result']
                print(f"✅ Bot encontrado: @{bot_data['username']}")
                print(f"📝 Nombre: {bot_data['first_name']}")
                print(f"🆔 ID del bot: {bot_data['id']}")
                print()
                print("📱 INSTRUCCIONES PARA OBTENER TU CHAT ID:")
                print("=" * 50)
                print("1. Busca tu bot en Telegram: @" + bot_data['username'])
                print("2. Inicia una conversación con el bot")
                print("3. Envía cualquier mensaje al bot")
                print("4. Ejecuta este comando para obtener tu Chat ID:")
                print(f"   python -c \"import requests; r = requests.get('https://api.telegram.org/bot{bot_token}/getUpdates'); print(r.json())\"")
                print()
                print("5. Busca el 'chat' -> 'id' en la respuesta")
                print("6. Actualiza el archivo .env con el Chat ID correcto")
            else:
                print("❌ Error en la respuesta del bot")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando bot: {e}")

def test_chat_id(chat_id):
    """Prueba un Chat ID específico"""
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        return
    
    print(f"🧪 Probando Chat ID: {chat_id}")
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': '🧪 Prueba de conexión - Sistema de notificaciones funcionando correctamente!'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Chat ID válido - Mensaje enviado correctamente")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando Chat ID: {e}")
        return False

def get_updates():
    """Obtiene las actualizaciones recientes del bot"""
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        return
    
    print("📡 Obteniendo actualizaciones recientes...")
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            updates = response.json()
            if updates['ok'] and updates['result']:
                print("✅ Mensajes recientes encontrados:")
                for update in updates['result']:
                    if 'message' in update:
                        message = update['message']
                        chat = message['chat']
                        print(f"   • Chat ID: {chat['id']}")
                        print(f"     Tipo: {chat['type']}")
                        if 'username' in chat:
                            print(f"     Usuario: @{chat['username']}")
                        if 'first_name' in chat:
                            print(f"     Nombre: {chat['first_name']}")
                        print()
            else:
                print("⚠️ No hay mensajes recientes")
                print("💡 Envía un mensaje al bot y vuelve a ejecutar este comando")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error obteniendo actualizaciones: {e}")

def main():
    """Función principal"""
    print("🚀 OBTENER CHAT ID DE TELEGRAM")
    print("=" * 40)
    
    # Verificar bot
    get_chat_id()
    
    print("\n" + "=" * 40)
    print("📡 OBTENER ACTUALIZACIONES")
    print("=" * 40)
    
    # Obtener actualizaciones
    get_updates()
    
    print("\n" + "=" * 40)
    print("🧪 PROBAR CHAT ID")
    print("=" * 40)
    
    # Probar Chat ID actual
    current_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
    if current_chat_id:
        print(f"Probando Chat ID actual: {current_chat_id}")
        test_chat_id(current_chat_id)
    
    print("\n💡 INSTRUCCIONES:")
    print("1. Busca tu bot en Telegram")
    print("2. Envía un mensaje al bot")
    print("3. Ejecuta: python get_chat_id.py")
    print("4. Copia el Chat ID correcto")
    print("5. Actualiza el archivo .env")

if __name__ == "__main__":
    main() 