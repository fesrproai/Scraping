# Sistema de Scraping de Descuentos - Tiendas Chilenas

Sistema automatizado que monitorea las principales tiendas online de Chile para identificar productos con descuentos del 70% o más.

## Características

- Scraping automatizado de múltiples tiendas chilenas
- Detección de descuentos del 70% o más
- Almacenamiento en Firebase Firestore
- Interfaz web en React para visualizar resultados
- Ejecución automática cada hora
- Manejo robusto de errores y anti-bloqueo

## Tiendas Soportadas

### 🛍️ Tiendas Generales
- **Paris.cl** - Ropa, tecnología, hogar (con sección Liquidación)
- **Falabella.com** - Categorización excelente, JavaScript dinámico
- **Ripley.cl** - Fácil de scrapear, muchos descuentos
- **La Polar.cl** - Excelentes ofertas en vestuario y hogar
- **Hites.com** - Productos muy rebajados constantemente

### 🏠 Hogar y Construcción
- **Sodimac.cl** - Electro, herramientas, muebles, outlet y saldos

## Estructura del Proyecto

```
scraping/
├── scrapers/           # Módulos de scraping por tienda
├── core/              # Lógica central y filtros
├── database/          # Configuración de Firebase
├── scheduler/         # Automatización periódica
├── api/               # API Flask para el frontend
├── frontend/          # Interfaz React
├── config/            # Configuraciones
└── utils/             # Utilidades comunes
```

## 🚀 Instalación

### Opción 1: Ejecutable (.exe) - Recomendado

1. **Descargar el ejecutable**
   - Descarga `DescuentosCL.exe` desde los releases
   - O ejecuta `build_all.py` para crear tu propio ejecutable

2. **Configurar Firebase**
   - Crear proyecto en [Firebase Console](https://console.firebase.google.com)
   - Descargar credenciales de servicio
   - Crear archivo `.env` con tus credenciales

3. **Ejecutar**
   ```bash
   DescuentosCL.exe --store all --verbose
   ```

### Opción 2: Código Fuente

#### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Cuenta de Firebase (gratuita)

#### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <url-del-repositorio>
   cd scraping
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar Firebase**
   - Crear proyecto en [Firebase Console](https://console.firebase.google.com)
   - Descargar credenciales de servicio
   - Copiar `.env.example` a `.env`
   - Editar `.env` con tus credenciales

4. **Instalar dependencias del frontend:**
   ```bash
   cd frontend
   npm install
   ```

### Opción 3: Crear Ejecutable

Si quieres crear tu propio ejecutable:

```bash
# Opción simple
python build_simple.py

# Opción completa (con instalador)
python build_all.py
```

Esto generará:
- `dist/DescuentosCL.exe` - Ejecutable principal
- `dist/DescuentosCL/` - Paquete completo con documentación
- `installer/DescuentosCL_Setup.exe` - Instalador MSI (si tienes Inno Setup)

## Uso

### Ejecutar Scraping Manual
```bash
python main.py
```

### Ejecutar Scheduler Automático
```bash
python scheduler/scheduler.py
```

### Ejecutar API
```bash
python api/app.py
```

### Ejecutar Frontend
```bash
cd frontend
npm start
```

## Configuración

Edita `config/settings.py` para personalizar:
- Intervalos de scraping
- Porcentajes de descuento mínimos
- Configuración de proxies
- Headers de navegación

## Contribuir

1. Fork el proyecto
2. Crear rama para feature
3. Commit cambios
4. Push a la rama
5. Abrir Pull Request 