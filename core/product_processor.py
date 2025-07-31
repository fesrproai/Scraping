from config.settings import MIN_DISCOUNT_PERCENTAGE
from utils.helpers import ScrapingHelper
import re

class ProductProcessor:
    def __init__(self):
        self.helper = ScrapingHelper()
    
    def process_products(self, products, store_name):
        """Procesa y valida una lista de productos"""
        processed_products = []
        
        for product in products:
            processed_product = self.process_single_product(product, store_name)
            if processed_product:
                processed_products.append(processed_product)
        
        return processed_products
    
    def process_single_product(self, product, store_name):
        """Procesa y valida un producto individual"""
        try:
            # Validar campos requeridos
            if not self.validate_required_fields(product):
                return None
            
            # Limpiar y normalizar datos
            cleaned_product = self.clean_product_data(product)
            
            # Calcular descuento si no existe
            if not cleaned_product.get('discount_percentage'):
                cleaned_product['discount_percentage'] = self.calculate_discount(
                    cleaned_product.get('original_price'),
                    cleaned_product.get('current_price')
                )
            
            # Verificar si cumple con el descuento mínimo
            if cleaned_product['discount_percentage'] < MIN_DISCOUNT_PERCENTAGE:
                return None
            
            # Agregar metadatos
            cleaned_product['store'] = store_name
            cleaned_product['processed'] = True
            
            return cleaned_product
            
        except Exception as e:
            print(f"❌ Error procesando producto: {str(e)}")
            return None
    
    def validate_required_fields(self, product):
        """Valida que el producto tenga los campos requeridos"""
        required_fields = ['name', 'current_price']
        
        for field in required_fields:
            if not product.get(field):
                return False
        
        # Validar que el precio sea un número válido
        if not isinstance(product.get('current_price'), (int, float)):
            return False
        
        return True
    
    def clean_product_data(self, product):
        """Limpia y normaliza los datos del producto"""
        cleaned = {}
        
        # Limpiar nombre
        if product.get('name'):
            cleaned['name'] = self.helper.clean_text(product['name'])
            # Eliminar caracteres especiales problemáticos
            cleaned['name'] = re.sub(r'[^\w\s\-\.]', '', cleaned['name'])
        
        # Limpiar precios
        if product.get('original_price'):
            cleaned['original_price'] = float(product['original_price'])
        
        if product.get('current_price'):
            cleaned['current_price'] = float(product['current_price'])
        
        # Limpiar descuento
        if product.get('discount_percentage'):
            cleaned['discount_percentage'] = float(product['discount_percentage'])
        
        # Limpiar URL
        if product.get('product_url'):
            cleaned['product_url'] = self.clean_url(product['product_url'])
        
        # Limpiar imagen
        if product.get('image_url'):
            cleaned['image_url'] = self.clean_url(product['image_url'])
        
        # Limpiar categoría
        if product.get('category'):
            cleaned['category'] = self.helper.clean_text(product['category'])
        
        return cleaned
    
    def clean_url(self, url):
        """Limpia y valida una URL"""
        if not url:
            return ""
        
        # Eliminar espacios
        url = url.strip()
        
        # Asegurar que tenga protocolo
        if url.startswith('//'):
            url = f"https:{url}"
        elif not url.startswith('http'):
            url = f"https://{url}"
        
        return url
    
    def calculate_discount(self, original_price, current_price):
        """Calcula el porcentaje de descuento"""
        if not original_price or not current_price:
            return 0
        
        if original_price <= current_price:
            return 0
        
        discount = ((original_price - current_price) / original_price) * 100
        return round(discount, 2)
    
    def filter_by_discount(self, products, min_discount=None):
        """Filtra productos por descuento mínimo"""
        if min_discount is None:
            min_discount = MIN_DISCOUNT_PERCENTAGE
        
        filtered_products = []
        
        for product in products:
            discount = product.get('discount_percentage', 0)
            if discount >= min_discount:
                filtered_products.append(product)
        
        return filtered_products
    
    def filter_by_store(self, products, store_name):
        """Filtra productos por tienda"""
        return [p for p in products if p.get('store') == store_name]
    
    def filter_by_category(self, products, category):
        """Filtra productos por categoría"""
        return [p for p in products if p.get('category') == category]
    
    def sort_products(self, products, sort_by='discount_percentage', reverse=True):
        """Ordena productos por un criterio específico"""
        if sort_by == 'discount_percentage':
            return sorted(products, key=lambda x: x.get('discount_percentage', 0), reverse=reverse)
        elif sort_by == 'current_price':
            return sorted(products, key=lambda x: x.get('current_price', 0), reverse=reverse)
        elif sort_by == 'name':
            return sorted(products, key=lambda x: x.get('name', ''), reverse=reverse)
        else:
            return products
    
    def remove_duplicates(self, products):
        """Elimina productos duplicados"""
        seen = set()
        unique_products = []
        
        for product in products:
            # Crear clave única
            key = f"{product.get('store', '')}_{product.get('name', '')}_{product.get('current_price', 0)}"
            key = key.lower().replace(' ', '_')
            
            if key not in seen:
                seen.add(key)
                unique_products.append(product)
        
        return unique_products
    
    def get_statistics(self, products):
        """Obtiene estadísticas de los productos"""
        if not products:
            return {}
        
        stats = {
            'total_products': len(products),
            'stores': {},
            'categories': {},
            'discount_ranges': {
                '70-80%': 0,
                '80-90%': 0,
                '90%+': 0
            },
            'price_ranges': {
                '0-10000': 0,
                '10000-50000': 0,
                '50000+': 0
            }
        }
        
        for product in products:
            # Contar por tienda
            store = product.get('store', 'Unknown')
            stats['stores'][store] = stats['stores'].get(store, 0) + 1
            
            # Contar por categoría
            category = product.get('category', 'Unknown')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # Contar por rango de descuento
            discount = product.get('discount_percentage', 0)
            if 70 <= discount < 80:
                stats['discount_ranges']['70-80%'] += 1
            elif 80 <= discount < 90:
                stats['discount_ranges']['80-90%'] += 1
            elif discount >= 90:
                stats['discount_ranges']['90%+'] += 1
            
            # Contar por rango de precio
            price = product.get('current_price', 0)
            if price <= 10000:
                stats['price_ranges']['0-10000'] += 1
            elif price <= 50000:
                stats['price_ranges']['10000-50000'] += 1
            else:
                stats['price_ranges']['50000+'] += 1
        
        return stats
    
    def validate_product_url(self, url):
        """Valida que una URL de producto sea accesible"""
        try:
            response = self.helper.make_request(url)
            return response.status_code == 200
        except:
            return False
    
    def enrich_product_data(self, product):
        """Enriquece los datos del producto con información adicional"""
        enriched = product.copy()
        
        # Calcular ahorro en pesos
        if enriched.get('original_price') and enriched.get('current_price'):
            enriched['savings'] = enriched['original_price'] - enriched['current_price']
        
        # Agregar etiquetas
        enriched['tags'] = []
        
        discount = enriched.get('discount_percentage', 0)
        if discount >= 90:
            enriched['tags'].append('Mega Oferta')
        elif discount >= 80:
            enriched['tags'].append('Gran Descuento')
        elif discount >= 70:
            enriched['tags'].append('Oferta')
        
        # Agregar etiqueta de precio
        price = enriched.get('current_price', 0)
        if price <= 5000:
            enriched['tags'].append('Precio Bajo')
        elif price <= 20000:
            enriched['tags'].append('Precio Medio')
        else:
            enriched['tags'].append('Precio Alto')
        
        return enriched 