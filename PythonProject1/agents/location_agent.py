import json
import os
from typing import Optional
from xml.etree.ElementTree import tostring

from dotenv import load_dotenv

# BENÖTIGTE BIBLIOTHEKEN
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# --- IHR BESTEHENDER CODE (leicht angepasst) ---

load_dotenv()

MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct"
IONOS_API_TOKEN = os.getenv("IONOS_API_TOKEN")
endpoint = "https://openai.inference.de-txl.ionos.com/v1/chat/completions"

system_prompt = """
 Du bist ein Stadtplaner und nutzt eine webbasierte GIS Anwendung. Diese Anwendung kann  alle geografischen Orte (z. B. Städte, Länder, Regionen) extrahiere

Gib die extrahierten geografischen Orte in einer nummerierten Liste zurück, ohne zusätzliche Erklärungen. Achte darauf, nur geografische Orte zu extrahieren und keine anderen Entitäten wie Personen, Organisationen oder Produkte.

Generiere die Antwort nur in ein Wort 
 Beispiele:

Text: "Wie lang fließt die Elbe durch Altona?"
Antwort
"Altona"

Text: "Zeige alle S-Bahn Stationen in Wandsbek"
Antwort 
"Wandsbek"
"""


class Location(BaseModel):
    location: str


model = OpenAIModel(
    MODEL_NAME,
    provider=OpenAIProvider(
        base_url='https://openai.inference.de-txl.ionos.com/v1',
        api_key=IONOS_API_TOKEN,
    ),
)

agent = Agent(
    model=model,
    system_prompt=system_prompt,
)
def detect_location(input_text: str) -> dict | None:
    try:
        result = agent.run_sync(input_text)
        return result.output
    except Exception as e:
        print(f"Fehler bei der Location-Extraktion: {e}")
        return None

def geocode_location(location_name: str):
    try:
        geolocator = Nominatim(user_agent="location_agent_app/1.0")
        location_data = geolocator.geocode(location_name)
        if location_data:
            coords = {
                "latitude": location_data.latitude,
                "longitude": location_data.longitude
            }
            print(f"Geokoordinaten für '{location_name}': {coords}")
            return  json.dumps(coords)
        else:
            print(f"Georeferenz für '{location_name}' konnte nicht gefunden werden.")
            return None
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"Fehler beim Geocoding:. {e}")
        return None
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        return None
