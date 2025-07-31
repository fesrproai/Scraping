# Guía de Instalación - Sistema de Scraping de Descuentos

## Prerrequisitos

- Python 3.8 o superior
- Node.js 16 o superior
- npm o yarn
- Cuenta de Firebase con proyecto configurado

## Paso 1: Configuración del Entorno

### 1.1 Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd scraping
```

### 1.2 Crear entorno virtual de Python
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

### 1.3 Instalar dependencias de Python
```bash
pip install -r requirements.txt
```

## Paso 2: Configuración de Firebase

### 2.1 Crear proyecto en Firebase
1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Crea un nuevo proyecto
3. Habilita Firestore Database
4. Ve a Configuración del proyecto > Cuentas de servicio
5. Genera una nueva clave privada
6. Descarga el archivo JSON

### 2.2 Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar .env con tus credenciales de Firebase
```

Ejemplo de `.env`:
```env
FIREBASE_PROJECT_ID=tu-proyecto-id
FIREBASE_PRIVATE_KEY_ID=tu-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nTu-clave-privada-aqui\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=tu-service-account@tu-proyecto.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=tu-client-id
FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/tu-service-account%40tu-proyecto.iam.gserviceaccount.com
```

## Paso 3: Configuración del Frontend

### 3.1 Instalar dependencias de React
```bash
cd frontend
npm install
```

### 3.2 Configurar Tailwind CSS
```bash
# Tailwind ya está configurado, pero puedes personalizar:
npx tailwindcss init -p
```

## Paso 4: Ejecutar el Sistema

### 4.1 Ejecutar la API (Terminal 1)
```bash
# Desde la raíz del proyecto
python api/app.py
```

La API estará disponible en: http://localhost:5000

### 4.2 Ejecutar el Frontend (Terminal 2)
```bash
cd frontend
npm start
```

El frontend estará disponible en: http://localhost:3000

### 4.3 Ejecutar Scraping Manual (Opcional)
```bash
# Desde la raíz del proyecto
python main.py --store paris --verbose
```

### 4.4 Ejecutar Scheduler Automático (Opcional)
```bash
# Desde la raíz del proyecto
python scheduler/scheduler.py
```

## Paso 5: Verificar la Instalación

### 5.1 Verificar API
```bash
curl http://localhost:5000/
```

Deberías recibir:
```json
{
  "message": "API de Scraping de Descuentos",
  "version": "1.0.0",
  "endpoints": {...}
}
```

### 5.2 Verificar Frontend
Abre http://localhost:3000 en tu navegador. Deberías ver la página de inicio.

### 5.3 Verificar Scraping
```bash
python main.py --store paris --dry-run
```

## Estructura de Archivos

```
scraping/
├── api/                    # API Flask
│   └── app.py
├── config/                 # Configuraciones
│   └── settings.py
├── core/                   # Lógica central
│   └── product_processor.py
├── database/               # Cliente Firebase
│   └── firebase_client.py
├── frontend/               # Aplicación React
│   ├── src/
│   ├── package.json
│   └── tailwind.config.js
├── scrapers/               # Módulos de scraping
│   ├── base_scraper.py
│   └── paris_scraper.py
├── scheduler/              # Automatización
│   └── scheduler.py
├── utils/                  # Utilidades
│   └── helpers.py
├── main.py                 # Script principal
├── requirements.txt        # Dependencias Python
└── README.md
```

## Comandos Útiles

### Scraping Manual
```bash
# Todas las tiendas
python main.py

# Tienda específica
python main.py --store paris

# Con información detallada
python main.py --verbose

# Modo prueba (sin guardar en Firebase)
python main.py --dry-run
```

### Desarrollo Frontend
```bash
cd frontend
npm start          # Desarrollo
npm run build      # Producción
npm test           # Tests
```

### API
```bash
# Desarrollo
python api/app.py

# Producción
gunicorn -w 4 -b 0.0.0.0:5000 api.app:app
```

## Solución de Problemas

### Error de Firebase
- Verifica que las credenciales en `.env` sean correctas
- Asegúrate de que Firestore esté habilitado en tu proyecto
- Verifica que la cuenta de servicio tenga permisos de escritura

### Error de Scraping
- Verifica tu conexión a internet
- Algunos sitios pueden bloquear requests automáticos
- Ajusta los delays en `config/settings.py`

### Error de Frontend
- Verifica que la API esté corriendo en el puerto 5000
- Revisa la consola del navegador para errores
- Verifica que todas las dependencias estén instaladas

### Error de Dependencias
```bash
# Reinstalar dependencias Python
pip uninstall -r requirements.txt
pip install -r requirements.txt

# Reinstalar dependencias Node
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Configuración Avanzada

### Personalizar Selectores CSS
Edita `config/settings.py` para ajustar los selectores de cada tienda.

### Agregar Nueva Tienda
1. Crea nuevo scraper en `scrapers/`
2. Hereda de `BaseScraper`
3. Implementa métodos `scrape_category()` y `parse_product()`
4. Agrega configuración en `config/settings.py`
5. Registra en `scheduler/scheduler.py`

### Cambiar Intervalo de Scraping
Edita `SCRAPING_INTERVAL_HOURS` en `config/settings.py`.

### Configurar Proxies
Agrega configuración de proxies en `utils/helpers.py`.

## Soporte

Para problemas o preguntas:
1. Revisa los logs de error
2. Verifica la configuración
3. Consulta la documentación de las librerías
4. Abre un issue en el repositorio 