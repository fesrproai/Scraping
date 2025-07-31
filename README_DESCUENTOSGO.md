# 🎯 DESCUENTOSGO - Scanner Automático Infinito

## 📋 Descripción

**DescuentosGO** es una aplicación avanzada de scraping automático que busca ofertas con 70% o más de descuento en las principales tiendas chilenas. La aplicación funciona 24/7 escaneando continuamente todas las tiendas configuradas y enviando notificaciones automáticas por Telegram.

## 🚀 Características Principales

### 🔄 Scanner Automático Infinito
- **Escaneo continuo**: La aplicación se ejecuta automáticamente cada 5 minutos
- **12 tiendas chilenas**: Paris, Hites, Falabella, Sodimac, Easy, Líder, Jumbo, Santa Isabel, Alcampo, Unimarc, Walmart, Tottus
- **Gestión de categorías**: Checkboxes para activar/desactivar categorías específicas por tienda
- **Detección de duplicados**: Evita productos repetidos usando hashing

### 📱 Bot de Telegram Integrado
- **Notificaciones automáticas**: Alerta cuando encuentra ofertas con 85%+ de descuento
- **Bot configurado**: `DescuentosGO_bot` ya integrado
- **Mensajes detallados**: Incluye precio, descuento, tienda y enlace directo

### 💾 Gestión de Datos Avanzada
- **Base de datos SQLite**: Almacenamiento persistente de productos y historial
- **Historial de precios**: Seguimiento de cambios de precios por producto
- **Score de confiabilidad**: Detecta precios inflados y calcula confiabilidad
- **Exportación JSON**: Datos disponibles en formato JSON

### 🎯 Filtros Inteligentes
- **Descuento mínimo**: Solo productos con 70%+ de descuento
- **Detección de spam**: Evita notificaciones repetidas
- **Validación de precios**: Verifica que los precios sean realistas

## 🏪 Tiendas Soportadas

| Tienda | Categorías Disponibles |
|--------|----------------------|
| **Paris** | Página Principal, Tecnología, Hogar, Deportes, Ropa |
| **Hites** | Liquidación, Tecnología, Hogar, Deportes, Página Principal |
| **Falabella** | Liquidación, Ofertas, Tecnología, Hogar, Deportes |
| **Sodimac** | Liquidación, Ofertas, Herramientas, Jardín, Construcción |
| **Easy** | Liquidación, Ofertas, Herramientas, Jardín, Hogar |
| **Líder** | Ofertas, Tecnología, Hogar, Deportes, Página Principal |
| **Jumbo** | Ofertas, Tecnología, Hogar, Deportes, Página Principal |
| **Santa Isabel** | Ofertas, Tecnología, Hogar, Página Principal |
| **Alcampo** | Ofertas, Tecnología, Hogar, Página Principal |
| **Unimarc** | Ofertas, Tecnología, Hogar, Página Principal |
| **Walmart** | Ofertas, Tecnología, Hogar, Página Principal |
| **Tottus** | Ofertas, Tecnología, Hogar, Página Principal |

## 🎮 Menú Interactivo

### Opciones Principales:
1. **🚀 Iniciar/Detener Scanner** - Controla el escaneo automático
2. **📦 Ver últimas ofertas** - Muestra las ofertas más recientes
3. **🏆 Ver top 10 mejores ofertas** - Ranking por descuento
4. **🔍 Buscar producto** - Búsqueda por palabra clave
5. **⚙️ Gestionar categorías** - Activar/desactivar categorías
6. **📊 Ver estadísticas completas** - Métricas del sistema
7. **🔧 Configurar Telegram** - Configurar notificaciones
8. **❌ Salir** - Cerrar la aplicación

### Gestión de Categorías:
- **Checkboxes por tienda**: Activa/desactiva categorías específicas
- **Control granular**: Gestiona cada tienda independientemente
- **Estado visual**: Muestra qué categorías están activas

## 📊 Estadísticas del Sistema

La aplicación proporciona estadísticas detalladas:
- **Total de productos**: Número total de ofertas encontradas
- **Descuento promedio**: Promedio de descuentos detectados
- **Mejor oferta**: Mayor descuento encontrado
- **Productos por tienda**: Distribución por tienda
- **Escaneos completados**: Número de escaneos realizados
- **Notificaciones enviadas**: Contador de alertas Telegram
- **Categorías activas**: Número de categorías habilitadas

## 🔧 Configuración de Telegram

### Configuración Automática:
- **Bot Token**: `8442920382:AAG_FpAAoJoWwKt9YAGv0fe5skB8fT1T2xg`
- **Bot Name**: `DescuentosGO_bot`
- **Chat ID**: Configurable desde el menú

### Configuración Manual:
1. Abre la aplicación
2. Selecciona opción **7. 🔧 Configurar Telegram**
3. Ingresa tu Chat ID de Telegram
4. Prueba la conexión

### Cómo obtener tu Chat ID:
1. Busca `@userinfobot` en Telegram
2. Envía cualquier mensaje al bot
3. El bot te responderá con tu Chat ID

## 📁 Estructura de Archivos

```
Descuentos_Rata_Auto.exe          # Ejecutable principal
data/
├── descuentos_rata_auto.db       # Base de datos SQLite
├── productos_auto.json           # Exportación JSON
└── scanner_logs.db              # Logs del scanner
```

## 🚀 Instalación y Uso

### Ejecución Directa:
1. **Doble clic** en `DescuentosGO.exe`
2. La aplicación se ejecutará automáticamente
3. Usa el menú para controlar el scanner

### Configuración Inicial:
1. Ejecuta la aplicación
2. Configura Telegram (opcional)
3. Gestiona categorías según tus preferencias
4. Inicia el scanner automático

## ⚙️ Configuración Avanzada

### Variables de Entorno:
```bash
TELEGRAM_BOT_TOKEN=8442920382:AAG_FpAAoJoWwKt9YAGv0fe5skB8fT1T2xg
TELEGRAM_CHAT_ID=tu_chat_id_aqui
```

### Parámetros del Scanner:
- **Intervalo de escaneo**: 5 minutos (configurable)
- **Descuento mínimo**: 70% (configurable)
- **Umbral Telegram**: 85% (configurable)
- **Máximo productos por tienda**: 100 (configurable)

## 🔍 Funcionalidades de Búsqueda

### Búsqueda por Palabra Clave:
- **Búsqueda inteligente**: Encuentra productos por nombre
- **Filtrado por descuento**: Ordena por mayor descuento
- **Resultados en tiempo real**: Búsqueda instantánea

### Top 10 Ofertas:
- **Ranking automático**: Mejores ofertas por descuento
- **Score de confiabilidad**: Considera la calidad del descuento
- **Información completa**: Precios, tienda, enlace

## 📈 Monitoreo y Logs

### Logs del Scanner:
- **Registro de escaneos**: Fecha, duración, productos encontrados
- **Estadísticas por tienda**: Rendimiento de cada tienda
- **Historial de errores**: Problemas detectados

### Base de Datos:
- **Tabla productos**: Información completa de ofertas
- **Tabla historial_precios**: Seguimiento de cambios
- **Tabla scanner_logs**: Logs de actividad

## 🛠️ Solución de Problemas

### Problemas Comunes:

**Scanner no encuentra productos:**
- Verifica conexión a internet
- Revisa que las categorías estén activas
- Comprueba que las tiendas estén funcionando

**No recibo notificaciones de Telegram:**
- Verifica que el Chat ID esté configurado
- Prueba la conexión desde el menú
- Asegúrate de que el bot esté activo

**La aplicación se cierra inesperadamente:**
- Verifica que tengas permisos de escritura
- Comprueba el espacio en disco
- Revisa los logs de error

## 🔮 Futuras Mejoras

### Funcionalidades Planificadas:
- **Web Dashboard**: Interfaz web para monitoreo
- **Alertas personalizadas**: Configurar umbrales por usuario
- **Comparación de precios**: Análisis entre tiendas
- **Enlaces de afiliados**: Monetización automática
- **API REST**: Integración con otras aplicaciones

### Optimizaciones Técnicas:
- **Scraping paralelo**: Múltiples tiendas simultáneamente
- **Cache inteligente**: Reducir requests innecesarios
- **Machine Learning**: Detección automática de patrones
- **Análisis de tendencias**: Predicción de ofertas

## 📞 Soporte

### Información de Contacto:
- **Bot de Telegram**: `@DescuentosGO_bot`
- **Versión**: 2.0 - Scanner Automático Infinito
- **Última actualización**: Diciembre 2024

### Reportar Problemas:
1. Usa el menú de estadísticas para ver logs
2. Verifica la configuración de Telegram
3. Comprueba la conectividad de internet
4. Revisa que las tiendas estén accesibles

---

## 🎉 ¡Disfruta Encontrando las Mejores Ofertas!

**DescuentosGO** te ayudará a encontrar las mejores ofertas automáticamente, sin perder tiempo revisando múltiples sitios web. ¡Deja que la aplicación trabaje por ti mientras tú te enfocas en lo importante! 