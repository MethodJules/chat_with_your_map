import requests
import json

"""
Input: Nutzer gibt einen Ort als Text ein (z. B. „Fahrradstation Altona“).
Schritt 1: Der Ortsname wird extrahiert.
Schritt 2: Script sucht den Ort (z. B. über eine Geocoding-API oder eine lokale Liste) → generiert Daten wie name, address, latitude, longitude.
Output: GeoJSON-Struktur, die direkt ins Masterportal übernommen werden kann.
"""

def get_location_data(place_name, city="Hamburg"):
    """
    Holt Geodaten für einen Ort in Hamburg über die OpenStreetMap Nominatim API
    und gibt diese im GeoJSON-Format zurück.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{place_name}, {city}",
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }
    headers = {
        "User-Agent": "IT-Studienprojekt/1.0"
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(data["lon"]), float(data["lat"])]
            },
            "properties": {
                "name": place_name,
                "display_name": data.get("display_name"),
                "type": data.get("type"),
                "address": data.get("address", {})
            }
        }
    else:
        return {
            "type": "Feature",
            "geometry": None,
            "properties": {"error": f"Ort '{place_name}' nicht gefunden."}
        }


def main():
    # Beispiel-Eingaben von Nutzern
    user_inputs = [
        "Fahrradstation Altona",
        "Hauptbahnhof Hamburg",
        "Elbphilharmonie"
    ]

    features = []
    for place in user_inputs:
        location_data = get_location_data(place)
        features.append(location_data)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    # GeoJSON-Output erzeugen
    with open("locations.geojson", "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=4)

    print("locations.geojson wurde erstellt!")


if __name__ == "__main__":
    main()
