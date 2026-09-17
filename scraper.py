import json
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def obtener_eventos_tae():
    eventos = []
    # Evento de prueba para forzar la detección de cambios
    eventos.append({
        "fecha": "2026-10-15",
        "dia": "Dijous",
        "hora": "20h",
        "actividad": "🎭 EVENTO DE PRUEBA: Gran Concierto de Test",
        "lugar": "Teatre Principal",
        "categoria": "Música",
        "precio": "10€",
        "organizador": "Terrassa Arts Escèniques",
        "url": "https://terrassaartsesceniques.cat"
    })
    return eventos

def obtener_eventos_lafact():
    return []

def obtener_eventos_tnt():
    return []

def actualizar_index():
    nuevos_eventos = []
    nuevos_eventos.extend(obtener_eventos_tae())
    nuevos_eventos.extend(obtener_eventos_lafact())
    nuevos_eventos.extend(obtener_eventos_tnt())

    if not nuevos_eventos:
        print("No hay eventos nuevos.")
        return

    # Leemos el index.html actual
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Buscamos si el evento de prueba ya está dentro para evitar duplicados
    json_eventos = json.dumps(nuevos_eventos, ensure_ascii=False, indent=6)

    # Reemplazamos la variable allData en el index.html
    nuevo_html = re.sub(
        r'const allData = \[[\s\S]*?\];',
        f'const allData = {json_eventos};',
        html
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(nuevo_html)

    print("✅ index.html actualizado correctamente.")

if __name__ == "__main__":
    actualizar_index()
