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

def obtener_eventos_tae():
    eventos = []
    try:
        resp = requests.get(URL_TAE, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("article, .esdeveniment, .event-card, .type-tribe_events")
            for card in cards:
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

                    eventos.append({
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
    return eventos

def obtener_eventos_lafact():
    eventos = []
    try:
        resp = requests.get(URL_LAFACT, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("article, .card-programacio, .item-programacio, .elementor-post")
            for card in cards:
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

                    eventos.append({
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
    return eventos

def obtener_eventos_tnt():
    eventos = []
    try:
        resp = requests.get(URL_TNT, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("article, .show-card, .espectaculo, .item-tnt")
            for card in cards:
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

                    eventos.append({
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
    return eventos

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
    todos_eventos = []
    todos_eventos.extend(obtener_eventos_tae())
    todos_eventos.extend(obtener_eventos_lafact())
    todos_eventos.extend(obtener_eventos_tnt())

    if not todos_eventos:
        print("No se encontraron nuevos eventos en las webs. No se modifica index.html.")
        return

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    json_eventos = json.dumps(todos_eventos, ensure_ascii=False, indent=6)

    nuevo_html = re.sub(
        r'const allData = \[[\s\S]*?\];',
        f'const allData = {json_eventos};',
        html
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(nuevo_html)

    print("✅ ¡index.html actualizado correctamente con datos extraídos!")

if __name__ == "__main__":
    actualizar_index()
