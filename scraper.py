import json
import re
import requests
from bs4 import BeautifulSoup

# URLs objetivo de los 3 organizadores
URL_TAE = "https://terrassaartsesceniques.cat/programacio/"
URL_LAFACT = "https://www.lafactcultural.cat/programacio/"
URL_TNT = "https://tnt.cat/es/programacio/"

def obtener_eventos_tae():
    eventos = []
    # Aquí irá la extracción específica para Terrassa Arts Escèniques
    return eventos

def obtener_eventos_lafact():
    eventos = []
    # Aquí irá la extracción específica para LaFACT
    return eventos

def obtener_eventos_tnt():
    eventos = []
    # Aquí irá la extracción específica para Festival TNT
    return eventos

def actualizar_index():
    # Recopilamos todos los eventos actualizados
    todos_eventos = []
    todos_eventos.extend(obtener_eventos_tae())
    todos_eventos.extend(obtener_eventos_lafact())
    todos_eventos.extend(obtener_eventos_tnt())

    # Si el scraper no devuelve datos (por ejemplo, si falla la red), no modificamos nada
    if not todos_eventos:
        print("No se encontraron nuevos eventos o la lista está vacía. No se modifica index.html.")
        return

    # Leemos el index.html actual
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Formateamos el JSON de los eventos
    json_eventos = json.dumps(todos_eventos, ensure_ascii=False, indent=6)

    # Reemplazamos la variable allData en el index.html
    nuevo_html = re.sub(
        r'const allData = \[[\s\S]*?\];',
        f'const allData = {json_eventos};',
        html
    )

    # Guardamos los cambios en el archivo
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(nuevo_html)

    print("✅ ¡index.html actualizado correctamente con nuevos datos!")

if __name__ == "__main__":
    actualizar_index()