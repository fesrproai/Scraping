#!/usr/bin/env python3
"""
Sistema de Machine Learning para Predicción de Precios
Predice precios futuros y tendencias basado en datos históricos
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
import os
import logging
from dataclasses import dataclass
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle
import warnings
warnings.filterwarnings('ignore')

@dataclass
class PricePrediction:
    """Resultado de predicción de precio"""
    predicted_price: float
    confidence: float
    trend: str  # 'increasing', 'decreasing', 'stable'
    next_week_price: float
    next_month_price: float
    volatility: float
    recommendation: str
    factors: Dict[str, float]

class PricePredictor:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        self.models_dir = os.path.join(data_dir, "ml_models")
        self.price_history_file = os.path.join(data_dir, "price_history.json")
        
        # Crear directorio de modelos si no existe
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
        
        # Cargar datos históricos
        self.price_history = self._load_price_history()
        
        # Modelos de ML
        self.models = {}
        self.scalers = {}
        
        # Configuración
        self.min_data_points = 10
        self.prediction_horizon = 30  # días
        self.confidence_threshold = 0.6
        
        # Cargar modelos entrenados
        self._load_trained_models()
    
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
    
    def _load_trained_models(self):
        """Carga modelos entrenados"""
        try:
            # Cargar modelo de regresión lineal
            linear_model_path = os.path.join(self.models_dir, "linear_model.pkl")
            if os.path.exists(linear_model_path):
                with open(linear_model_path, 'rb') as f:
                    self.models['linear'] = pickle.load(f)
            
            # Cargar modelo de Random Forest
            rf_model_path = os.path.join(self.models_dir, "random_forest_model.pkl")
            if os.path.exists(rf_model_path):
                with open(rf_model_path, 'rb') as f:
                    self.models['random_forest'] = pickle.load(f)
            
            # Cargar scalers
            scaler_path = os.path.join(self.models_dir, "scaler.pkl")
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scalers['standard'] = pickle.load(f)
                    
        except Exception as e:
            self.logger.warning(f"Error cargando modelos entrenados: {e}")
    
    def _save_trained_models(self):
        """Guarda modelos entrenados"""
        try:
            # Guardar modelo de regresión lineal
            if 'linear' in self.models:
                with open(os.path.join(self.models_dir, "linear_model.pkl"), 'wb') as f:
                    pickle.dump(self.models['linear'], f)
            
            # Guardar modelo de Random Forest
            if 'random_forest' in self.models:
                with open(os.path.join(self.models_dir, "random_forest_model.pkl"), 'wb') as f:
                    pickle.dump(self.models['random_forest'], f)
            
            # Guardar scaler
            if 'standard' in self.scalers:
                with open(os.path.join(self.models_dir, "scaler.pkl"), 'wb') as f:
                    pickle.dump(self.scalers['standard'], f)
                    
        except Exception as e:
            self.logger.error(f"Error guardando modelos entrenados: {e}")
    
    def _generate_product_key(self, product_name: str, store: str) -> str:
        """Genera clave única para el producto"""
        return f"{store}_{product_name.lower().replace(' ', '_')[:50]}"
    
    def _prepare_features(self, price_history: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara características para el modelo de ML"""
        if len(price_history) < self.min_data_points:
            return None, None
        
        # Convertir a DataFrame
        df = pd.DataFrame(price_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Crear características
        features = []
        targets = []
        
        for i in range(len(df) - 1):
            # Características de precio
            current_price = df.iloc[i]['current_price']
            original_price = df.iloc[i]['original_price']
            
            # Características de tiempo
            day_of_week = df.iloc[i]['timestamp'].dayofweek
            day_of_month = df.iloc[i]['timestamp'].day
            month = df.iloc[i]['timestamp'].month
            
            # Características de tendencia
            if i > 0:
                price_change = (current_price - df.iloc[i-1]['current_price']) / df.iloc[i-1]['current_price']
                price_volatility = np.std([p['current_price'] for p in price_history[max(0, i-5):i+1]])
            else:
                price_change = 0
                price_volatility = 0
            
            # Características de descuento
            discount = (original_price - current_price) / original_price if original_price > 0 else 0
            
            # Características de movimiento de precio
            price_moving_avg_3 = np.mean([p['current_price'] for p in price_history[max(0, i-2):i+1]])
            price_moving_avg_7 = np.mean([p['current_price'] for p in price_history[max(0, i-6):i+1]])
            
            # Vector de características
            feature_vector = [
                current_price,
                original_price,
                discount,
                day_of_week,
                day_of_month,
                month,
                price_change,
                price_volatility,
                price_moving_avg_3,
                price_moving_avg_7
            ]
            
            features.append(feature_vector)
            targets.append(df.iloc[i+1]['current_price'])
        
        return np.array(features), np.array(targets)
    
    def train_models(self, force_retrain: bool = False):
        """Entrena los modelos de ML"""
        if not self.price_history:
            self.logger.warning("No hay datos históricos para entrenar modelos")
            return
        
        # Preparar datos de entrenamiento
        all_features = []
        all_targets = []
        
        for key, history in self.price_history.items():
            features, targets = self._prepare_features(history)
            if features is not None and targets is not None:
                all_features.append(features)
                all_targets.append(targets)
        
        if not all_features:
            self.logger.warning("No hay suficientes datos para entrenar modelos")
            return
        
        # Combinar todos los datos
        X = np.vstack(all_features)
        y = np.concatenate(all_targets)
        
        # Dividir en train/test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Escalar características
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers['standard'] = scaler
        
        # Entrenar modelo de regresión lineal
        linear_model = LinearRegression()
        linear_model.fit(X_train_scaled, y_train)
        
        # Evaluar modelo lineal
        y_pred_linear = linear_model.predict(X_test_scaled)
        mae_linear = mean_absolute_error(y_test, y_pred_linear)
        r2_linear = r2_score(y_test, y_pred_linear)
        
        self.models['linear'] = linear_model
        
        # Entrenar modelo de Random Forest
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train_scaled, y_train)
        
        # Evaluar modelo RF
        y_pred_rf = rf_model.predict(X_test_scaled)
        mae_rf = mean_absolute_error(y_test, y_pred_rf)
        r2_rf = r2_score(y_test, y_pred_rf)
        
        self.models['random_forest'] = rf_model
        
        # Guardar modelos
        self._save_trained_models()
        
        self.logger.info(f"✅ Modelos entrenados - Linear MAE: {mae_linear:.2f}, R²: {r2_linear:.3f}")
        self.logger.info(f"✅ Random Forest MAE: {mae_rf:.2f}, R²: {r2_rf:.3f}")
    
    def predict_price(self, product: Dict, store: str) -> Optional[PricePrediction]:
        """Predice el precio futuro de un producto"""
        product_name = product.get('name', '')
        key = self._generate_product_key(product_name, store)
        
        if key not in self.price_history:
            return None
        
        history = self.price_history[key]
        if len(history) < self.min_data_points:
            return None
        
        # Preparar características del producto actual
        current_price = self._extract_numeric_price(product.get('current_price', ''))
        original_price = self._extract_numeric_price(product.get('original_price', ''))
        
        if not current_price or not original_price:
            return None
        
        # Crear vector de características
        feature_vector = self._create_feature_vector(product, history)
        
        if feature_vector is None:
            return None
        
        # Escalar características
        if 'standard' not in self.scalers:
            return None
        
        feature_scaled = self.scalers['standard'].transform([feature_vector])
        
        # Hacer predicciones
        predictions = {}
        for model_name, model in self.models.items():
            try:
                pred = model.predict(feature_scaled)[0]
                predictions[model_name] = max(0, pred)  # Precio no puede ser negativo
            except Exception as e:
                self.logger.error(f"Error en predicción con {model_name}: {e}")
        
        if not predictions:
            return None
        
        # Calcular predicción promedio
        predicted_price = np.mean(list(predictions.values()))
        
        # Calcular confianza basada en la consistencia de los modelos
        confidence = self._calculate_prediction_confidence(predictions, current_price)
        
        # Determinar tendencia
        trend = self._determine_trend(predicted_price, current_price)
        
        # Predicciones a diferentes plazos
        next_week_price = self._predict_future_price(predicted_price, current_price, 7)
        next_month_price = self._predict_future_price(predicted_price, current_price, 30)
        
        # Calcular volatilidad
        volatility = self._calculate_volatility(history)
        
        # Generar recomendación
        recommendation = self._generate_prediction_recommendation(
            predicted_price, current_price, confidence, trend
        )
        
        # Factores que influyen en la predicción
        factors = self._analyze_prediction_factors(feature_vector)
        
        return PricePrediction(
            predicted_price=predicted_price,
            confidence=confidence,
            trend=trend,
            next_week_price=next_week_price,
            next_month_price=next_month_price,
            volatility=volatility,
            recommendation=recommendation,
            factors=factors
        )
    
    def _create_feature_vector(self, product: Dict, history: List[Dict]) -> Optional[np.ndarray]:
        """Crea vector de características para predicción"""
        try:
            current_price = self._extract_numeric_price(product.get('current_price', ''))
            original_price = self._extract_numeric_price(product.get('original_price', ''))
            
            if not current_price or not original_price:
                return None
            
            # Características de tiempo
            now = datetime.now()
            day_of_week = now.weekday()
            day_of_month = now.day
            month = now.month
            
            # Características de precio
            discount = (original_price - current_price) / original_price if original_price > 0 else 0
            
            # Características de tendencia
            if len(history) > 1:
                prev_price = history[-2]['current_price']
                price_change = (current_price - prev_price) / prev_price
                price_volatility = np.std([p['current_price'] for p in history[-5:]])
            else:
                price_change = 0
                price_volatility = 0
            
            # Promedios móviles
            price_moving_avg_3 = np.mean([p['current_price'] for p in history[-3:]])
            price_moving_avg_7 = np.mean([p['current_price'] for p in history[-7:]])
            
            return np.array([
                current_price,
                original_price,
                discount,
                day_of_week,
                day_of_month,
                month,
                price_change,
                price_volatility,
                price_moving_avg_3,
                price_moving_avg_7
            ])
            
        except Exception as e:
            self.logger.error(f"Error creando vector de características: {e}")
            return None
    
    def _calculate_prediction_confidence(self, predictions: Dict[str, float], current_price: float) -> float:
        """Calcula la confianza de la predicción"""
        if not predictions:
            return 0.0
        
        # Calcular variabilidad entre modelos
        pred_values = list(predictions.values())
        std_dev = np.std(pred_values)
        mean_pred = np.mean(pred_values)
        
        # Confianza basada en consistencia
        if mean_pred > 0:
            cv = std_dev / mean_pred  # Coeficiente de variación
            confidence = max(0.1, 1.0 - cv)
        else:
            confidence = 0.1
        
        # Ajustar confianza basada en la diferencia con precio actual
        price_diff_ratio = abs(mean_pred - current_price) / current_price
        if price_diff_ratio > 0.5:  # Predicción muy diferente al precio actual
            confidence *= 0.8
        
        return min(confidence, 1.0)
    
    def _determine_trend(self, predicted_price: float, current_price: float) -> str:
        """Determina la tendencia de precio"""
        if predicted_price > current_price * 1.05:
            return 'increasing'
        elif predicted_price < current_price * 0.95:
            return 'decreasing'
        else:
            return 'stable'
    
    def _predict_future_price(self, predicted_price: float, current_price: float, days: int) -> float:
        """Predice precio futuro basado en tendencia"""
        trend_factor = (predicted_price - current_price) / current_price
        daily_change = trend_factor / 30  # Asumir cambio lineal en 30 días
        
        future_price = current_price * (1 + daily_change * days)
        return max(0, future_price)
    
    def _calculate_volatility(self, history: List[Dict]) -> float:
        """Calcula la volatilidad del precio"""
        if len(history) < 2:
            return 0.0
        
        prices = [p['current_price'] for p in history]
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        return np.std(returns) if returns else 0.0
    
    def _generate_prediction_recommendation(self, predicted_price: float, current_price: float, 
                                          confidence: float, trend: str) -> str:
        """Genera recomendación basada en la predicción"""
        if confidence < self.confidence_threshold:
            return "Predicción de baja confianza - datos insuficientes"
        
        price_change_pct = ((predicted_price - current_price) / current_price) * 100
        
        if trend == 'increasing' and price_change_pct > 10:
            return f"¡COMPRAR AHORA! Precio subirá {price_change_pct:.1f}% en 30 días"
        elif trend == 'decreasing' and price_change_pct < -10:
            return f"ESPERAR - Precio bajará {abs(price_change_pct):.1f}% en 30 días"
        elif trend == 'stable':
            return "Precio estable - comprar cuando sea conveniente"
        else:
            return f"Cambio moderado ({price_change_pct:.1f}%) - evaluar según necesidad"
    
    def _analyze_prediction_factors(self, feature_vector: np.ndarray) -> Dict[str, float]:
        """Analiza factores que influyen en la predicción"""
        factor_names = [
            'precio_actual', 'precio_original', 'descuento', 'dia_semana',
            'dia_mes', 'mes', 'cambio_precio', 'volatilidad',
            'promedio_3dias', 'promedio_7dias'
        ]
        
        factors = {}
        for i, name in enumerate(factor_names):
            if i < len(feature_vector):
                factors[name] = float(feature_vector[i])
        
        return factors
    
    def _extract_numeric_price(self, price_text: str) -> Optional[float]:
        """Extrae precio numérico del texto"""
        if not price_text:
            return None
        
        import re
        numbers = re.findall(r'[\d,]+\.?\d*', price_text.replace('$', '').replace(',', ''))
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass
        return None
    
    def update_price_history(self, product: Dict, store: str):
        """Actualiza el historial de precios con nuevos datos"""
        product_name = product.get('name', '')
        key = self._generate_product_key(product_name, store)
        
        current_price = self._extract_numeric_price(product.get('current_price', ''))
        original_price = self._extract_numeric_price(product.get('original_price', ''))
        
        if not current_price or not original_price:
            return
        
        if key not in self.price_history:
            self.price_history[key] = []
        
        # Agregar nueva entrada
        entry = {
            'name': product_name,
            'store': store,
            'current_price': current_price,
            'original_price': original_price,
            'timestamp': datetime.now().isoformat()
        }
        
        self.price_history[key].append(entry)
        
        # Mantener solo últimos 50 registros
        if len(self.price_history[key]) > 50:
            self.price_history[key] = self.price_history[key][-50:]
        
        self._save_price_history()
    
    def get_prediction_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de predicciones"""
        stats = {
            'total_products': len(self.price_history),
            'products_with_sufficient_data': 0,
            'average_confidence': 0.0,
            'trend_distribution': {'increasing': 0, 'decreasing': 0, 'stable': 0},
            'model_performance': {}
        }
        
        confidences = []
        trends = []
        
        for key, history in self.price_history.items():
            if len(history) >= self.min_data_points:
                stats['products_with_sufficient_data'] += 1
                
                # Simular predicción para estadísticas
                if history:
                    latest = history[-1]
                    product = {
                        'name': latest.get('name', ''),
                        'current_price': str(latest.get('current_price', '')),
                        'original_price': str(latest.get('original_price', ''))
                    }
                    
                    prediction = self.predict_price(product, latest.get('store', ''))
                    if prediction:
                        confidences.append(prediction.confidence)
                        trends.append(prediction.trend)
        
        if confidences:
            stats['average_confidence'] = np.mean(confidences)
        
        for trend in trends:
            stats['trend_distribution'][trend] += 1
        
        return stats 