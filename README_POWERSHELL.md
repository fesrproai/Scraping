# Sistema de Scraping de Descuentos - Versión PowerShell

## 🚀 Descripción

Sistema de scraping de descuentos optimizado para PowerShell que funciona sin Firebase, guardando todos los datos localmente en archivos JSON.

## ✨ Características

- ✅ **Sin Firebase**: No requiere configuración de base de datos
- ✅ **Compatible con PowerShell**: Funciona nativamente en Windows
- ✅ **Almacenamiento local**: Guarda datos en archivos JSON
- ✅ **Scraping automático**: Extrae productos de tiendas chilenas
- ✅ **Filtrado por descuento**: Encuentra ofertas con descuentos altos
- ✅ **Interfaz simple**: Script de PowerShell con menú interactivo

## 📁 Estructura del Proyecto

```
scraping/
├── data/                          # Carpeta con archivos generados
│   ├── demo_system_*.json         # Archivos de demostración
│   └── *_products_*.json          # Archivos de productos encontrados
├── scraping_final.py              # Script principal de scraping
├── demo_scraping.py               # Script de demostración
├── ejecutar_scraping.ps1          # Script de PowerShell
└── README_POWERSHELL.md           # Este archivo
```

## 🛠️ Instalación

1. **Verificar Python**: Asegúrate de tener Python instalado
2. **Instalar dependencias**:
   ```bash
   pip install requests beautifulsoup4
   ```

## 🎯 Uso

### Opción 1: Script de PowerShell (Recomendado)
```powershell
powershell -ExecutionPolicy Bypass -File ejecutar_scraping.ps1
```

### Opción 2: Ejecución directa
```bash
# Demostración
python demo_scraping.py

# Scraping completo
python scraping_final.py
```

## 📊 Resultados

Los datos se guardan en la carpeta `data/` con el siguiente formato:

```json
{
  "store": "paris",
  "timestamp": "2025-07-29T18:09:42",
  "total_products": 5,
  "products": [
    {
      "name": "Producto ejemplo",
      "current_price": "$29.990",
      "original_price": "$59.990",
      "discount": "50%",
      "product_link": "https://...",
      "product_image": "https://...",
      "store": "paris",
      "scraped_at": "2025-07-29T18:09:42"
    }
  ]
}
```

## 🏪 Tiendas Soportadas

- **Paris**: https://www.paris.cl
- **Falabella**: https://www.falabella.com

## 🔧 Configuración

El sistema está configurado para:
- **Descuento mínimo**: 70%
- **Timeout de conexión**: 30 segundos
- **Delay entre requests**: 2 segundos
- **Formato de archivo**: JSON con codificación UTF-8

## 📈 Ventajas de esta Versión

1. **Simplicidad**: No requiere configuración de Firebase
2. **Portabilidad**: Funciona en cualquier Windows con Python
3. **Transparencia**: Los datos están en archivos JSON legibles
4. **Flexibilidad**: Fácil de modificar y extender
5. **Independencia**: No depende de servicios externos

## 🚨 Limitaciones

- Los selectores CSS pueden necesitar actualización si las tiendas cambian su estructura
- Algunas páginas usan JavaScript para cargar productos dinámicamente
- Las URLs de categorías pueden cambiar con el tiempo

## 🔄 Actualizaciones Futuras

- [ ] Agregar más tiendas
- [ ] Mejorar selectores CSS
- [ ] Agregar soporte para JavaScript dinámico
- [ ] Implementar interfaz web simple
- [ ] Agregar notificaciones de ofertas

## 📞 Soporte

Si encuentras problemas:
1. Verifica que Python esté instalado
2. Asegúrate de tener las dependencias instaladas
3. Revisa la carpeta `data/` para ver los archivos generados
4. Ejecuta la demostración para verificar el funcionamiento

## 🎉 ¡Listo!

El sistema está funcionando correctamente y listo para usar. ¡Disfruta encontrando las mejores ofertas! 