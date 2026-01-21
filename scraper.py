# =========================
# IMPORTACIÓN DE LIBRERÍAS
# =========================

# Librería para realizar solicitudes HTTP
import requests

# Librería para controlar pausas entre peticiones (politeness)
import time

# Librerías para exportación de datos
import csv
import json

# Librería para logging estructurado
import logging

# Librería para expresiones regulares (extracción de números)
import re

# Librería para persistencia en base de datos SQLite
import sqlite3

# Parser HTML
from bs4 import BeautifulSoup

# Tipado estático (mejora legibilidad y mantenibilidad)
from typing import List, Dict, Optional


# =========================
# CONSTANTES DEL PROYECTO
# =========================

# URL base del sitio web
URL_BASE = "http://books.toscrape.com/"

# URL inicial de la paginación
URL_INICIAL = URL_BASE + "catalogue/page-1.html"

# Tiempo de espera entre requests para no saturar el servidor
TIEMPO_ESPERA_SEGUNDOS = 1.5

# Mapeo de valoraciones textuales a valores numéricos
MAPA_VALORACIONES = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


# =========================
# CONFIGURACIÓN DE LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# =========================
# FUNCIONES AUXILIARES
# =========================

def obtener_soup(url: str) -> Optional[BeautifulSoup]:
    """
    Realiza una solicitud HTTP a la URL proporcionada y devuelve
    un objeto BeautifulSoup para parsear el HTML.

    Maneja errores de red y fuerza encoding UTF-8 para evitar
    problemas de caracteres especiales.
    """
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        respuesta.encoding = "utf-8"
        return BeautifulSoup(respuesta.text, "html.parser")
    except requests.RequestException as error:
        logging.error(f"Error al acceder a {url}: {error}")
        return None


def parsear_precio(texto_precio: str) -> float:
    """
    Convierte el precio desde texto (ej: '£51.77')
    a un valor numérico float (51.77).
    """
    return float(texto_precio.replace("£", "").strip())


def parsear_stock(texto_stock: str) -> Optional[int]:
    """
    Extrae la cantidad numérica de stock desde un texto como:
    'In stock (19 available)' → 19

    Si no se encuentra un número, retorna None.
    """
    coincidencia = re.search(r"(\d+)", texto_stock)
    return int(coincidencia.group(1)) if coincidencia else None


def parsear_valoracion(etiqueta_html) -> Optional[int]:
    """
    Convierte la valoración en estrellas desde texto HTML
    a un valor entero (1 a 5).

    Ejemplo:
    <p class="star-rating Three"> → 3
    """
    try:
        clases = etiqueta_html.get("class", [])
        for clase in clases:
            if clase in MAPA_VALORACIONES:
                return MAPA_VALORACIONES[clase]
    except Exception:
        pass
    return None


# =========================
# SCRAPING DE UNA PÁGINA
# =========================

def scrapear_pagina(url: str) -> List[Dict]:
    """
    Extrae todos los productos de una página específica
    y retorna una lista de diccionarios con los datos limpios.
    """
    soup = obtener_soup(url)
    if not soup:
        return []

    productos = []

    # Cada producto está contenido en un article.product_pod
    articulos = soup.select("article.product_pod")

    for articulo in articulos:
        try:
            # Extracción del título
            titulo = articulo.h3.a["title"]

            # Extracción y conversión del precio
            precio = parsear_precio(
                articulo.select_one(".price_color").text
            )

            # Extracción de la valoración
            valoracion = parsear_valoracion(
                articulo.select_one(".star-rating")
            )

            # Extracción del texto de stock
            texto_stock = articulo.select_one(".availability").text.strip()

            # Extracción de la cantidad numérica de stock
            cantidad_stock = parsear_stock(texto_stock)

            # Almacenamiento del producto como diccionario
            productos.append({
                "titulo": titulo,
                "precio": precio,
                "valoracion": valoracion,
                "cantidad_stock": cantidad_stock,
                "texto_stock": texto_stock
            })

        except Exception as error:
            # Error controlado: no detiene el proceso completo
            logging.warning(f"Error procesando producto: {error}")

    return productos


# =========================
# SCRAPING DE TODA LA WEB
# =========================

def obtener_todos_los_productos() -> List[Dict]:
    """
    Recorre todas las páginas de paginación del sitio
    y consolida todos los productos en una sola lista.
    """
    productos_totales = []
    url_actual = URL_INICIAL

    while url_actual:
        logging.info(f"Scrapeando: {url_actual}")

        productos_pagina = scrapear_pagina(url_actual)
        productos_totales.extend(productos_pagina)

        soup = obtener_soup(url_actual)

        # Detección de botón "Next" para paginación
        if soup and soup.select_one("li.next a"):
            siguiente_pagina = soup.select_one("li.next a")["href"]
            url_actual = URL_BASE + "catalogue/" + siguiente_pagina
            time.sleep(TIEMPO_ESPERA_SEGUNDOS)
        else:
            url_actual = None

    return productos_totales


# =========================
# EXPORTACIÓN DE DATOS
# =========================

def guardar_csv(datos: List[Dict], nombre_archivo: str):
    """
    Guarda los datos en formato CSV.
    """
    with open(nombre_archivo, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=datos[0].keys())
        escritor.writeheader()
        escritor.writerows(datos)


def guardar_json(datos: List[Dict], nombre_archivo: str):
    """
    Guarda los datos en formato JSON.
    """
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)


def guardar_sqlite(datos: List[Dict], nombre_bd: str):
    """
    Guarda los datos en una base de datos SQLite.
    """
    conexion = sqlite3.connect(nombre_bd)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            precio REAL,
            valoracion INTEGER,
            cantidad_stock INTEGER,
            texto_stock TEXT
        )
    """)

    cursor.executemany("""
        INSERT INTO productos (titulo, precio, valoracion, cantidad_stock, texto_stock)
        VALUES (?, ?, ?, ?, ?)
    """, [
        (
            p["titulo"],
            p["precio"],
            p["valoracion"],
            p["cantidad_stock"],
            p["texto_stock"]
        ) for p in datos
    ])

    conexion.commit()
    conexion.close()


# =========================
# PUNTO DE ENTRADA
# =========================

if __name__ == "__main__":
    productos = obtener_todos_los_productos()
    guardar_csv(productos, "productos.csv")
    guardar_json(productos, "productos.json")
    guardar_sqlite(productos, "productos.db")

    logging.info(
        f"Proceso completado correctamente. Total productos extraídos: {len(productos)}"
    )
