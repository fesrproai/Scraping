# -*- coding: utf-8 -*-
import asyncio
import json
import logging
import os
import telegram
import pandas as pd
# from scrapers.falabella_scraper import FalabellaScraper
from scrapers.paris_scraper import ParisScraper
from scrapers.ripley_scraper import RipleyScraper
from scrapers.hites_scraper import HitesScraper
from scrapers.sodimac_scraper import SodimacScraper

# --- Configuración ---
LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'scraping.log')
DEALS_FILE = 'deals.json'
MIN_DISCOUNT = 70
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# --- Configurar Logging ---
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Scrapers ---
SCRAPERS = {
    # 'falabella': FalabellaScraper(),
    'paris': ParisScraper(),
    'ripley': RipleyScraper(),
    'hites': HitesScraper(),
    'sodimac': SodimacScraper()
}

# --- Funciones Principales ---
async def scrape_all_stores():
    """Ejecuta el scraping en todas las tiendas en paralelo."""
    logger.info(f"Iniciando scraping en {len(SCRAPERS)} tiendas.")
    tasks = [scraper.scrape() for scraper in SCRAPERS.values()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_products = []
    for result in results:
        if isinstance(result, list):
            all_products.extend(result)
        elif isinstance(result, Exception):
            logger.error(f"Error durante el scraping: {result}")
            
    return all_products

def filter_deals(products):
    """Filtra los productos para encontrar ofertas con un descuento mínimo."""
    df = pd.DataFrame(products)
    if 'discount_percentage' in df.columns:
        deals = df[df['discount_percentage'] >= MIN_DISCOUNT]
        return deals.to_dict('records')
    return []

def save_deals_to_json(deals):
    """Guarda las ofertas en un archivo JSON."""
    with open(DEALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(deals, f, indent=4, ensure_ascii=False)
    logger.info(f"{len(deals)} ofertas guardadas en {DEALS_FILE}")

async def send_telegram_notification(deals):
    """Envía una notificación a Telegram con las mejores ofertas."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("No se ha configurado el bot de Telegram. Omitiendo notificación.")
        return

    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    message = f"¡Se encontraron {len(deals)} nuevas ofertas con {MIN_DISCOUNT}% de descuento o más!\n\n"
    
    for deal in deals[:5]: # Enviar las 5 mejores ofertas
        message += f"- *{deal['name']}*\n"
        message += f"  Precio: ${deal['current_price']:,}\n"
        message += f"  Descuento: {deal['discount_percentage']}%\n"
        message += f"  Tienda: {deal['store']}\n\n"

    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        logger.info("Notificación de Telegram enviada.")
    except Exception as e:
        logger.error(f"Error al enviar la notificación de Telegram: {e}")

# --- Flujo Principal ---
async def main():
    """Función principal que orquesta el proceso de scraping."""
    logger.info("--- Iniciando Proceso de Scraping de Ofertas ---")
    
    products = await scrape_all_stores()
    deals = filter_deals(products)
    
    if deals:
        save_deals_to_json(deals)
        await send_telegram_notification(deals)
    else:
        logger.info("No se encontraron ofertas que cumplan con el criterio.")
        
    logger.info("--- Proceso de Scraping de Ofertas Finalizado ---")

if __name__ == '__main__':
    asyncio.run(main())
