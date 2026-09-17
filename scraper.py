import json
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

URL_TAE = "https://terrassaartsesceniques.cat/programacio/"
URL_LAFACT = "https://www.lafactcultural.cat/programacio/"
URL_TNT = "https://tnt.cat/es/programacio/"

def obtener_eventos_nuevos():
    eventos_encontrados = []
    
    # 1. Extracción en Terrassa Arts Escèniques
    try:
        resp = requests.get(URL_TAE, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for card in soup.select("article, .esdeveniment, .event-card, .type-tribe_events"):
                title_el = card.select_one(".entry-title, .event-title, h2, h3")
                link_el = card.select_one("a[href]")
                date_el = card.select_one(".event-date, .data, time, .tribe-event-date-start")
                place_el = card.select_one(".event-venue, .espai, .tribe-venue")
                price_el = card.select_one(".event-price, .preu, .tribe-tickets-price")
                cat_el = card.select_one(".event-category, .categoria")

                if title_el and link_el:
                    titulo = title_el.get_text(strip=True)
                    url = link_el["href"]
                    fecha_raw = date_el.get_text(strip=True) if date_el else ""
                    lugar = place_el.get_text(strip=True) if place_el else "Teatre Principal / Alegria"
                    precio = price_el.get_text(strip=True) if price_el else "Consultar"
                    categoria = cat_el.get_text(strip=True) if cat_el else "Teatre"

                    eventos_encontrados.append({
                        "fecha": extraer_fecha_iso(fecha_raw),
                        "dia": extraer_nombre_dia(fecha_raw),
                        "hora": extraer_hora(fecha_raw),
                        "actividad": titulo,
                        "lugar": lugar,
                        "categoria": categoria,
                        "precio": precio,
                        "organizador": "Terrassa Arts Escèniques",
                        "url": url
                    })
    except Exception as e:
        print(f"[TAE] Error al extraer: {e}")

    # 2. Extracción en LaFACT Cultural
    try:
        resp = requests.get(URL_LAFACT, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for card in soup.select("article, .card-programacio, .item-programacio, .elementor-post"):
                title_el = card.select_one("h2, h3, .title, .entry-title")
                link_el = card.select_one("a[href]")
                date_el = card.select_one(".date, .fecha, .data")
                price_el = card.select_one(".price, .preu")
                cat_el = card.select_one(".category, .categoria")

                if title_el and link_el:
                    titulo = title_el.get_text(strip=True)
                    url = link_el["href"]
                    fecha_raw = date_el.get_text(strip=True) if date_el else ""
                    precio = price_el.get_text(strip=True) if price_el else "Consultar"
                    categoria = cat_el.get_text(strip=True) if cat_el else "Programació LaFACT"

                    eventos_encontrados.append({
                        "fecha": extraer_fecha_iso(fecha_raw),
                        "dia": extraer_nombre_dia(fecha_raw),
                        "hora": extraer_hora(fecha_raw),
                        "actividad": titulo,
                        "lugar": "La Factoria Cultural",
                        "categoria": categoria,
                        "precio": precio,
                        "organizador": "La Factoria Cultural",
                        "url": url
                    })
    except Exception as e:
        print(f"[LaFACT] Error al extraer: {e}")

    # 3. Extracción en Festival TNT
    try:
        resp = requests.get(URL_TNT, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for card in soup.select("article, .show-card, .espectaculo, .item-tnt"):
                title_el = card.select_one("h2, h3, .title")
                link_el = card.select_one("a[href]")
                date_el = card.select_one(".date, .fecha")
                place_el = card.select_one(".place, .lugar, .espai")
                price_el = card.select_one(".price, .precio, .preu")

                if title_el and link_el:
                    titulo = title_el.get_text(strip=True)
                    url = link_el["href"]
                    fecha_raw = date_el.get_text(strip=True) if date_el else ""
                    lugar = place_el.get_text(strip=True) if place_el else "Terrassa"
                    precio = price_el.get_text(strip=True) if price_el else "Consultar"

                    eventos_encontrados.append({
                        "fecha": extraer_fecha_iso(fecha_raw),
                        "dia": extraer_nombre_dia(fecha_raw),
                        "hora": extraer_hora(fecha_raw),
                        "actividad": titulo,
                        "lugar": lugar,
                        "categoria": "Festival TNT",
                        "precio": precio,
                        "organizador": "Festival TNT",
                        "url": url
                    })
    except Exception as e:
        print(f"[TNT] Error al extraer: {e}")

    return eventos_encontrados

def extraer_fecha_iso(texto):
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', texto)
    if match:
        return match.group(0)
    match_es = re.search(r'(\d{1,2})[\/\.-](\d{1,2})[\/\.-](\d{4})', texto)
    if match_es:
        day, month, year = match_es.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return "2026-10-01"

def extraer_nombre_dia(texto):
    dias = ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte", "Diumenge"]
    for d in dias:
        if d.lower() in texto.lower():
            return d
    return "Dissabte"

def extraer_hora(texto):
    match = re.search(r'(\d{1,2}(?::\d{2})?\s*h)', texto, re.IGNORECASE)
    if match:
        return match.group(1)
    return "20h"

def actualizar_index():
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Extraer los eventos actuales existentes en index.html
    match = re.search(r'const allData = (\[[\s\S]*?\]);', html)
    if not match:
        print("No se encontró la variable allData en index.html")
        return

    try:
        eventos_actuales = json.loads(match.group(1))
    except Exception as e:
        print(f"Error al parsear el JSON existente: {e}")
        return

    nuevos_eventos = obtener_eventos_nuevos()
    
    # Filtrar solo los eventos que no existan previamente (evitar duplicados por URL o título)
    urls_existentes = {e.get("url") for e in eventos_actuales if "url" in e}
    titulos_existentes = {e.get("actividad") for e in eventos_actuales if "actividad" in e}

    agregados = 0
    for ev in nuevos_eventos:
        if ev.get("url") not in urls_existentes and ev.get("actividad") not in titulos_existentes:
            eventos_actuales.append(ev)
            agregados += 1

    if agregados == 0:
        print("No se encontraron eventos nuevos en las webs. Se mantiene index.html intacto.")
        return

    # Ordenar cronológicamente
    eventos_actuales.sort(key=lambda x: x.get("fecha", "9999-99-99"))

    # Reemplazar allData con la lista combinada actualizada
    json_actualizado = json.dumps(eventos_actuales, ensure_ascii=False, indent=6)
    nuevo_html = re.sub(
        r'const allData = \[[\s\S]*?\];',
        f'const allData = {json_actualizado};',
        html
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(nuevo_html)

    print(f"✅ Se han añadido {agregados} eventos nuevos sin modificar la agenda existente.")

if __name__ == "__main__":
    actualizar_index()
