# -*- coding: utf-8 -*-
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# --- Configuración ---
DEALS_FILE = 'deals.json'

# --- Aplicación FastAPI ---
app = FastAPI(
    title="API de Ofertas de Scraping",
    description="API para obtener las mejores ofertas encontradas por el sistema de scraping.",
    version="1.0.0"
)

# --- Endpoints ---
@app.get("/api/deals", summary="Obtener todas las ofertas", response_class=JSONResponse)
async def get_deals():
    """Devuelve una lista de todas las ofertas encontradas con más de 70% de descuento."""
    if not os.path.exists(DEALS_FILE):
        raise HTTPException(status_code=404, detail="No se ha generado el archivo de ofertas todavía. Ejecuta el scraping primero.")
    
    with open(DEALS_FILE, 'r', encoding='utf-8') as f:
        deals = json.load(f)
        
    return deals

@app.get("/api/search", summary="Buscar ofertas por palabra clave", response_class=JSONResponse)
async def search_deals(query: str):
    """Busca ofertas que contengan la palabra clave en el nombre del producto."""
    if not os.path.exists(DEALS_FILE):
        raise HTTPException(status_code=404, detail="No se ha generado el archivo de ofertas todavía. Ejecuta el scraping primero.")
        
    with open(DEALS_FILE, 'r', encoding='utf-8') as f:
        deals = json.load(f)
        
    results = [deal for deal in deals if query.lower() in deal.get('name', '').lower()]
    
    return results

# --- Ejecución (para pruebas locales) ---
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
