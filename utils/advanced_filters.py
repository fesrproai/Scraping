#!/usr/bin/env python3
"""
Sistema de Filtros Avanzados para DescuentosGO
Permite filtrar productos por múltiples criterios personalizables
"""

import re
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

@dataclass
class FilterCriteria:
    """Criterios de filtrado"""
    min_discount: float = 0.0
    max_discount: float = 100.0
    min_price: float = 0.0
    max_price: float = float('inf')
    stores: List[str] = None
    categories: List[str] = None
    keywords: List[str] = None
    exclude_keywords: List[str] = None
    min_confidence: float = 0.0
    risk_levels: List[str] = None
    price_trends: List[str] = None
    only_historical_lows: bool = False
    only_new_products: bool = False
    max_days_old: int = None

class AdvancedFilters:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Filtros predefinidos
        self.preset_filters = {
            'ofertas_extremas': FilterCriteria(
                min_discount=80.0,
                min_confidence=0.7,
                risk_levels=['low', 'medium']
            ),
            'ofertas_seguras': FilterCriteria(
                min_discount=50.0,
                max_discount=80.0,
                min_confidence=0.8,
                risk_levels=['low']
            ),
            'tecnologia': FilterCriteria(
                min_discount=30.0,
                keywords=['smartphone', 'laptop', 'tablet', 'pc', 'computador', 'celular'],
                categories=['tecnologia', 'tecnología']
            ),
            'hogar': FilterCriteria(
                min_discount=40.0,
                keywords=['mueble', 'decoracion', 'cocina', 'baño', 'jardin'],
                categories=['hogar', 'hogar-y-muebles', 'hogar-y-jardin']
            ),
            'ropa': FilterCriteria(
                min_discount=50.0,
                keywords=['camisa', 'pantalon', 'vestido', 'zapato', 'bolso'],
                categories=['ropa', 'ropa-y-accesorios', 'zapatos-y-bolsos']
            ),
            'nuevos_productos': FilterCriteria(
                only_new_products=True,
                max_days_old=7
            ),
            'precios_historicos': FilterCriteria(
                only_historical_lows=True,
                min_discount=30.0
            )
        }
    
    def apply_filters(self, products: List[Dict], criteria: FilterCriteria) -> List[Dict]:
        """Aplica filtros a la lista de productos"""
        filtered_products = []
        
        for product in products:
            if self._product_matches_criteria(product, criteria):
                filtered_products.append(product)
        
        self.logger.info(f"🔍 Filtros aplicados: {len(products)} → {len(filtered_products)} productos")
        return filtered_products
    
    def _product_matches_criteria(self, product: Dict, criteria: FilterCriteria) -> bool:
        """Verifica si un producto cumple con los criterios de filtrado"""
        
        # Filtro por descuento
        if not self._matches_discount_filter(product, criteria):
            return False
        
        # Filtro por precio
        if not self._matches_price_filter(product, criteria):
            return False
        
        # Filtro por tienda
        if not self._matches_store_filter(product, criteria):
            return False
        
        # Filtro por categoría
        if not self._matches_category_filter(product, criteria):
            return False
        
        # Filtro por palabras clave
        if not self._matches_keyword_filter(product, criteria):
            return False
        
        # Filtro por palabras excluidas
        if not self._matches_exclude_keyword_filter(product, criteria):
            return False
        
        # Filtro por confianza
        if not self._matches_confidence_filter(product, criteria):
            return False
        
        # Filtro por nivel de riesgo
        if not self._matches_risk_filter(product, criteria):
            return False
        
        # Filtro por tendencia de precio
        if not self._matches_trend_filter(product, criteria):
            return False
        
        # Filtro por precio histórico
        if criteria.only_historical_lows and not self._is_historical_low(product):
            return False
        
        # Filtro por productos nuevos
        if criteria.only_new_products and not self._is_new_product(product, criteria.max_days_old):
            return False
        
        return True
    
    def _matches_discount_filter(self, product: Dict, criteria: FilterCriteria) -> bool:
        """Verifica filtro de descuento"""
        discount = self._extract_discount_percentage(product)
        return criteria.min_discount <= discount <= criteria.max_discount
    
    def _matches_price_filter(self, product: Dict, criteria: FilterCriteria) -> bool:
        """Verifica filtro de precio"""
        current_price = self._extract_numeric_price(product.get('current_price', ''))
        if not current_price:
            return False
        
        return criteria.min_price <= current_price <= criteria.max_price
    
    def _matches_store_filter(self, product: Dict, criteria: FilterCriteria) -> bool:
        """Verifica filtro de tienda"""
        if not criteria.stores:
            return True
        
        product_store = product.get('store', '').lower()
        return any(store.lower() in product_store for store in criteria.stores)
    
    def _matches_category_filter(self, product: Dict, criteria: FilterCriteria) -> bool:
        """Verifica filtro de categoría"""
        if not criteria.categories:
            return True
        
        product_category = product.get('category', '').lower()
        return any(cat.lower() in product_category for cat in criteria.categories)
    
    def _matches_keyword_filter(self, product: Dict, criteria: FilterCriteria) -> bool:
        """Verifica filtro de palabras clave"""
        if not criteria.keywords:
            return True
        
        product_name = product.get('name', '').lower()
        return any(keyword.lower() in product_name for keyword in criteria.keywords)
    
    def _matches_exclude_keyword_filter(self, product: Dict, criteria: FilterCriteria) -> bool:
        """Verifica filtro de palabras excluidas"""
        if not criteria.exclude_keywords:
            return True
        
        product_name = product.get('name', '').lower()
        return not any(keyword.lower() in product_name for keyword in criteria.exclude_keywords)
    
    def _matches_confidence_filter(self, product: Dict, criteria: FilterCriteria) -> bool:
        """Verifica filtro de confianza"""
        confidence = product.get('confidence_score', 0.0)
        return confidence >= criteria.min_confidence
    
    def _matches_risk_filter(self, product: Dict, criteria: FilterCriteria) -> bool:
        """Verifica filtro de nivel de riesgo"""
        if not criteria.risk_levels:
            return True
        
        risk_level = product.get('risk_level', 'medium')
        return risk_level in criteria.risk_levels
    
    def _matches_trend_filter(self, product: Dict, criteria: FilterCriteria) -> bool:
        """Verifica filtro de tendencia de precio"""
        if not criteria.price_trends:
            return True
        
        trend = product.get('price_trend', 'stable')
        return trend in criteria.price_trends
    
    def _is_historical_low(self, product: Dict) -> bool:
        """Verifica si es precio histórico bajo"""
        return product.get('historical_low', False)
    
    def _is_new_product(self, product: Dict, max_days: int) -> bool:
        """Verifica si es un producto nuevo"""
        if not max_days:
            return True
        
        extraction_date = product.get('fecha_extraccion', '')
        if not extraction_date:
            return False
        
        try:
            extraction_datetime = datetime.fromisoformat(extraction_date.replace('Z', '+00:00'))
            days_old = (datetime.now() - extraction_datetime).days
            return days_old <= max_days
        except:
            return False
    
    def _extract_discount_percentage(self, product: Dict) -> float:
        """Extrae el porcentaje de descuento del producto"""
        discount_text = product.get('discount', '')
        if not discount_text:
            return 0.0
        
        # Buscar porcentaje en el texto
        match = re.search(r'(\d+)%', discount_text)
        if match:
            return float(match.group(1))
        
        # Calcular descuento desde precios
        current_price = self._extract_numeric_price(product.get('current_price', ''))
        original_price = self._extract_numeric_price(product.get('original_price', ''))
        
        if current_price and original_price and original_price > 0:
            return ((original_price - current_price) / original_price) * 100
        
        return 0.0
    
    def _extract_numeric_price(self, price_text: str) -> Optional[float]:
        """Extrae precio numérico del texto"""
        if not price_text:
            return None
        
        numbers = re.findall(r'[\d,]+\.?\d*', price_text.replace('$', '').replace(',', ''))
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass
        return None
    
    def get_preset_filter(self, preset_name: str) -> Optional[FilterCriteria]:
        """Obtiene un filtro predefinido"""
        return self.preset_filters.get(preset_name)
    
    def list_preset_filters(self) -> List[str]:
        """Lista todos los filtros predefinidos disponibles"""
        return list(self.preset_filters.keys())
    
    def create_custom_filter(self, **kwargs) -> FilterCriteria:
        """Crea un filtro personalizado"""
        return FilterCriteria(**kwargs)
    
    def combine_filters(self, *filters: FilterCriteria) -> FilterCriteria:
        """Combina múltiples filtros"""
        combined = FilterCriteria()
        
        for filter_criteria in filters:
            # Combinar descuentos (usar el más restrictivo)
            combined.min_discount = max(combined.min_discount, filter_criteria.min_discount)
            combined.max_discount = min(combined.max_discount, filter_criteria.max_discount)
            
            # Combinar precios (usar el más restrictivo)
            combined.min_price = max(combined.min_price, filter_criteria.min_price)
            combined.max_price = min(combined.max_price, filter_criteria.max_price)
            
            # Combinar tiendas (intersección)
            if filter_criteria.stores:
                if combined.stores is None:
                    combined.stores = filter_criteria.stores.copy()
                else:
                    combined.stores = list(set(combined.stores) & set(filter_criteria.stores))
            
            # Combinar categorías (intersección)
            if filter_criteria.categories:
                if combined.categories is None:
                    combined.categories = filter_criteria.categories.copy()
                else:
                    combined.categories = list(set(combined.categories) & set(filter_criteria.categories))
            
            # Combinar palabras clave (unión)
            if filter_criteria.keywords:
                if combined.keywords is None:
                    combined.keywords = filter_criteria.keywords.copy()
                else:
                    combined.keywords = list(set(combined.keywords) | set(filter_criteria.keywords))
            
            # Combinar palabras excluidas (unión)
            if filter_criteria.exclude_keywords:
                if combined.exclude_keywords is None:
                    combined.exclude_keywords = filter_criteria.exclude_keywords.copy()
                else:
                    combined.exclude_keywords = list(set(combined.exclude_keywords) | set(filter_criteria.exclude_keywords))
            
            # Usar la confianza más alta
            combined.min_confidence = max(combined.min_confidence, filter_criteria.min_confidence)
            
            # Combinar niveles de riesgo (intersección)
            if filter_criteria.risk_levels:
                if combined.risk_levels is None:
                    combined.risk_levels = filter_criteria.risk_levels.copy()
                else:
                    combined.risk_levels = list(set(combined.risk_levels) & set(filter_criteria.risk_levels))
            
            # Combinar tendencias (intersección)
            if filter_criteria.price_trends:
                if combined.price_trends is None:
                    combined.price_trends = filter_criteria.price_trends.copy()
                else:
                    combined.price_trends = list(set(combined.price_trends) & set(filter_criteria.price_trends))
            
            # Combinar flags booleanos (AND lógico)
            combined.only_historical_lows = combined.only_historical_lows or filter_criteria.only_historical_lows
            combined.only_new_products = combined.only_new_products or filter_criteria.only_new_products
            
            # Usar el máximo de días más restrictivo
            if filter_criteria.max_days_old:
                if combined.max_days_old is None:
                    combined.max_days_old = filter_criteria.max_days_old
                else:
                    combined.max_days_old = min(combined.max_days_old, filter_criteria.max_days_old)
        
        return combined
    
    def get_filter_stats(self, products: List[Dict], criteria: FilterCriteria) -> Dict[str, Any]:
        """Obtiene estadísticas de los filtros aplicados"""
        filtered_products = self.apply_filters(products, criteria)
        
        stats = {
            'total_products': len(products),
            'filtered_products': len(filtered_products),
            'filter_percentage': (len(filtered_products) / len(products) * 100) if products else 0,
            'average_discount': 0,
            'price_range': {'min': 0, 'max': 0, 'avg': 0},
            'store_distribution': {},
            'category_distribution': {},
            'risk_distribution': {}
        }
        
        if filtered_products:
            # Calcular descuento promedio
            discounts = [self._extract_discount_percentage(p) for p in filtered_products]
            stats['average_discount'] = sum(discounts) / len(discounts)
            
            # Calcular rango de precios
            prices = [self._extract_numeric_price(p.get('current_price', '')) for p in filtered_products]
            prices = [p for p in prices if p is not None]
            if prices:
                stats['price_range'] = {
                    'min': min(prices),
                    'max': max(prices),
                    'avg': sum(prices) / len(prices)
                }
            
            # Distribución por tienda
            for product in filtered_products:
                store = product.get('store', 'Unknown')
                stats['store_distribution'][store] = stats['store_distribution'].get(store, 0) + 1
            
            # Distribución por categoría
            for product in filtered_products:
                category = product.get('category', 'Unknown')
                stats['category_distribution'][category] = stats['category_distribution'].get(category, 0) + 1
            
            # Distribución por nivel de riesgo
            for product in filtered_products:
                risk = product.get('risk_level', 'unknown')
                stats['risk_distribution'][risk] = stats['risk_distribution'].get(risk, 0) + 1
        
        return stats 