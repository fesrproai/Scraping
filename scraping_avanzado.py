#!/usr/bin/env python3
"""
Sistema de Scraping de Descuentos - Versión Avanzada Optimizada
Usa múltiples técnicas para encontrar productos reales con mejor rendimiento
"""

import os
import json
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
import logging
from typing import List, Dict, Optional, Tuple
from tqdm import tqdm
import colorama
from colorama import Fore, Style
import random

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Inicializar colorama para Windows
colorama.init()

# Importar sistema de notificaciones
try:
    from notifier.telegram_notifier import TelegramNotifier
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

class ScrapingAvanzado:
    def __init__(self):
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Configurar logging
        self.setup_logging()
        
        # Headers más realistas para evitar detección
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        # Configuración de tiendas con URLs más específicas
        self.stores = {
            'paris': {
                'name': 'Paris',
                'base_url': 'https://www.paris.cl',
                'categories': [
                    {
                        'name': 'Página Principal',
                        'url': 'https://www.paris.cl'
                    },
                    {
                        'name': 'Ofertas',
                        'url': 'https://www.paris.cl/ofertas'
                    }
                ]
            },
            'falabella': {
                'name': 'Falabella',
                'base_url': 'https://www.falabella.com',
                'categories': [
                    {
                        'name': 'Ofertas',
                        'url': 'https://www.falabella.com/falabella-cl/collection/ofertas'
                    },
                    {
                        'name': 'Tecnología',
                        'url': 'https://www.falabella.com/falabella-cl/category/cat20002/Tecnologia'
                    },
                    {
                        'name': 'Hogar',
                        'url': 'https://www.falabella.com/falabella-cl/category/cat20001/Hogar-y-Muebles'
                    }
                ]
            }
        }
        
        # Configuración de timeouts y reintentos
        self.timeout = 30
        self.max_retries = 3
        self.delay_between_requests = 2
        
        # Data manager para almacenamiento
        self.data_manager = None
        
        # Sistema de notificaciones Telegram
        if TELEGRAM_AVAILABLE:
            self.telegram = TelegramNotifier()
            if self.telegram.enabled:
                self.logger.info("✅ Sistema de notificaciones Telegram habilitado")
                print(f"{Fore.GREEN}✅ Sistema de notificaciones Telegram habilitado{Style.RESET_ALL}")
            else:
                self.logger.info("⚠️ Sistema de notificaciones Telegram no configurado")
                print(f"{Fore.YELLOW}⚠️ Sistema de notificaciones Telegram no configurado{Style.RESET_ALL}")
        else:
            self.telegram = None
            self.logger.info("⚠️ Módulo de notificaciones Telegram no disponible")
            print(f"{Fore.YELLOW}⚠️ Módulo de notificaciones Telegram no disponible{Style.RESET_ALL}")
    
    def setup_logging(self):
        """Configura el sistema de logging"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, f"scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_page_content(self, url: str) -> Optional[str]:
        """Obtiene el contenido de una página web con headers mejorados y reintentos"""
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"📡 Cargando (intento {attempt + 1}/{self.max_retries}): {url}")
                print(f"{Fore.CYAN}📡 Cargando: {url}{Style.RESET_ALL}")
                
                # Agregar delay aleatorio para evitar detección
                time.sleep(random.uniform(1, self.delay_between_requests))
                
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    timeout=self.timeout,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # Verificar que el contenido sea HTML
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' not in content_type:
                    self.logger.warning(f"Contenido no es HTML: {content_type}")
                    return None
                
                self.logger.info(f"✅ Página cargada exitosamente: {url}")
                return response.text
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"⏰ Timeout en intento {attempt + 1} para {url}")
                print(f"{Fore.YELLOW}⏰ Timeout en intento {attempt + 1} para {url}{Style.RESET_ALL}")
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"❌ Error en intento {attempt + 1} para {url}: {e}")
                print(f"{Fore.RED}❌ Error en intento {attempt + 1} para {url}: {e}{Style.RESET_ALL}")
                
            except Exception as e:
                self.logger.error(f"❌ Error inesperado en intento {attempt + 1} para {url}: {e}")
                print(f"{Fore.RED}❌ Error inesperado en intento {attempt + 1} para {url}: {e}{Style.RESET_ALL}")
        
        self.logger.error(f"❌ Falló después de {self.max_retries} intentos: {url}")
        print(f"{Fore.RED}❌ Falló después de {self.max_retries} intentos: {url}{Style.RESET_ALL}")
        return None
    
    def extract_products_from_html(self, html_content: str, store_name: str) -> List[Dict]:
        """Extrae productos usando múltiples técnicas optimizadas"""
        if not html_content:
            return []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            products = []
            
            # Técnica 1: Buscar elementos con datos de productos
            product_elements = []
            
            # Selectores optimizados para cada tienda
            if store_name == 'paris':
                selectors = [
                    '.product-item', '.product-card', '.product-grid-item',
                    '.product-tile', '.product-container', '.product-box',
                    '.product', '.item', '.card', '.producto',
                    '[data-product]', '[class*="product"]', '[class*="item"]',
                    '[class*="card"]', '.product-grid', '.product-list'
                ]
            else:  # falabella
                selectors = [
                    '.pod-item', '.pod', '.product-item', '.product-card',
                    '.product-grid-item', '.product-tile', '.product-container',
                    '.product-box', '.product', '.item', '.card',
                    '[class*="product"]', '[class*="item"]', '[class*="card"]'
                ]
            
            # Buscar elementos con selectores específicos
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    self.logger.info(f"✅ Encontrados {len(elements)} elementos con selector: {selector}")
                    print(f"{Fore.GREEN}✅ Encontrados {len(elements)} elementos con selector: {selector}{Style.RESET_ALL}")
                    product_elements.extend(elements)
                    break
            
            # Técnica 2: Si no encontramos con selectores específicos, buscar por patrones
            if not product_elements:
                self.logger.info("🔍 Buscando productos por patrones de precio...")
                print(f"{Fore.YELLOW}🔍 Buscando productos por patrones de precio...{Style.RESET_ALL}")
                
                # Buscar elementos que contengan precios
                price_pattern = re.compile(r'\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?')
                elements_with_prices = soup.find_all(text=price_pattern)
                
                for element in elements_with_prices:
                    parent = element.parent
                    if parent and parent.name not in ['script', 'style']:
                        product_elements.append(parent)
            
            # Extraer información de cada elemento con barra de progreso
            self.logger.info(f"🔄 Procesando {len(product_elements)} elementos encontrados...")
            print(f"{Fore.BLUE}🔄 Procesando {len(product_elements)} elementos encontrados...{Style.RESET_ALL}")
            
            for element in tqdm(product_elements[:20], desc="Extrayendo productos", unit="producto"):
                product = self.extract_product_info(element, store_name)
                if product and product.get('name') and product.get('current_price'):
                    products.append(product)
            
            self.logger.info(f"✅ Extraídos {len(products)} productos válidos de {store_name}")
            print(f"{Fore.GREEN}✅ Extraídos {len(products)} productos válidos de {store_name}{Style.RESET_ALL}")
            
            return products
            
        except Exception as e:
            self.logger.error(f"❌ Error extrayendo productos de {store_name}: {e}")
            print(f"{Fore.RED}❌ Error extrayendo productos de {store_name}: {e}{Style.RESET_ALL}")
            return []
    
    def extract_product_info(self, element, store_name):
        """Extrae información detallada de un producto con mejor manejo de errores"""
        try:
            # Buscar nombre del producto
            name = self.extract_product_name(element, store_name)
            
            # Buscar precios
            current_price, original_price = self.extract_prices(element)
            
            # Buscar descuento
            discount = self.extract_discount(element)
            
            # Buscar enlace
            product_link = self.extract_product_link(element, store_name)
            
            # Buscar imagen
            product_image = self.extract_product_image(element, store_name)
            
            # Validar que el producto tenga información mínima
            if not name or not current_price:
                return None
            
            # Crear objeto producto
            product = {
                'name': name.strip(),
                'current_price': current_price.strip(),
                'original_price': original_price.strip() if original_price else "",
                'discount': discount.strip() if discount else "",
                'product_link': product_link.strip() if product_link else "",
                'product_image': product_image.strip() if product_image else "",
                'store': store_name,
                'scraped_at': datetime.now().isoformat()
            }
            
            return product
            
        except Exception as e:
            self.logger.debug(f"Error extrayendo información de producto: {e}")
            return None
    
    def extract_product_name(self, element, store_name):
        """Extrae el nombre del producto"""
        name_selectors = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            '.title', '.name', '.product-name', '.product-title',
            '.item-title', '.card-title', '.product-name',
            '[data-product-name]', '[title]', 'a[title]'
        ]
        
        for selector in name_selectors:
            try:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    if name and len(name) > 3 and len(name) < 200:
                        return name
            except:
                continue
        
        # Buscar en el texto del elemento
        text = element.get_text(strip=True)
        if text and len(text) > 3 and len(text) < 200:
            return text[:100]  # Limitar longitud
        
        return ""
    
    def extract_prices(self, element):
        """Extrae precios actual y original"""
        # Patrón para precios chilenos
        price_pattern = re.compile(r'\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)')
        
        # Buscar todos los precios en el elemento
        text = element.get_text()
        prices = price_pattern.findall(text)
        
        if len(prices) >= 2:
            # Si hay múltiples precios, el más alto es el original
            prices = [int(p.replace('.', '').replace(',', '')) for p in prices]
            prices.sort(reverse=True)
            original_price = f"${prices[0]:,}".replace(',', '.')
            current_price = f"${prices[1]:,}".replace(',', '.')
            return current_price, original_price
        elif len(prices) == 1:
            current_price = f"${prices[0]}"
            return current_price, ""
        
        return "", ""
    
    def extract_discount(self, element):
        """Extrae información de descuento"""
        discount_selectors = [
            '.discount', '.discount-badge', '.discount-percentage',
            '.discount-label', '.sale-badge', '.discount-tag',
            '[class*="discount"]', '[class*="sale"]'
        ]
        
        for selector in discount_selectors:
            try:
                discount_elem = element.select_one(selector)
                if discount_elem:
                    discount = discount_elem.get_text(strip=True)
                    if discount and ('%' in discount or 'off' in discount.lower()):
                        return discount
            except:
                continue
        
        return ""
    
    def extract_product_link(self, element, store_name):
        """Extrae el enlace del producto"""
        try:
            link_elem = element.find('a')
            if link_elem:
                href = link_elem.get('href')
                if href:
                    if not href.startswith('http'):
                        href = self.stores[store_name]['base_url'] + href
                    return href
        except:
            pass
        return ""
    
    def extract_product_image(self, element, store_name):
        """Extrae la imagen del producto"""
        try:
            img_elem = element.find('img')
            if img_elem:
                src = img_elem.get('src') or img_elem.get('data-src')
                if src:
                    if not src.startswith('http'):
                        src = self.stores[store_name]['base_url'] + src
                    return src
        except:
            pass
        return ""
    
    def scrape_store(self, store_name: str) -> List[Dict]:
        """Scraping de una tienda específica con mejor manejo de errores"""
        if store_name not in self.stores:
            self.logger.error(f"❌ Tienda no encontrada: {store_name}")
            print(f"{Fore.RED}❌ Tienda no encontrada: {store_name}{Style.RESET_ALL}")
            return []
        
        store_config = self.stores[store_name]
        all_products = []
        
        self.logger.info(f"🏪 Iniciando scraping de {store_config['name']}")
        print(f"{Fore.CYAN}\n🏪 Scraping {store_config['name']} con técnicas avanzadas...{Style.RESET_ALL}")
        
        for category in tqdm(store_config['categories'], desc=f"Procesando categorías de {store_config['name']}", unit="categoría"):
            try:
                self.logger.info(f"📂 Procesando categoría: {category['name']}")
                print(f"{Fore.BLUE}  📂 Categoría: {category['name']}{Style.RESET_ALL}")
                
                html_content = self.get_page_content(category['url'])
                if not html_content:
                    self.logger.warning(f"⚠️ No se pudo cargar contenido de {category['name']}")
                    continue
                
                products = self.extract_products_from_html(html_content, store_name)
                
                if products:
                    all_products.extend(products)
                    self.logger.info(f"✅ {len(products)} productos encontrados en {category['name']}")
                    print(f"{Fore.GREEN}    📦 {len(products)} productos encontrados{Style.RESET_ALL}")
                else:
                    self.logger.warning(f"⚠️ No se encontraron productos en {category['name']}")
                    print(f"{Fore.YELLOW}    ⚠️  No se encontraron productos en esta categoría{Style.RESET_ALL}")
                
                # Delay entre categorías para evitar detección
                time.sleep(random.uniform(1.5, 3.0))
                
            except Exception as e:
                self.logger.error(f"❌ Error en categoría {category['name']}: {e}")
                print(f"{Fore.RED}    ❌ Error en categoría {category['name']}: {e}{Style.RESET_ALL}")
                continue
        
        self.logger.info(f"✅ Scraping completado de {store_config['name']}: {len(all_products)} productos totales")
        print(f"{Fore.GREEN}✅ Scraping completado de {store_config['name']}: {len(all_products)} productos totales{Style.RESET_ALL}")
        
        return all_products
    
    def save_products(self, products: List[Dict], store_name: str) -> Optional[str]:
        """Guarda productos usando el data manager con mejor manejo de errores"""
        if not products:
            self.logger.warning("⚠️ No hay productos para guardar")
            return None
        
        try:
            self.logger.info(f"💾 Guardando {len(products)} productos de {store_name}")
            print(f"{Fore.CYAN}💾 Guardando {len(products)} productos de {store_name}...{Style.RESET_ALL}")
            
            # Guardar en base de datos si hay data manager
            saved_count = 0
            if hasattr(self, 'data_manager') and self.data_manager:
                for product in tqdm(products, desc="Guardando en base de datos", unit="producto"):
                    if self.data_manager.save_product_to_db(product):
                        saved_count += 1
                
                if saved_count > 0:
                    self.logger.info(f"✅ {saved_count} productos guardados en base de datos")
                    print(f"{Fore.GREEN}✅ {saved_count} productos guardados en base de datos{Style.RESET_ALL}")
                    
                    # También guardar en JSON y CSV
                    json_file = self.data_manager.save_products_to_json(products, store_name)
                    csv_file = self.data_manager.save_products_to_csv(products, store_name)
                    
                    if json_file:
                        self.logger.info(f"✅ Productos guardados en JSON: {json_file}")
                    if csv_file:
                        self.logger.info(f"✅ Productos guardados en CSV: {csv_file}")
                    
                    return f"database_{saved_count}_products"
            
            # Fallback: guardar en JSON si no hay data manager
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.data_dir}/{store_name}_products_avanzado_{timestamp}.json"
            
            data = {
                'store': store_name,
                'timestamp': datetime.now().isoformat(),
                'total_products': len(products),
                'method': 'avanzado',
                'products': products
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ {len(products)} productos guardados en {filename}")
            print(f"{Fore.GREEN}✅ {len(products)} productos guardados en {filename}{Style.RESET_ALL}")
            
            # Enviar notificaciones de ofertas extremas
            notifications_sent = self.send_extreme_offer_notifications(products)
            if notifications_sent > 0:
                print(f"{Fore.CYAN}📱 {notifications_sent} notificaciones Telegram enviadas{Style.RESET_ALL}")
            
            return filename
            
        except Exception as e:
            self.logger.error(f"❌ Error guardando productos: {e}")
            print(f"{Fore.RED}❌ Error guardando productos: {e}{Style.RESET_ALL}")
            return None
    
    def send_extreme_offer_notifications(self, products: List[Dict]) -> int:
        """Envía notificaciones de ofertas extremas por Telegram"""
        if not self.telegram or not self.telegram.enabled:
            return 0
        
        notifications_sent = 0
        extreme_offers = []
        
        # Filtrar ofertas con 85%+ de descuento
        for product in products:
            try:
                # Calcular descuento si no está presente
                if 'discount' not in product or not product['discount']:
                    current_price = product.get('current_price', '')
                    original_price = product.get('original_price', '')
                    
                    if current_price and original_price:
                        # Extraer números de los precios
                        import re
                        current_num = re.findall(r'\d+', current_price.replace('.', ''))
                        original_num = re.findall(r'\d+', original_price.replace('.', ''))
                        
                        if current_num and original_num:
                            current_val = int(current_num[0])
                            original_val = int(original_num[0])
                            
                            if original_val > 0:
                                discount_percent = ((original_val - current_val) / original_val) * 100
                                if discount_percent >= 85:
                                    extreme_offers.append({
                                        'nombre': product.get('name', 'Producto sin nombre'),
                                        'precio_actual': current_val,
                                        'precio_original': original_val,
                                        'descuento_porcentaje': discount_percent,
                                        'tienda': product.get('store', 'Tienda desconocida'),
                                        'enlace': product.get('product_link', ''),
                                        'confiabilidad_score': 0.9
                                    })
                else:
                    # Si ya tiene descuento calculado
                    discount_text = product['discount']
                    discount_match = re.findall(r'(\d+)%', discount_text)
                    if discount_match:
                        discount_percent = int(discount_match[0])
                        if discount_percent >= 85:
                            extreme_offers.append({
                                'nombre': product.get('name', 'Producto sin nombre'),
                                'precio_actual': product.get('current_price', ''),
                                'precio_original': product.get('original_price', ''),
                                'descuento_porcentaje': discount_percent,
                                'tienda': product.get('store', 'Tienda desconocida'),
                                'enlace': product.get('product_link', ''),
                                'confiabilidad_score': 0.9
                            })
                            
            except Exception as e:
                self.logger.debug(f"Error procesando producto para notificación: {e}")
                continue
        
        # Enviar notificaciones
        for offer in extreme_offers:
            try:
                if self.telegram.send_offer_alert(offer):
                    notifications_sent += 1
                    self.logger.info(f"📱 Notificación enviada para oferta extrema: {offer['nombre']}")
                    print(f"{Fore.GREEN}📱 Notificación enviada para oferta extrema: {offer['nombre']}{Style.RESET_ALL}")
            except Exception as e:
                self.logger.error(f"❌ Error enviando notificación: {e}")
        
        if notifications_sent > 0:
            self.logger.info(f"📱 {notifications_sent} notificaciones de ofertas extremas enviadas")
            print(f"{Fore.GREEN}📱 {notifications_sent} notificaciones de ofertas extremas enviadas{Style.RESET_ALL}")
        
        return notifications_sent
    
    def run_scraping(self, stores_to_scrape: Optional[List[str]] = None) -> Dict:
        """Ejecuta el scraping completo con mejor manejo de errores y estadísticas"""
        self.logger.info("🚀 Iniciando sistema de scraping de descuentos")
        print(f"{Fore.CYAN}🚀 Sistema de Scraping de Descuentos - Versión Avanzada Optimizada{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}💾 Usando técnicas avanzadas para encontrar productos{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📁 Los datos se guardarán localmente en la carpeta 'data'{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Logs detallados en la carpeta 'logs'{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        
        start_time = time.time()
        
        if stores_to_scrape is None:
            stores_to_scrape = list(self.stores.keys())
        
        total_products = 0
        saved_files = []
        successful_stores = 0
        failed_stores = 0
        
        self.logger.info(f"🎯 Iniciando scraping de {len(stores_to_scrape)} tiendas: {', '.join(stores_to_scrape)}")
        
        for store_name in tqdm(stores_to_scrape, desc="Procesando tiendas", unit="tienda"):
            if store_name not in self.stores:
                self.logger.error(f"❌ Tienda '{store_name}' no configurada")
                print(f"{Fore.RED}❌ Tienda '{store_name}' no configurada{Style.RESET_ALL}")
                failed_stores += 1
                continue
            
            try:
                products = self.scrape_store(store_name)
                
                if products:
                    filename = self.save_products(products, store_name)
                    if filename:
                        saved_files.append(filename)
                    total_products += len(products)
                    successful_stores += 1
                else:
                    self.logger.warning(f"⚠️ No se encontraron productos en {store_name}")
                    failed_stores += 1
                    
            except Exception as e:
                self.logger.error(f"❌ Error procesando tienda {store_name}: {e}")
                print(f"{Fore.RED}❌ Error procesando tienda {store_name}: {e}{Style.RESET_ALL}")
                failed_stores += 1
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Resumen final optimizado
        self.logger.info(f"✅ Scraping completado en {execution_time:.2f} segundos")
        print(f"\n{Fore.GREEN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📊 RESUMEN FINAL{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Total productos encontrados: {total_products}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🏪 Tiendas exitosas: {successful_stores}{Style.RESET_ALL}")
        print(f"{Fore.RED}❌ Tiendas fallidas: {failed_stores}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📁 Archivos guardados: {len(saved_files)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⏱️  Tiempo de ejecución: {execution_time:.2f} segundos{Style.RESET_ALL}")
        
        if saved_files:
            print(f"\n{Fore.CYAN}📂 Archivos creados:{Style.RESET_ALL}")
            for file in saved_files:
                print(f"   • {file}")
        
        print(f"\n{Fore.GREEN}🎉 Scraping completado exitosamente!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}💡 Revisa la carpeta 'data' para ver los resultados{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📋 Revisa la carpeta 'logs' para ver los logs detallados{Style.RESET_ALL}")
        
        return {
            'total_products': total_products,
            'successful_stores': successful_stores,
            'failed_stores': failed_stores,
            'saved_files': saved_files,
            'execution_time': execution_time
        }

def main():
    scraper = ScrapingAvanzado()
    scraper.run_scraping()

if __name__ == "__main__":
    main() 