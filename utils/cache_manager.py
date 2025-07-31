#!/usr/bin/env python3
"""
Sistema de Cache Inteligente para DescuentosGO
Optimiza consultas y reduce tiempo de scraping
"""

import os
import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

class CacheManager:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "cache_data.pkl")
        self.metadata_file = os.path.join(cache_dir, "cache_metadata.json")
        
        # Crear directorio de cache si no existe
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # Cargar cache existente
        self.cache_data = self._load_cache()
        self.metadata = self._load_metadata()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Carga el cache desde archivo"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            self.logger.warning(f"Error cargando cache: {e}")
        return {}
    
    def _save_cache(self):
        """Guarda el cache en archivo"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache_data, f)
        except Exception as e:
            self.logger.error(f"Error guardando cache: {e}")
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Carga metadata del cache"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Error cargando metadata: {e}")
        return {"created": datetime.now().isoformat(), "hits": 0, "misses": 0}
    
    def _save_metadata(self):
        """Guarda metadata del cache"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error guardando metadata: {e}")
    
    def _generate_key(self, store: str, category: str, url: str) -> str:
        """Genera una clave única para el cache"""
        content = f"{store}:{category}:{url}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, store: str, category: str, url: str, max_age_hours: int = 1) -> Optional[List[Dict]]:
        """Obtiene datos del cache si no han expirado"""
        key = self._generate_key(store, category, url)
        
        if key in self.cache_data:
            cached_item = self.cache_data[key]
            cached_time = datetime.fromisoformat(cached_item['timestamp'])
            
            # Verificar si el cache no ha expirado
            if datetime.now() - cached_time < timedelta(hours=max_age_hours):
                self.metadata['hits'] += 1
                self._save_metadata()
                self.logger.info(f"✅ Cache hit para {store}/{category}")
                return cached_item['data']
            else:
                # Cache expirado, eliminarlo
                del self.cache_data[key]
                self.logger.info(f"⏰ Cache expirado para {store}/{category}")
        
        self.metadata['misses'] += 1
        self._save_metadata()
        self.logger.info(f"❌ Cache miss para {store}/{category}")
        return None
    
    def set(self, store: str, category: str, url: str, data: List[Dict]):
        """Guarda datos en el cache"""
        key = self._generate_key(store, category, url)
        
        self.cache_data[key] = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'store': store,
            'category': category,
            'url': url,
            'count': len(data)
        }
        
        self._save_cache()
        self.logger.info(f"💾 Cache guardado para {store}/{category} ({len(data)} productos)")
    
    def clear_expired(self, max_age_hours: int = 24):
        """Limpia entradas expiradas del cache"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, item in self.cache_data.items():
            cached_time = datetime.fromisoformat(item['timestamp'])
            if current_time - cached_time > timedelta(hours=max_age_hours):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache_data[key]
        
        if expired_keys:
            self._save_cache()
            self.logger.info(f"🧹 Cache limpiado: {len(expired_keys)} entradas expiradas")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        total_entries = len(self.cache_data)
        total_products = sum(item.get('count', 0) for item in self.cache_data.values())
        
        return {
            'total_entries': total_entries,
            'total_products': total_products,
            'hits': self.metadata.get('hits', 0),
            'misses': self.metadata.get('misses', 0),
            'hit_rate': self.metadata.get('hits', 0) / max(1, self.metadata.get('hits', 0) + self.metadata.get('misses', 0)) * 100,
            'created': self.metadata.get('created', 'Unknown'),
            'cache_size_mb': os.path.getsize(self.cache_file) / (1024 * 1024) if os.path.exists(self.cache_file) else 0
        }
    
    def clear_all(self):
        """Limpia todo el cache"""
        self.cache_data = {}
        self.metadata = {"created": datetime.now().isoformat(), "hits": 0, "misses": 0}
        self._save_cache()
        self._save_metadata()
        self.logger.info("🗑️ Cache completamente limpiado")
    
    def get_cached_stores(self) -> List[str]:
        """Obtiene lista de tiendas en cache"""
        stores = set()
        for item in self.cache_data.values():
            stores.add(item.get('store', ''))
        return list(stores)
    
    def get_cached_categories(self, store: str = None) -> List[str]:
        """Obtiene lista de categorías en cache"""
        categories = set()
        for item in self.cache_data.values():
            if store is None or item.get('store') == store:
                categories.add(item.get('category', ''))
        return list(categories) 