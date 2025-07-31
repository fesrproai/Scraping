import time
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class ScrapingMonitor:
    def __init__(self):
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_products_found': 0,
            'high_discount_products': 0,
            'store_stats': defaultdict(dict),
            'error_log': [],
            'performance_metrics': {}
        }
        self.request_times = []
        self.error_counts = Counter()
    
    def start_session(self):
        """Inicia una sesión de monitoreo"""
        self.stats['start_time'] = datetime.now()
        logger.info("🚀 Iniciando sesión de monitoreo")
    
    def end_session(self):
        """Finaliza la sesión de monitoreo"""
        self.stats['end_time'] = datetime.now()
        duration = self.stats['end_time'] - self.stats['start_time']
        self.stats['performance_metrics']['total_duration'] = str(duration)
        
        if self.request_times:
            avg_response_time = sum(self.request_times) / len(self.request_times)
            self.stats['performance_metrics']['avg_response_time'] = f"{avg_response_time:.2f}s"
        
        logger.info(f"✅ Sesión finalizada en {duration}")
        return self.generate_report()
    
    def log_request(self, url, success=True, response_time=None, error=None):
        """Registra una petición HTTP"""
        self.stats['total_requests'] += 1
        
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
            if error:
                self.error_counts[error] += 1
                self.stats['error_log'].append({
                    'timestamp': datetime.now().isoformat(),
                    'url': url,
                    'error': str(error)
                })
        
        if response_time:
            self.request_times.append(response_time)
    
    def log_store_scraping(self, store_name, category, products_found, high_discount_count, errors=None):
        """Registra estadísticas de scraping por tienda"""
        if store_name not in self.stats['store_stats']:
            self.stats['store_stats'][store_name] = {
                'total_products': 0,
                'high_discount_products': 0,
                'categories_scraped': [],
                'errors': []
            }
        
        store_stat = self.stats['store_stats'][store_name]
        store_stat['total_products'] += products_found
        store_stat['high_discount_products'] += high_discount_count
        
        if category not in store_stat['categories_scraped']:
            store_stat['categories_scraped'].append(category)
        
        if errors:
            store_stat['errors'].extend(errors)
        
        self.stats['total_products_found'] += products_found
        self.stats['high_discount_products'] += high_discount_count
        
        logger.info(f"📊 {store_name} - {category}: {products_found} productos, {high_discount_count} con alto descuento")
    
    def get_success_rate(self):
        """Calcula la tasa de éxito de las peticiones"""
        if self.stats['total_requests'] == 0:
            return 0
        return (self.stats['successful_requests'] / self.stats['total_requests']) * 100
    
    def get_most_common_errors(self, limit=5):
        """Obtiene los errores más comunes"""
        return self.error_counts.most_common(limit)
    
    def generate_report(self):
        """Genera un reporte completo de la sesión"""
        report = {
            'session_info': {
                'start_time': self.stats['start_time'].isoformat() if self.stats['start_time'] else None,
                'end_time': self.stats['end_time'].isoformat() if self.stats['end_time'] else None,
                'duration': self.stats['performance_metrics'].get('total_duration', 'N/A')
            },
            'request_stats': {
                'total_requests': self.stats['total_requests'],
                'successful_requests': self.stats['successful_requests'],
                'failed_requests': self.stats['failed_requests'],
                'success_rate': f"{self.get_success_rate():.2f}%",
                'avg_response_time': self.stats['performance_metrics'].get('avg_response_time', 'N/A')
            },
            'product_stats': {
                'total_products_found': self.stats['total_products_found'],
                'high_discount_products': self.stats['high_discount_products'],
                'high_discount_percentage': f"{(self.stats['high_discount_products'] / max(self.stats['total_products_found'], 1)) * 100:.2f}%"
            },
            'store_performance': {},
            'error_summary': {
                'total_errors': len(self.stats['error_log']),
                'most_common_errors': self.get_most_common_errors()
            }
        }
        
        # Agregar estadísticas por tienda
        for store, stats in self.stats['store_stats'].items():
            report['store_performance'][store] = {
                'total_products': stats['total_products'],
                'high_discount_products': stats['high_discount_products'],
                'categories_scraped': len(stats['categories_scraped']),
                'error_count': len(stats['errors'])
            }
        
        return report
    
    def save_report(self, filename=None):
        """Guarda el reporte en un archivo JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraping_report_{timestamp}.json"
        
        report = self.generate_report()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 Reporte guardado en: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error guardando reporte: {e}")
            return None
    
    def print_summary(self):
        """Imprime un resumen en consola"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE SCRAPING")
        print("="*60)
        
        print(f"⏱️  Duración: {report['session_info']['duration']}")
        print(f"🌐 Peticiones: {report['request_stats']['total_requests']} "
              f"({report['request_stats']['success_rate']} éxito)")
        print(f"📦 Productos: {report['product_stats']['total_products_found']} total, "
              f"{report['product_stats']['high_discount_products']} con alto descuento")
        
        print("\n🏪 RENDIMIENTO POR TIENDA:")
        for store, stats in report['store_performance'].items():
            print(f"  • {store}: {stats['total_products']} productos, "
                  f"{stats['high_discount_products']} con descuento")
        
        if report['error_summary']['total_errors'] > 0:
            print(f"\n❌ Errores: {report['error_summary']['total_errors']} total")
            for error, count in report['error_summary']['most_common_errors']:
                print(f"  • {error}: {count} veces")
        
        print("="*60)
    
    def get_performance_alerts(self):
        """Genera alertas de rendimiento"""
        alerts = []
        
        # Alerta por tasa de éxito baja
        success_rate = self.get_success_rate()
        if success_rate < 80:
            alerts.append(f"⚠️ Tasa de éxito baja: {success_rate:.1f}%")
        
        # Alerta por muchos errores
        if self.stats['failed_requests'] > 10:
            alerts.append(f"⚠️ Muchos errores: {self.stats['failed_requests']} fallos")
        
        # Alerta por tiempo de respuesta alto
        if self.request_times:
            avg_time = sum(self.request_times) / len(self.request_times)
            if avg_time > 10:
                alerts.append(f"⚠️ Tiempo de respuesta alto: {avg_time:.1f}s promedio")
        
        return alerts 