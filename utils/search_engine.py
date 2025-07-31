#!/usr/bin/env python3
"""
Motor de búsqueda inteligente para el sistema de scraping
Incluye búsqueda por palabra clave y comparación entre tiendas
"""

import re
from typing import List, Dict, Optional
from difflib import SequenceMatcher

class SearchEngine:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def search_products(self, query: str, store: Optional[str] = None, 
                       min_discount: int = 0, max_results: int = 50) -> List[Dict]:
        """Busca productos por palabra clave"""
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.lower().strip()
        
        # Obtener productos activos
        products = self.data_manager.get_active_products(store=store, limit=1000)
        
        if not products:
            return []
        
        # Filtrar y puntuar productos
        scored_products = []
        
        for product in products:
            score = self.calculate_search_score(product, query)
            
            if score > 0:
                # Verificar descuento mínimo
                if min_discount > 0:
                    discount_str = product.get('discount', '')
                    if discount_str:
                        try:
                            discount_value = int(discount_str.replace('%', '').replace('-', ''))
                            if discount_value < min_discount:
                                continue
                        except:
                            continue
                
                scored_products.append((score, product))
        
        # Ordenar por puntuación (mayor primero)
        scored_products.sort(key=lambda x: x[0], reverse=True)
        
        # Retornar solo los productos (sin puntuación)
        results = [product for score, product in scored_products[:max_results]]
        
        return results
    
    def calculate_search_score(self, product: Dict, query: str) -> float:
        """Calcula la puntuación de relevancia para un producto"""
        name = product.get('name', '').lower()
        store = product.get('store', '').lower()
        category = product.get('category', '').lower()
        
        score = 0.0
        
        # Búsqueda exacta en nombre (mayor puntuación)
        if query in name:
            score += 10.0
        
        # Búsqueda de palabras individuales
        query_words = query.split()
        for word in query_words:
            if len(word) >= 3:  # Solo palabras de 3+ caracteres
                if word in name:
                    score += 5.0
                elif word in store:
                    score += 2.0
                elif word in category:
                    score += 3.0
        
        # Coincidencia parcial usando SequenceMatcher
        name_similarity = SequenceMatcher(None, query, name).ratio()
        score += name_similarity * 3.0
        
        # Bonus por descuento alto
        discount_str = product.get('discount', '')
        if discount_str:
            try:
                discount_value = int(discount_str.replace('%', '').replace('-', ''))
                if discount_value >= 50:
                    score += 2.0
                elif discount_value >= 30:
                    score += 1.0
            except:
                pass
        
        return score
    
    def find_similar_products(self, product_name: str, exclude_store: Optional[str] = None) -> List[Dict]:
        """Encuentra productos similares en otras tiendas"""
        if not product_name:
            return []
        
        # Obtener todos los productos activos
        all_products = self.data_manager.get_active_products(limit=1000)
        
        if not all_products:
            return []
        
        # Filtrar productos similares
        similar_products = []
        product_name_lower = product_name.lower()
        
        for product in all_products:
            # Excluir productos de la misma tienda si se especifica
            if exclude_store and product.get('store') == exclude_store:
                continue
            
            # Calcular similitud
            similarity = self.calculate_product_similarity(product_name_lower, product.get('name', '').lower())
            
            if similarity > 0.3:  # Umbral de similitud
                similar_products.append((similarity, product))
        
        # Ordenar por similitud
        similar_products.sort(key=lambda x: x[0], reverse=True)
        
        # Retornar solo los productos (sin puntuación)
        results = [product for similarity, product in similar_products[:10]]
        
        return results
    
    def calculate_product_similarity(self, name1: str, name2: str) -> float:
        """Calcula la similitud entre dos nombres de productos"""
        if not name1 or not name2:
            return 0.0
        
        # Usar SequenceMatcher para similitud general
        general_similarity = SequenceMatcher(None, name1, name2).ratio()
        
        # Extraer palabras clave comunes
        words1 = set(re.findall(r'\b\w{3,}\b', name1.lower()))
        words2 = set(re.findall(r'\b\w{3,}\b', name2.lower()))
        
        if not words1 or not words2:
            return general_similarity
        
        # Calcular intersección de palabras
        common_words = words1.intersection(words2)
        word_similarity = len(common_words) / max(len(words1), len(words2))
        
        # Combinar similitudes
        combined_similarity = (general_similarity + word_similarity) / 2
        
        return combined_similarity
    
    def get_products_by_category(self, category: str, store: Optional[str] = None) -> List[Dict]:
        """Obtiene productos por categoría"""
        if not category:
            return []
        
        category_lower = category.lower()
        products = self.data_manager.get_active_products(store=store, limit=1000)
        
        if not products:
            return []
        
        filtered_products = []
        
        for product in products:
            product_category = product.get('category', '').lower()
            product_name = product.get('name', '').lower()
            
            # Buscar categoría en el campo category o en el nombre
            if (category_lower in product_category or 
                category_lower in product_name):
                filtered_products.append(product)
        
        return filtered_products
    
    def get_products_by_price_range(self, min_price: float, max_price: float, 
                                   store: Optional[str] = None) -> List[Dict]:
        """Obtiene productos por rango de precio"""
        products = self.data_manager.get_active_products(store=store, limit=1000)
        
        if not products:
            return []
        
        filtered_products = []
        
        for product in products:
            price_str = product.get('current_price', '')
            if price_str:
                try:
                    price_value = self.extract_price_value(price_str)
                    if min_price <= price_value <= max_price:
                        filtered_products.append(product)
                except:
                    continue
        
        return filtered_products
    
    def extract_price_value(self, price_str: str) -> float:
        """Extrae el valor numérico del precio"""
        try:
            if not price_str:
                return 0.0
            
            # Remover símbolos y convertir a número
            price_clean = price_str.replace('$', '').replace('.', '').replace(',', '')
            return float(price_clean)
        except:
            return 0.0
    
    def get_best_deals(self, limit: int = 10, min_discount: int = 20) -> List[Dict]:
        """Obtiene las mejores ofertas"""
        products = self.data_manager.get_products_by_discount_range(min_discount, 100)
        
        if not products:
            return []
        
        # Ordenar por porcentaje de descuento (mayor primero)
        sorted_products = sorted(products, 
                               key=lambda x: self.extract_discount_value(x.get('discount', '')),
                               reverse=True)
        
        return sorted_products[:limit]
    
    def extract_discount_value(self, discount_str: str) -> int:
        """Extrae el valor numérico del descuento"""
        try:
            if not discount_str:
                return 0
            
            # Remover símbolos y convertir a número
            discount_clean = discount_str.replace('%', '').replace('-', '')
            return int(discount_clean)
        except:
            return 0
    
    def get_store_comparison(self, product_keywords: List[str]) -> Dict[str, List[Dict]]:
        """Compara productos similares entre tiendas"""
        if not product_keywords:
            return {}
        
        # Obtener productos de todas las tiendas
        all_products = self.data_manager.get_active_products(limit=1000)
        
        if not all_products:
            return {}
        
        # Agrupar por tienda
        store_products = {}
        
        for product in all_products:
            store = product.get('store', '')
            if store not in store_products:
                store_products[store] = []
            
            # Verificar si el producto coincide con las palabras clave
            product_name = product.get('name', '').lower()
            matches = 0
            
            for keyword in product_keywords:
                if keyword.lower() in product_name:
                    matches += 1
            
            if matches > 0:
                # Agregar puntuación de coincidencia
                product['match_score'] = matches / len(product_keywords)
                store_products[store].append(product)
        
        # Ordenar productos por puntuación en cada tienda
        for store in store_products:
            store_products[store].sort(key=lambda x: x.get('match_score', 0), reverse=True)
            store_products[store] = store_products[store][:5]  # Top 5 por tienda
        
        return store_products 