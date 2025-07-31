#!/usr/bin/env python3
"""
Sistema de Análisis de Precios Inteligente
Detecta patrones, ofertas reales y precios históricos
"""

import re
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import json
import os

@dataclass
class PriceAnalysis:
    """Resultado del análisis de precios"""
    is_real_discount: bool
    confidence_score: float
    price_trend: str  # 'increasing', 'decreasing', 'stable'
    historical_low: bool
    competitor_analysis: Dict[str, float]
    recommendation: str
    risk_level: str  # 'low', 'medium', 'high'

class PriceAnalyzer:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        self.price_history_file = os.path.join(data_dir, "price_history.json")
        self.price_history = self._load_price_history()
        
        # Configuración de análisis
        self.min_discount_threshold = 0.15  # 15% mínimo para considerar descuento real
        self.price_fluctuation_threshold = 0.10  # 10% de fluctuación normal
        self.suspicious_patterns = [
            r'\$0\.01', r'\$1\.00', r'\$999\.99', r'\$1,999\.99',  # Precios sospechosos
            r'GRATIS', r'FREE', r'0\.00',  # Productos gratuitos
            r'\d{1,3}%', r'\d{1,3}% OFF'  # Descuentos extremos
        ]
    
    def _load_price_history(self) -> Dict[str, List[Dict]]:
        """Carga historial de precios"""
        try:
            if os.path.exists(self.price_history_file):
                with open(self.price_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Error cargando historial de precios: {e}")
        return {}
    
    def _save_price_history(self):
        """Guarda historial de precios"""
        try:
            with open(self.price_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.price_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error guardando historial de precios: {e}")
    
    def _generate_product_key(self, product_name: str, store: str) -> str:
        """Genera clave única para el producto"""
        return f"{store}_{product_name.lower().replace(' ', '_')[:50]}"
    
    def analyze_price(self, product: Dict, store: str) -> PriceAnalysis:
        """Analiza el precio de un producto"""
        product_name = product.get('name', '')
        current_price = self._extract_numeric_price(product.get('current_price', ''))
        original_price = self._extract_numeric_price(product.get('original_price', ''))
        discount_text = product.get('discount', '')
        
        # Verificar si es un descuento real
        is_real_discount = self._is_real_discount(current_price, original_price, discount_text)
        
        # Calcular score de confianza
        confidence_score = self._calculate_confidence_score(product, store)
        
        # Analizar tendencia de precios
        price_trend = self._analyze_price_trend(product_name, store, current_price)
        
        # Verificar si es precio histórico bajo
        historical_low = self._is_historical_low(product_name, store, current_price)
        
        # Análisis de competencia
        competitor_analysis = self._analyze_competition(product_name, current_price, store)
        
        # Generar recomendación
        recommendation = self._generate_recommendation(
            is_real_discount, confidence_score, price_trend, historical_low
        )
        
        # Evaluar nivel de riesgo
        risk_level = self._evaluate_risk_level(product, confidence_score)
        
        # Actualizar historial de precios
        self._update_price_history(product_name, store, current_price, original_price)
        
        return PriceAnalysis(
            is_real_discount=is_real_discount,
            confidence_score=confidence_score,
            price_trend=price_trend,
            historical_low=historical_low,
            competitor_analysis=competitor_analysis,
            recommendation=recommendation,
            risk_level=risk_level
        )
    
    def _extract_numeric_price(self, price_text: str) -> Optional[float]:
        """Extrae precio numérico del texto"""
        if not price_text:
            return None
        
        # Buscar números en el texto
        numbers = re.findall(r'[\d,]+\.?\d*', price_text.replace('$', '').replace(',', ''))
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass
        return None
    
    def _is_real_discount(self, current_price: float, original_price: float, discount_text: str) -> bool:
        """Verifica si el descuento es real"""
        if not current_price or not original_price:
            return False
        
        # Calcular descuento real
        real_discount = (original_price - current_price) / original_price
        
        # Verificar si supera el umbral mínimo
        if real_discount < self.min_discount_threshold:
            return False
        
        # Verificar patrones sospechosos
        for pattern in self.suspicious_patterns:
            if re.search(pattern, discount_text, re.IGNORECASE):
                return False
        
        # Verificar que el precio actual no sea muy bajo
        if current_price < original_price * 0.1:  # Menos del 10% del precio original
            return False
        
        return True
    
    def _calculate_confidence_score(self, product: Dict, store: str) -> float:
        """Calcula score de confianza del producto"""
        score = 0.5  # Score base
        
        # Verificar que tenga nombre
        if product.get('name'):
            score += 0.1
        
        # Verificar que tenga precios
        if product.get('current_price') and product.get('original_price'):
            score += 0.2
        
        # Verificar que tenga enlace
        if product.get('product_link'):
            score += 0.1
        
        # Verificar que tenga imagen
        if product.get('image'):
            score += 0.1
        
        # Verificar descuento razonable
        current_price = self._extract_numeric_price(product.get('current_price', ''))
        original_price = self._extract_numeric_price(product.get('original_price', ''))
        
        if current_price and original_price:
            discount = (original_price - current_price) / original_price
            if 0.1 <= discount <= 0.8:  # Descuento entre 10% y 80%
                score += 0.2
        
        return min(score, 1.0)
    
    def _analyze_price_trend(self, product_name: str, store: str, current_price: float) -> str:
        """Analiza la tendencia de precios"""
        key = self._generate_product_key(product_name, store)
        
        if key not in self.price_history:
            return 'stable'
        
        history = self.price_history[key]
        if len(history) < 3:
            return 'stable'
        
        # Obtener últimos 5 precios
        recent_prices = [item['current_price'] for item in history[-5:]]
        
        # Calcular tendencia
        if len(recent_prices) >= 2:
            trend = statistics.mean(recent_prices[1:]) - statistics.mean(recent_prices[:-1])
            
            if trend > self.price_fluctuation_threshold * statistics.mean(recent_prices):
                return 'increasing'
            elif trend < -self.price_fluctuation_threshold * statistics.mean(recent_prices):
                return 'decreasing'
        
        return 'stable'
    
    def _is_historical_low(self, product_name: str, store: str, current_price: float) -> bool:
        """Verifica si el precio actual es un mínimo histórico"""
        key = self._generate_product_key(product_name, store)
        
        if key not in self.price_history:
            return False
        
        history = self.price_history[key]
        if not history:
            return False
        
        # Obtener precio mínimo histórico
        historical_prices = [item['current_price'] for item in history]
        min_price = min(historical_prices)
        
        # Verificar si el precio actual está cerca del mínimo
        return current_price <= min_price * 1.05  # 5% de tolerancia
    
    def _analyze_competition(self, product_name: str, current_price: float, store: str) -> Dict[str, float]:
        """Analiza precios de competencia"""
        # Buscar productos similares en otras tiendas
        similar_products = []
        
        for store_key, store_history in self.price_history.items():
            if store not in store_key:  # Otra tienda
                for item in store_history:
                    if self._is_similar_product(product_name, item.get('name', '')):
                        similar_products.append(item['current_price'])
        
        if not similar_products:
            return {'average': current_price, 'min': current_price, 'max': current_price}
        
        return {
            'average': statistics.mean(similar_products),
            'min': min(similar_products),
            'max': max(similar_products),
            'count': len(similar_products)
        }
    
    def _is_similar_product(self, name1: str, name2: str) -> bool:
        """Verifica si dos productos son similares"""
        # Normalizar nombres
        name1_norm = re.sub(r'[^\w\s]', '', name1.lower())
        name2_norm = re.sub(r'[^\w\s]', '', name2.lower())
        
        # Buscar palabras clave comunes
        words1 = set(name1_norm.split())
        words2 = set(name2_norm.split())
        
        common_words = words1.intersection(words2)
        total_words = words1.union(words2)
        
        if not total_words:
            return False
        
        similarity = len(common_words) / len(total_words)
        return similarity > 0.3  # 30% de similitud
    
    def _generate_recommendation(self, is_real_discount: bool, confidence_score: float, 
                               price_trend: str, historical_low: bool) -> str:
        """Genera recomendación basada en el análisis"""
        if not is_real_discount:
            return "No es un descuento real"
        
        if confidence_score < 0.5:
            return "Información insuficiente para recomendar"
        
        if price_trend == 'decreasing' and historical_low:
            return "¡EXCELENTE OFERTA! Precio en tendencia bajista y mínimo histórico"
        elif price_trend == 'decreasing':
            return "Buena oferta - Precio en tendencia bajista"
        elif historical_low:
            return "Buena oferta - Precio mínimo histórico"
        elif price_trend == 'stable':
            return "Oferta regular - Precio estable"
        else:
            return "Oferta cuestionable - Precio en tendencia alcista"
    
    def _evaluate_risk_level(self, product: Dict, confidence_score: float) -> str:
        """Evalúa el nivel de riesgo del producto"""
        if confidence_score < 0.3:
            return 'high'
        elif confidence_score < 0.7:
            return 'medium'
        else:
            return 'low'
    
    def _update_price_history(self, product_name: str, store: str, current_price: float, original_price: float):
        """Actualiza el historial de precios"""
        key = self._generate_product_key(product_name, store)
        
        if key not in self.price_history:
            self.price_history[key] = []
        
        # Agregar entrada al historial
        entry = {
            'name': product_name,
            'store': store,
            'current_price': current_price,
            'original_price': original_price,
            'timestamp': datetime.now().isoformat()
        }
        
        self.price_history[key].append(entry)
        
        # Mantener solo últimos 20 registros
        if len(self.price_history[key]) > 20:
            self.price_history[key] = self.price_history[key][-20:]
        
        # Guardar historial
        self._save_price_history()
    
    def get_price_statistics(self, store: str = None) -> Dict[str, Any]:
        """Obtiene estadísticas de precios"""
        stats = {
            'total_products': 0,
            'average_discount': 0,
            'price_ranges': {'low': 0, 'medium': 0, 'high': 0},
            'trends': {'increasing': 0, 'decreasing': 0, 'stable': 0}
        }
        
        discounts = []
        
        for key, history in self.price_history.items():
            if store and store not in key:
                continue
            
            if history:
                latest = history[-1]
                stats['total_products'] += 1
                
                if latest.get('original_price') and latest.get('current_price'):
                    discount = (latest['original_price'] - latest['current_price']) / latest['original_price']
                    discounts.append(discount)
                
                # Clasificar por rango de precio
                price = latest.get('current_price', 0)
                if price < 10000:
                    stats['price_ranges']['low'] += 1
                elif price < 50000:
                    stats['price_ranges']['medium'] += 1
                else:
                    stats['price_ranges']['high'] += 1
        
        if discounts:
            stats['average_discount'] = statistics.mean(discounts) * 100
        
        return stats 