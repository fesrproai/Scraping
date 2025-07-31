import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from config.settings import FIREBASE_CONFIG

class FirebaseClient:
    def __init__(self):
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Inicializa la conexión con Firebase"""
        try:
            # Verificar si ya está inicializado
            if not firebase_admin._apps:
                cred = credentials.Certificate(FIREBASE_CONFIG)
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            print("✅ Conexión a Firebase establecida correctamente")
        except Exception as e:
            print(f"❌ Error al conectar con Firebase: {e}")
            raise
    
    def save_product(self, product_data):
        """Guarda un producto en Firestore"""
        try:
            if not self.db:
                raise Exception("Firebase no está inicializado")
            
            # Agregar timestamp
            product_data['timestamp'] = datetime.now()
            product_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            # Crear ID único basado en store + nombre + precio
            product_id = f"{product_data['store']}_{product_data['name'][:50]}_{product_data['current_price']}"
            product_id = product_id.replace(' ', '_').replace('/', '_').lower()
            
            # Guardar en la colección 'products'
            doc_ref = self.db.collection('products').document(product_id)
            doc_ref.set(product_data, merge=True)
            
            print(f"✅ Producto guardado: {product_data['name'][:50]}...")
            return product_id
            
        except Exception as e:
            print(f"❌ Error al guardar producto: {e}")
            return None
    
    def save_products_batch(self, products_list):
        """Guarda múltiples productos en lote"""
        try:
            if not self.db:
                raise Exception("Firebase no está inicializado")
            
            batch = self.db.batch()
            saved_count = 0
            
            for product_data in products_list:
                # Agregar timestamp
                product_data['timestamp'] = datetime.now()
                product_data['created_at'] = firestore.SERVER_TIMESTAMP
                
                # Crear ID único
                product_id = f"{product_data['store']}_{product_data['name'][:50]}_{product_data['current_price']}"
                product_id = product_id.replace(' ', '_').replace('/', '_').lower()
                
                doc_ref = self.db.collection('products').document(product_id)
                batch.set(doc_ref, product_data, merge=True)
                saved_count += 1
            
            # Ejecutar batch
            batch.commit()
            print(f"✅ {saved_count} productos guardados en lote")
            return saved_count
            
        except Exception as e:
            print(f"❌ Error al guardar productos en lote: {e}")
            return 0
    
    def get_products(self, filters=None, limit=100):
        """Obtiene productos de Firestore con filtros opcionales"""
        try:
            if not self.db:
                raise Exception("Firebase no está inicializado")
            
            query = self.db.collection('products')
            
            # Aplicar filtros
            if filters:
                if filters.get('store'):
                    query = query.where('store', '==', filters['store'])
                if filters.get('category'):
                    query = query.where('category', '==', filters['category'])
                if filters.get('min_discount'):
                    query = query.where('discount_percentage', '>=', filters['min_discount'])
            
            # Ordenar por timestamp descendente
            query = query.order_by('timestamp', direction=firestore.Query.DESCENDING)
            
            # Limitar resultados
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            products = []
            
            for doc in docs:
                product = doc.to_dict()
                product['id'] = doc.id
                products.append(product)
            
            return products
            
        except Exception as e:
            print(f"❌ Error al obtener productos: {e}")
            return []
    
    def get_products_by_discount(self, min_discount=70):
        """Obtiene productos con descuento mínimo específico"""
        return self.get_products({'min_discount': min_discount})
    
    def get_products_by_store(self, store_name):
        """Obtiene productos de una tienda específica"""
        return self.get_products({'store': store_name})
    
    def get_products_by_category(self, category):
        """Obtiene productos de una categoría específica"""
        return self.get_products({'category': category})
    
    def delete_old_products(self, days_old=7):
        """Elimina productos antiguos (más de X días)"""
        try:
            if not self.db:
                raise Exception("Firebase no está inicializado")
            
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            query = self.db.collection('products').where('timestamp', '<', cutoff_date)
            docs = query.stream()
            
            batch = self.db.batch()
            deleted_count = 0
            
            for doc in docs:
                batch.delete(doc.reference)
                deleted_count += 1
            
            if deleted_count > 0:
                batch.commit()
                print(f"✅ {deleted_count} productos antiguos eliminados")
            
            return deleted_count
            
        except Exception as e:
            print(f"❌ Error al eliminar productos antiguos: {e}")
            return 0
    
    def get_statistics(self):
        """Obtiene estadísticas de los productos almacenados"""
        try:
            if not self.db:
                raise Exception("Firebase no está inicializado")
            
            # Contar total de productos
            total_products = len(list(self.db.collection('products').stream()))
            
            # Contar por tienda
            stores = {}
            docs = self.db.collection('products').stream()
            
            for doc in docs:
                product = doc.to_dict()
                store = product.get('store', 'Unknown')
                stores[store] = stores.get(store, 0) + 1
            
            # Contar productos con descuento alto
            high_discount_products = len(list(
                self.db.collection('products')
                .where('discount_percentage', '>=', 70)
                .stream()
            ))
            
            return {
                'total_products': total_products,
                'products_by_store': stores,
                'high_discount_products': high_discount_products
            }
            
        except Exception as e:
            print(f"❌ Error al obtener estadísticas: {e}")
            return {} 