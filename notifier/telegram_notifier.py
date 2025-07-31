#!/usr/bin/env python3
"""
Módulo de notificaciones por Telegram para DescuentosGO
Envía alertas cuando se detectan ofertas extremas
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class TelegramNotifier:
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID', '')
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if self.enabled:
            print("✅ Notificaciones Telegram configuradas")
        else:
            print("⚠️ Notificaciones Telegram no configuradas")
    
    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Envía un mensaje por Telegram"""
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Error enviando mensaje Telegram: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en notificación Telegram: {e}")
            return False
    
    def send_offer_alert(self, product: Dict, discount_threshold: float = 85) -> bool:
        """Envía alerta por oferta extrema"""
        if not self.enabled:
            return False
        
        discount = product.get('descuento_porcentaje', 0)
        if discount < discount_threshold:
            return False
        
        try:
            message = f"""
🚨 ¡OFERTA EXTREMA DETECTADA! 🚨

🏪 <b>{product['tienda'].upper()}</b>
📦 <b>{product['nombre']}</b>

💰 <b>Precio actual:</b> ${product['precio_actual']:,}
💸 <b>Precio original:</b> ${product['precio_original']:,}
🎯 <b>Descuento:</b> {product['descuento_porcentaje']}%
⭐ <b>Confiabilidad:</b> {product.get('confiabilidad_score', 1.0):.1f}/1.0

🔗 <a href="{product['enlace']}">Ver oferta</a>

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"❌ Error creando alerta: {e}")
            return False
    
    def send_daily_summary(self, products: List[Dict]) -> bool:
        """Envía resumen diario de ofertas"""
        if not self.enabled or not products:
            return False
        
        try:
            # Filtrar solo ofertas con 70%+ de descuento
            extreme_offers = [p for p in products if p.get('descuento_porcentaje', 0) >= 70]
            
            if not extreme_offers:
                return False
            
            # Agrupar por tienda
            stores = {}
            for product in extreme_offers:
                store = product['tienda']
                if store not in stores:
                    stores[store] = []
                stores[store].append(product)
            
            message = f"""
📊 <b>RESUMEN DIARIO - DESCUENTOSGO</b>

📦 <b>Total de ofertas:</b> {len(extreme_offers)}
🎯 <b>Descuento mínimo:</b> 70%
📅 <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y')}

🏪 <b>Ofertas por tienda:</b>
            """.strip()
            
            for store, store_products in stores.items():
                best_discount = max(p['descuento_porcentaje'] for p in store_products)
                message += f"\n• {store.upper()}: {len(store_products)} ofertas (máx: {best_discount}%)"
            
            # Top 3 mejores ofertas
            top_offers = sorted(extreme_offers, key=lambda x: x['descuento_porcentaje'], reverse=True)[:3]
            
            message += "\n\n🏆 <b>TOP 3 MEJORES OFERTAS:</b>"
            for i, product in enumerate(top_offers, 1):
                message += f"""
{i}. {product['nombre'][:40]}...
   💰 ${product['precio_actual']:,} | 🎯 {product['descuento_porcentaje']}%
   🏪 {product['tienda'].upper()}
                """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"❌ Error enviando resumen diario: {e}")
            return False
    
    def send_error_alert(self, error_message: str) -> bool:
        """Envía alerta de error"""
        if not self.enabled:
            return False
        
        try:
            message = f"""
⚠️ <b>ERROR EN DESCUENTOSGO</b>

❌ <b>Error:</b> {error_message}
⏰ <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}

🔧 Revisar logs para más detalles.
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"❌ Error enviando alerta de error: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Prueba la conexión con Telegram"""
        if not self.enabled:
            print("❌ Telegram no está configurado")
            return False
        
        try:
            message = f"""
🧪 <b>PRUEBA DE CONEXIÓN</b>

✅ DescuentosGO está funcionando correctamente
⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}

🎯 Las notificaciones están activas para ofertas con 85%+ de descuento.
            """.strip()
            
            success = self.send_message(message)
            if success:
                print("✅ Conexión con Telegram exitosa")
            else:
                print("❌ Error en la conexión con Telegram")
            
            return success
            
        except Exception as e:
            print(f"❌ Error probando conexión: {e}")
            return False

def main():
    """Función de prueba"""
    notifier = TelegramNotifier()
    
    if notifier.enabled:
        print("🧪 Probando conexión con Telegram...")
        notifier.test_connection()
        
        # Ejemplo de alerta de oferta
        test_product = {
            'nombre': 'Producto de prueba',
            'precio_actual': 15000,
            'precio_original': 50000,
            'descuento_porcentaje': 85,
            'tienda': 'paris',
            'enlace': 'https://www.paris.cl',
            'confiabilidad_score': 0.9
        }
        
        print("📱 Enviando alerta de prueba...")
        notifier.send_offer_alert(test_product)
    else:
        print("⚠️ Configura las variables de entorno:")
        print("   TELEGRAM_BOT_TOKEN=tu_token_aqui")
        print("   TELEGRAM_CHAT_ID=tu_chat_id_aqui")

if __name__ == "__main__":
    main() 