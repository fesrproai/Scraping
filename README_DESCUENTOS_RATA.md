# 🐀 DESCUENTOS RATA - App de Scraping de Ofertas Chilenas

Una aplicación Python que scrapea automáticamente productos con grandes descuentos (70% o más) desde tiendas chilenas populares.

## 🎯 Objetivo

Scrapear automáticamente productos con grandes descuentos desde tiendas chilenas como Paris.cl, Ripley.cl, Hites.com, Falabella.com, Sodimac.cl y otras, mostrando solo las ofertas más atractivas.

## 🏗️ Estructura del Proyecto

```
descuentos_rata/
├── descuentos_rata.py          # Aplicación principal
├── scrapers/                   # Scrapers individuales por tienda
│   ├── __init__.py
│   └── paris_scraper.py        # Scraper específico para Paris
├── notifier/                   # Módulo de notificaciones
│   ├── __init__.py
│   └── telegram_notifier.py    # Notificaciones por Telegram
├── data/                       # Datos generados
│   ├── descuentos_rata.db      # Base de datos SQLite
│   └── productos.json          # Archivo JSON con productos
├── requirements.txt            # Dependencias
└── README_DESCUENTOS_RATA.md   # Este archivo
```

## ✨ Funcionalidades Principales

### 🔍 Scraping Inteligente
- **6 tiendas chilenas**: Paris, Ripley, Hites, Falabella, Sodimac, Easy
- **Filtrado automático**: Solo productos con 70%+ de descuento
- **Detección de duplicados**: Evita productos repetidos
- **Score de confiabilidad**: Detecta precios inflados

### 📊 Gestión de Datos
- **Base de datos SQLite**: Almacenamiento persistente
- **Archivo JSON**: Exportación de datos
- **Historial de precios**: Seguimiento de cambios
- **Eliminación de duplicados**: Mismo nombre + tienda

### 🔔 Notificaciones
- **Telegram**: Alertas para ofertas con 85%+ de descuento
- **Resumen diario**: Estadísticas de ofertas encontradas
- **Alertas de error**: Notificaciones de problemas

### 🎮 Menú CLI Interactivo
- **Ver últimas ofertas**: Productos recientes
- **Top 10 mejores ofertas**: Ranking por descuento
- **Búsqueda por palabra clave**: Filtrado inteligente
- **Forzar scraping**: Ejecución manual
- **Estadísticas**: Resumen completo

## 🚀 Instalación y Uso

### 1. Requisitos Previos
```bash
# Python 3.8 o superior
python --version

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración (Opcional)
Para notificaciones por Telegram, configura las variables de entorno:
```bash
# Windows
set TELEGRAM_BOT_TOKEN=tu_token_aqui
set TELEGRAM_CHAT_ID=tu_chat_id_aqui

# Linux/Mac
export TELEGRAM_BOT_TOKEN=tu_token_aqui
export TELEGRAM_CHAT_ID=tu_chat_id_aqui
```

### 3. Ejecución
```bash
# Ejecutar desde PowerShell
python descuentos_rata.py

# O crear un ejecutable
python -m PyInstaller --onefile descuentos_rata.py
```

## 📋 Dependencias

```txt
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
```

## 🏪 Tiendas Soportadas

| Tienda | URL | Categorías |
|--------|-----|------------|
| **Paris** | paris.cl | Liquidación, Ofertas, Tecnología, Hogar |
| **Ripley** | ripley.cl | Liquidación, Ofertas, Tecnología |
| **Hites** | hites.com | Liquidación, Ofertas, Tecnología |
| **Falabella** | falabella.com | Liquidación, Ofertas, Tecnología |
| **Sodimac** | sodimac.cl | Liquidación, Ofertas, Herramientas |
| **Easy** | easy.cl | Liquidación, Ofertas, Herramientas |

## 🔧 Configuración Avanzada

### Modificar Descuento Mínimo
Edita `descuentos_rata.py` línea 15:
```python
MIN_DISCOUNT_PERCENTAGE = 70  # Cambiar a 60, 80, etc.
```

### Agregar Nueva Tienda
1. Crear scraper en `scrapers/nueva_tienda_scraper.py`
2. Agregar configuración en `descuentos_rata.py` línea 40+
3. Implementar selectores específicos

### Configurar Telegram
1. Crear bot con @BotFather
2. Obtener token del bot
3. Obtener chat_id (enviar mensaje al bot y revisar logs)
4. Configurar variables de entorno

## 📊 Estructura de Datos

### Producto en Base de Datos
```sql
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hash_id TEXT UNIQUE,                    -- Hash único del producto
    nombre TEXT NOT NULL,                   -- Nombre del producto
    precio_actual REAL NOT NULL,            -- Precio actual
    precio_original REAL,                   -- Precio original
    descuento_porcentaje REAL,              -- % de descuento
    enlace TEXT,                           -- URL del producto
    imagen TEXT,                           -- URL de la imagen
    tienda TEXT NOT NULL,                  -- Nombre de la tienda
    categoria TEXT,                        -- Categoría del producto
    confiabilidad_score REAL DEFAULT 1.0,  -- Score de confiabilidad
    fecha_creacion TIMESTAMP,              -- Fecha de creación
    fecha_actualizacion TIMESTAMP          -- Última actualización
);
```

### Historial de Precios
```sql
CREATE TABLE historial_precios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_hash TEXT,                     -- Hash del producto
    precio REAL,                           -- Precio registrado
    fecha TIMESTAMP,                       -- Fecha del registro
    FOREIGN KEY (producto_hash) REFERENCES productos (hash_id)
);
```

## 🎮 Uso del Menú CLI

### Opciones Disponibles
1. **📦 Ver últimas ofertas**: Muestra las 20 ofertas más recientes
2. **🏆 Ver top 10 mejores ofertas**: Ranking por porcentaje de descuento
3. **🔍 Buscar producto**: Búsqueda por palabra clave
4. **🚀 Forzar scraping**: Ejecuta scraping completo de todas las tiendas
5. **📊 Ver estadísticas**: Resumen de productos y tiendas
6. **❌ Salir**: Cierra la aplicación

### Ejemplo de Uso
```
🐀 DESCUENTOS RATA - Ofertas Chilenas
==================================================
📊 Últimas ofertas: 15
🎯 Descuento promedio: 78.5%

OPCIONES DISPONIBLES:
1. 📦 Ver últimas ofertas
2. 🏆 Ver top 10 mejores ofertas
3. 🔍 Buscar producto
4. 🚀 Forzar scraping
5. 📊 Ver estadísticas
6. ❌ Salir

Selecciona una opción (1-6): 2
```

## 🔍 Algoritmo de Scraping

### 1. Extracción de Productos
- **Selectores CSS**: Específicos por tienda
- **Patrones de precio**: Regex para precios chilenos ($1.000,00)
- **Detección de descuentos**: Cálculo automático si no viene explícito

### 2. Filtrado Inteligente
- **Descuento mínimo**: Solo 70%+ de descuento
- **Score de confiabilidad**: Detecta precios inflados
- **Eliminación de duplicados**: Hash único por producto

### 3. Almacenamiento
- **Base de datos**: SQLite para persistencia
- **Historial**: Seguimiento de cambios de precio
- **JSON**: Exportación para análisis

## 📱 Notificaciones Telegram

### Configuración del Bot
1. Hablar con @BotFather en Telegram
2. Crear nuevo bot: `/newbot`
3. Obtener token del bot
4. Enviar mensaje al bot para obtener chat_id

### Tipos de Notificaciones
- **🚨 Ofertas extremas**: 85%+ de descuento
- **📊 Resumen diario**: Estadísticas de ofertas
- **⚠️ Alertas de error**: Problemas en el scraping

### Ejemplo de Mensaje
```
🚨 ¡OFERTA EXTREMA DETECTADA! 🚨

🏪 PARIS
📦 Samsung Galaxy S21 128GB

💰 Precio actual: $299.990
💸 Precio original: $899.990
🎯 Descuento: 85%
⭐ Confiabilidad: 0.9/1.0

🔗 Ver oferta

⏰ 29/07/2025 20:30
```

## 🛠️ Desarrollo y Extensión

### Agregar Nueva Tienda
1. **Crear scraper específico**:
```python
class NuevaTiendaScraper:
    def __init__(self):
        self.base_url = "https://www.nueva-tienda.cl"
        # Configuración específica
    
    def extract_products(self, html_content):
        # Lógica de extracción específica
        pass
```

2. **Agregar a configuración principal**:
```python
'nueva_tienda': {
    'name': 'Nueva Tienda',
    'base_url': 'https://www.nueva-tienda.cl',
    'categories': [
        {'name': 'Ofertas', 'url': 'https://www.nueva-tienda.cl/ofertas'}
    ]
}
```

### Modificar Selectores
Cada tienda tiene selectores CSS específicos en `extract_products_from_html()`:
```python
store_selectors = {
    'paris': ['.product-item', '.product-card'],
    'nueva_tienda': ['.mi-selector', '.otro-selector']
}
```

## 🔒 Consideraciones de Seguridad

### Headers y User-Agent
- Headers realistas para evitar bloqueos
- User-Agent de Chrome actualizado
- Pausas entre requests (2-3 segundos)

### Rate Limiting
- Máximo 50 productos por tienda
- Pausas entre categorías
- Backoff exponencial en errores

### Manejo de Errores
- Timeout de 30 segundos por request
- 3 reintentos por página
- Logging de errores

## 📈 Monetización Futura

### Enlaces de Afiliado
La estructura está preparada para enlaces de afiliado:
```python
# En configuración de tienda
'affiliate_url': 'https://tienda.com/?ref=tu_codigo'
```

### Funcionalidades Planificadas
- **API REST**: Para integración con apps móviles
- **Dashboard web**: Interfaz gráfica con Flask/Streamlit
- **Alertas personalizadas**: Por categoría o precio
- **Comparador de precios**: Entre tiendas

## 🐛 Solución de Problemas

### Error: "No se encontraron productos"
- Verificar conectividad a internet
- Revisar si las URLs de las tiendas han cambiado
- Comprobar que los selectores CSS siguen siendo válidos

### Error: "Telegram no está configurado"
- Configurar variables de entorno
- Verificar token y chat_id
- Probar conexión con `notifier/telegram_notifier.py`

### Error: "Base de datos bloqueada"
- Cerrar otras instancias de la aplicación
- Verificar permisos de escritura en carpeta `data/`

## 📄 Licencia

Este proyecto es de código abierto. Puedes modificarlo y distribuirlo libremente.

## 🤝 Contribuciones

Las contribuciones son bienvenidas:
1. Fork del proyecto
2. Crear rama para nueva funcionalidad
3. Commit de cambios
4. Push a la rama
5. Crear Pull Request

## 📞 Soporte

Para soporte o preguntas:
- Crear issue en GitHub
- Revisar documentación
- Verificar logs de error

---

**🐀 Descuentos Rata** - Encuentra las mejores ofertas de Chile automáticamente! 