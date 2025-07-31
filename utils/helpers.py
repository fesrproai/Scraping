# -*- coding: utf-8 -*-
import re
import random
import time
import httpx
import logging
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from retrying import retry
from config.settings import DEFAULT_HEADERS, MIN_DELAY, MAX_DELAY, REQUEST_TIMEOUT, RETRY_CONFIG, RATE_LIMIT_CONFIG

logger = logging.getLogger(__name__)

class ScrapingHelper:
    def __init__(self):
        self.ua = UserAgent()
        self.client = httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
        self.request_count = 0
        self.last_request_time = 0
    
    async def _rate_limit(self):
        """Implementa rate limiting para evitar bloqueos"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        min_delay = RATE_LIMIT_CONFIG['delay_between_requests']
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    @retry(
        stop_max_attempt_number=RETRY_CONFIG['max_attempts'],
        wait_fixed=RETRY_CONFIG['delay_between_attempts'] * 1000,
        wait_exponential_multiplier=RETRY_CONFIG['backoff_factor'] * 1000,
        wait_exponential_max=RETRY_CONFIG['max_delay'] * 1000
    )
    async def make_request(self, url, headers=None, timeout=None):
        """Realiza una petición HTTP con reintentos y rate limiting"""
        try:
            await self._rate_limit()
            
            if headers is None:
                headers = {'User-Agent': self.get_random_user_agent()}
            
            logger.info(f"Realizando petición a: {url}")
            response = await self.client.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            logger.info(f"Petición exitosa: {response.status_code}")
            return response.text
            
        except httpx.RequestError as e:
            logger.error(f"Error en petición a {url}: {str(e)}")
            raise
    
    def get_random_user_agent(self):
        """Genera un User-Agent aleatorio"""
        try:
            return self.ua.random
        except Exception as e:
            logger.warning(f"Error generando User-Agent: {e}")
            return DEFAULT_HEADERS['User-Agent']
    
    async def random_delay(self, min_delay=None, max_delay=None):
        """Aplica un delay aleatorio entre peticiones"""
        if min_delay is None:
            min_delay = MIN_DELAY
        if max_delay is None:
            max_delay = MAX_DELAY
        
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"Delay aleatorio: {delay:.2f}s")
        await asyncio.sleep(delay)
    
    def get_soup(self, html_content):
        """Convierte HTML en objeto BeautifulSoup"""
        try:
            return BeautifulSoup(html_content, 'lxml')
        except Exception as e:
            logger.error(f"Error parseando HTML: {e}")
            return None
    
    def parse_price(self, price_text):
        """Extrae precio numérico de texto"""
        if not price_text:
            return None
        
        try:
            # Limpiar texto
            cleaned = re.sub(r'[^\d.,]', '', str(price_text))
            
            # Manejar diferentes formatos de precio
            if ',' in cleaned and '.' in cleaned:
                # Formato: 1.234,56 o 1,234.56
                if cleaned.rfind(',') > cleaned.rfind('.'):
                    # Formato europeo: 1.234,56
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                else:
                    # Formato americano: 1,234.56
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # Solo comas: 1,234
                cleaned = cleaned.replace(',', '')
            
            price = float(cleaned)
            return price if price > 0 else None
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Error parseando precio '{price_text}': {e}")
            return None
    
    def parse_discount_percentage(self, discount_text):
        """Extrae porcentaje de descuento de texto"""
        if not discount_text:
            return 0
        
        try:
            # Buscar patrones de descuento
            patterns = [
                r'(\d+)%',  # 50%
                r'(\d+)\s*por\s*ciento',  # 50 por ciento
                r'(\d+)\s*percent',  # 50 percent
                r'descuento\s*(\d+)',  # descuento 50
                r'rebaja\s*(\d+)',  # rebaja 50
                r'-(\d+)%',  # -50%
            ]
            
            for pattern in patterns:
                match = re.search(pattern, discount_text.lower())
                if match:
                    discount = int(match.group(1))
                    return min(discount, 100)  # Máximo 100%
            
            return 0
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Error parseando descuento '{discount_text}': {e}")
            return 0
    
    def calculate_discount_percentage(self, original_price, current_price):
        """Calcula el porcentaje de descuento"""
        try:
            if not original_price or not current_price:
                return 0
            
            if original_price <= current_price:
                return 0
            
            discount = ((original_price - current_price) / original_price) * 100
            return round(discount, 2)
            
        except (TypeError, ZeroDivisionError) as e:
            logger.warning(f"Error calculando descuento: {e}")
            return 0
    
    def extract_image_url(self, img_element, base_url):
        """Extrae URL de imagen de un elemento img"""
        try:
            # Buscar en diferentes atributos
            for attr in ['src', 'data-src', 'data-lazy', 'data-original']:
                src = img_element.get(attr)
                if src:
                    # Convertir a URL absoluta
                    if src.startswith('//'):
                        return 'https:' + src
                    elif src.startswith('/'):
                        return base_url + src
                    elif src.startswith('http'):
                        return src
                    else:
                        return base_url + '/' + src
            
            return ""
            
        except Exception as e:
            logger.warning(f"Error extrayendo imagen: {e}")
            return ""
    
    def clean_text(self, text):
        """Limpia texto de caracteres especiales"""
        if not text:
            return ""
        
        try:
            # Remover espacios extra y caracteres especiales
            cleaned = re.sub(r'\s+', ' ', str(text).strip())
            cleaned = re.sub(r'[^\w\s\-.,%$]', '', cleaned)
            return cleaned
            
        except Exception as e:
            logger.warning(f"Error limpiando texto: {e}")
            return str(text)
    
    def validate_product_data(self, product):
        """Valida que los datos del producto sean correctos"""
        try:
            required_fields = ['name', 'current_price']
            
            for field in required_fields:
                if not product.get(field):
                    logger.warning(f"Campo requerido faltante: {field}")
                    return False
            
            # Validar precios
            if product.get('original_price') and product.get('current_price'):
                if product['original_price'] < product['current_price']:
                    logger.warning("Precio original menor que precio actual")
                    return False
            
            # Validar descuento
            if product.get('discount_percentage'):
                if not (0 <= product['discount_percentage'] <= 100):
                    logger.warning("Porcentaje de descuento inválido")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando producto: {e}")
            return False