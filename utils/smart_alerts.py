#!/usr/bin/env python3
"""
Sistema de Alertas Inteligentes para DescuentosGO
Detecta patrones, ofertas especiales y envía notificaciones personalizadas
"""

import re
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging
from collections import defaultdict

@dataclass
class AlertRule:
    """Regla de alerta personalizable"""
    name: str
    description: str
    conditions: Dict[str, Any]
    priority: str  # 'low', 'medium', 'high', 'critical'
    enabled: bool = True
    notification_channels: List[str] = None  # ['telegram', 'email', 'webhook']
    cooldown_hours: int = 24  # Tiempo entre alertas del mismo tipo

@dataclass
class Alert:
    """Alerta generada"""
    rule_name: str
    product: Dict
    message: str
    priority: str
    timestamp: datetime
    store: str
    category: str

class SmartAlerts:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        self.alerts_file = os.path.join(data_dir, "alerts_history.json")
        self.rules_file = os.path.join(data_dir, "alert_rules.json")
        
        # Cargar configuración
        self.alerts_history = self._load_alerts_history()
        self.alert_rules = self._load_alert_rules()
        
        # Configurar reglas por defecto
        self._setup_default_rules()
        
        # Callbacks para notificaciones
        self.notification_callbacks = {}
    
    def _load_alerts_history(self) -> List[Dict]:
        """Carga historial de alertas"""
        try:
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Error cargando historial de alertas: {e}")
        return []
    
    def _save_alerts_history(self):
        """Guarda historial de alertas"""
        try:
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(self.alerts_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error guardando historial de alertas: {e}")
    
    def _load_alert_rules(self) -> Dict[str, AlertRule]:
        """Carga reglas de alerta"""
        try:
            if os.path.exists(self.rules_file):
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                    return {name: AlertRule(**rule) for name, rule in rules_data.items()}
        except Exception as e:
            self.logger.warning(f"Error cargando reglas de alerta: {e}")
        return {}
    
    def _save_alert_rules(self):
        """Guarda reglas de alerta"""
        try:
            rules_data = {name: {
                'name': rule.name,
                'description': rule.description,
                'conditions': rule.conditions,
                'priority': rule.priority,
                'enabled': rule.enabled,
                'notification_channels': rule.notification_channels,
                'cooldown_hours': rule.cooldown_hours
            } for name, rule in self.alert_rules.items()}
            
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error guardando reglas de alerta: {e}")
    
    def _setup_default_rules(self):
        """Configura reglas de alerta por defecto"""
        if not self.alert_rules:
            self.alert_rules = {
                'ofertas_extremas': AlertRule(
                    name='Ofertas Extremas',
                    description='Productos con descuentos superiores al 85%',
                    conditions={
                        'min_discount': 85.0,
                        'min_confidence': 0.7,
                        'risk_levels': ['low', 'medium']
                    },
                    priority='critical',
                    notification_channels=['telegram'],
                    cooldown_hours=6
                ),
                'precios_historicos': AlertRule(
                    name='Precios Históricos',
                    description='Productos en su precio más bajo histórico',
                    conditions={
                        'historical_low': True,
                        'min_discount': 50.0
                    },
                    priority='high',
                    notification_channels=['telegram'],
                    cooldown_hours=12
                ),
                'nuevos_productos': AlertRule(
                    name='Nuevos Productos',
                    description='Productos nuevos con descuentos atractivos',
                    conditions={
                        'max_days_old': 3,
                        'min_discount': 40.0
                    },
                    priority='medium',
                    notification_channels=['telegram'],
                    cooldown_hours=24
                ),
                'tecnologia_barata': AlertRule(
                    name='Tecnología Barata',
                    description='Productos tecnológicos con precios muy bajos',
                    conditions={
                        'categories': ['tecnologia', 'tecnología'],
                        'max_price': 50000,
                        'min_discount': 60.0
                    },
                    priority='high',
                    notification_channels=['telegram'],
                    cooldown_hours=12
                ),
                'liquidacion_final': AlertRule(
                    name='Liquidación Final',
                    description='Productos en liquidación con descuentos masivos',
                    conditions={
                        'keywords': ['liquidacion', 'liquidación', 'final', 'outlet'],
                        'min_discount': 70.0
                    },
                    priority='critical',
                    notification_channels=['telegram'],
                    cooldown_hours=4
                ),
                'tendencias_bajistas': AlertRule(
                    name='Tendencias Bajistas',
                    description='Productos con precios en tendencia bajista',
                    conditions={
                        'price_trend': 'decreasing',
                        'min_discount': 30.0
                    },
                    priority='medium',
                    notification_channels=['telegram'],
                    cooldown_hours=24
                )
            }
            self._save_alert_rules()
    
    def analyze_products(self, products: List[Dict]) -> List[Alert]:
        """Analiza productos y genera alertas"""
        alerts = []
        
        for product in products:
            product_alerts = self._check_product_alerts(product)
            alerts.extend(product_alerts)
        
        # Filtrar alertas por cooldown
        filtered_alerts = self._filter_alerts_by_cooldown(alerts)
        
        # Guardar alertas en historial
        for alert in filtered_alerts:
            self._save_alert_to_history(alert)
        
        self.logger.info(f"🚨 {len(filtered_alerts)} alertas generadas de {len(alerts)} posibles")
        return filtered_alerts
    
    def _check_product_alerts(self, product: Dict) -> List[Alert]:
        """Verifica si un producto activa alguna alerta"""
        alerts = []
        
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            if self._product_matches_rule(product, rule):
                alert = self._create_alert(product, rule)
                alerts.append(alert)
        
        return alerts
    
    def _product_matches_rule(self, product: Dict, rule: AlertRule) -> bool:
        """Verifica si un producto cumple con una regla de alerta"""
        conditions = rule.conditions
        
        # Verificar descuento mínimo
        if 'min_discount' in conditions:
            discount = self._extract_discount_percentage(product)
            if discount < conditions['min_discount']:
                return False
        
        # Verificar descuento máximo
        if 'max_discount' in conditions:
            discount = self._extract_discount_percentage(product)
            if discount > conditions['max_discount']:
                return False
        
        # Verificar precio mínimo
        if 'min_price' in conditions:
            current_price = self._extract_numeric_price(product.get('current_price', ''))
            if not current_price or current_price < conditions['min_price']:
                return False
        
        # Verificar precio máximo
        if 'max_price' in conditions:
            current_price = self._extract_numeric_price(product.get('current_price', ''))
            if not current_price or current_price > conditions['max_price']:
                return False
        
        # Verificar confianza mínima
        if 'min_confidence' in conditions:
            confidence = product.get('confidence_score', 0.0)
            if confidence < conditions['min_confidence']:
                return False
        
        # Verificar niveles de riesgo
        if 'risk_levels' in conditions:
            risk_level = product.get('risk_level', 'medium')
            if risk_level not in conditions['risk_levels']:
                return False
        
        # Verificar tendencia de precio
        if 'price_trend' in conditions:
            trend = product.get('price_trend', 'stable')
            if trend != conditions['price_trend']:
                return False
        
        # Verificar precio histórico
        if conditions.get('historical_low', False):
            if not product.get('historical_low', False):
                return False
        
        # Verificar días de antigüedad
        if 'max_days_old' in conditions:
            if not self._is_recent_product(product, conditions['max_days_old']):
                return False
        
        # Verificar categorías
        if 'categories' in conditions:
            product_category = product.get('category', '').lower()
            if not any(cat.lower() in product_category for cat in conditions['categories']):
                return False
        
        # Verificar palabras clave
        if 'keywords' in conditions:
            product_name = product.get('name', '').lower()
            if not any(keyword.lower() in product_name for keyword in conditions['keywords']):
                return False
        
        # Verificar tiendas
        if 'stores' in conditions:
            product_store = product.get('store', '').lower()
            if not any(store.lower() in product_store for store in conditions['stores']):
                return False
        
        return True
    
    def _create_alert(self, product: Dict, rule: AlertRule) -> Alert:
        """Crea una alerta basada en una regla y producto"""
        message = self._generate_alert_message(product, rule)
        
        return Alert(
            rule_name=rule.name,
            product=product,
            message=message,
            priority=rule.priority,
            timestamp=datetime.now(),
            store=product.get('store', 'Unknown'),
            category=product.get('category', 'Unknown')
        )
    
    def _generate_alert_message(self, product: Dict, rule: AlertRule) -> str:
        """Genera mensaje personalizado para la alerta"""
        product_name = product.get('name', 'Producto sin nombre')
        current_price = product.get('current_price', 'Precio no disponible')
        original_price = product.get('original_price', '')
        discount = self._extract_discount_percentage(product)
        store = product.get('store', 'Tienda desconocida')
        
        # Emojis según prioridad
        priority_emojis = {
            'low': '🔵',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }
        
        emoji = priority_emojis.get(rule.priority, '🔵')
        
        message = f"{emoji} **{rule.name}**\n\n"
        message += f"🏪 **Tienda:** {store}\n"
        message += f"📦 **Producto:** {product_name}\n"
        message += f"💰 **Precio:** {current_price}"
        
        if original_price:
            message += f" (antes {original_price})\n"
        else:
            message += "\n"
        
        message += f"🏷️ **Descuento:** {discount:.1f}%\n"
        
        # Agregar información adicional según el tipo de alerta
        if product.get('historical_low'):
            message += "📉 **¡Precio histórico bajo!**\n"
        
        if product.get('price_trend') == 'decreasing':
            message += "📊 **Precio en tendencia bajista**\n"
        
        if product.get('confidence_score', 0) > 0.8:
            message += "✅ **Alta confianza**\n"
        
        # Agregar enlace si está disponible
        if product.get('product_link'):
            message += f"\n🔗 [Ver producto]({product['product_link']})"
        
        return message
    
    def _filter_alerts_by_cooldown(self, alerts: List[Alert]) -> List[Alert]:
        """Filtra alertas por tiempo de cooldown"""
        filtered_alerts = []
        
        for alert in alerts:
            rule = self.alert_rules.get(alert.rule_name)
            if not rule:
                continue
            
            # Verificar si ha pasado suficiente tiempo desde la última alerta similar
            if self._can_send_alert(alert.rule_name, rule.cooldown_hours):
                filtered_alerts.append(alert)
        
        return filtered_alerts
    
    def _can_send_alert(self, rule_name: str, cooldown_hours: int) -> bool:
        """Verifica si se puede enviar una alerta basada en el cooldown"""
        # Buscar la última alerta de esta regla
        for alert_data in reversed(self.alerts_history):
            if alert_data.get('rule_name') == rule_name:
                last_alert_time = datetime.fromisoformat(alert_data['timestamp'])
                time_diff = datetime.now() - last_alert_time
                return time_diff.total_seconds() > cooldown_hours * 3600
        
        return True  # No hay alertas previas, se puede enviar
    
    def _save_alert_to_history(self, alert: Alert):
        """Guarda alerta en el historial"""
        alert_data = {
            'rule_name': alert.rule_name,
            'product_name': alert.product.get('name', ''),
            'store': alert.store,
            'category': alert.category,
            'priority': alert.priority,
            'timestamp': alert.timestamp.isoformat(),
            'message': alert.message
        }
        
        self.alerts_history.append(alert_data)
        
        # Mantener solo últimos 1000 alertas
        if len(self.alerts_history) > 1000:
            self.alerts_history = self.alerts_history[-1000:]
        
        self._save_alerts_history()
    
    def register_notification_callback(self, channel: str, callback: Callable):
        """Registra callback para notificaciones"""
        self.notification_callbacks[channel] = callback
    
    def send_notifications(self, alerts: List[Alert]):
        """Envía notificaciones para las alertas"""
        for alert in alerts:
            rule = self.alert_rules.get(alert.rule_name)
            if not rule or not rule.notification_channels:
                continue
            
            for channel in rule.notification_channels:
                callback = self.notification_callbacks.get(channel)
                if callback:
                    try:
                        callback(alert)
                        self.logger.info(f"📤 Notificación enviada por {channel}: {alert.rule_name}")
                    except Exception as e:
                        self.logger.error(f"❌ Error enviando notificación por {channel}: {e}")
    
    def add_alert_rule(self, rule: AlertRule):
        """Agrega una nueva regla de alerta"""
        self.alert_rules[rule.name] = rule
        self._save_alert_rules()
        self.logger.info(f"✅ Nueva regla de alerta agregada: {rule.name}")
    
    def remove_alert_rule(self, rule_name: str):
        """Elimina una regla de alerta"""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            self._save_alert_rules()
            self.logger.info(f"🗑️ Regla de alerta eliminada: {rule_name}")
    
    def enable_alert_rule(self, rule_name: str):
        """Habilita una regla de alerta"""
        if rule_name in self.alert_rules:
            self.alert_rules[rule_name].enabled = True
            self._save_alert_rules()
            self.logger.info(f"✅ Regla de alerta habilitada: {rule_name}")
    
    def disable_alert_rule(self, rule_name: str):
        """Deshabilita una regla de alerta"""
        if rule_name in self.alert_rules:
            self.alert_rules[rule_name].enabled = False
            self._save_alert_rules()
            self.logger.info(f"❌ Regla de alerta deshabilitada: {rule_name}")
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de alertas"""
        stats = {
            'total_alerts': len(self.alerts_history),
            'alerts_by_priority': defaultdict(int),
            'alerts_by_rule': defaultdict(int),
            'alerts_by_store': defaultdict(int),
            'recent_alerts': 0
        }
        
        # Contar alertas por prioridad y regla
        for alert_data in self.alerts_history:
            stats['alerts_by_priority'][alert_data['priority']] += 1
            stats['alerts_by_rule'][alert_data['rule_name']] += 1
            stats['alerts_by_store'][alert_data['store']] += 1
        
        # Contar alertas recientes (últimas 24 horas)
        recent_time = datetime.now() - timedelta(hours=24)
        for alert_data in self.alerts_history:
            alert_time = datetime.fromisoformat(alert_data['timestamp'])
            if alert_time > recent_time:
                stats['recent_alerts'] += 1
        
        return dict(stats)
    
    def _extract_discount_percentage(self, product: Dict) -> float:
        """Extrae el porcentaje de descuento del producto"""
        discount_text = product.get('discount', '')
        if not discount_text:
            return 0.0
        
        match = re.search(r'(\d+)%', discount_text)
        if match:
            return float(match.group(1))
        
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
    
    def _is_recent_product(self, product: Dict, max_days: int) -> bool:
        """Verifica si es un producto reciente"""
        extraction_date = product.get('fecha_extraccion', '')
        if not extraction_date:
            return False
        
        try:
            extraction_datetime = datetime.fromisoformat(extraction_date.replace('Z', '+00:00'))
            days_old = (datetime.now() - extraction_datetime).days
            return days_old <= max_days
        except:
            return False 