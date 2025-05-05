import os

from fastapi import FastAPI
import requests

app = FastAPI()
PROMPT = """
Du bist ein Stadtplaner und nutzt eine webbasierte GIS Anwendung. Diese Anwendung kann verschiedene Aktionen ausführen. Diese sind:

Messen
Zeigen
Öffnen
Zoomen
Berechnen
Aktivieren

Deine Aufgabe ist es, aus einem deutschen Text die richtige Aktion zuzuordnen. Begründe dabei, warum du diese Zuordnung gemacht hast.

Antworte im JSON-Format mit den Attributen
action: Aktionsklasse
explanation: deine Erklärung für die Zuordnung

Beispiel:

Text: "Wie lang fließt die Elbe durch Altona?"
Antwort (JSON): {
"action": "Messen",
"explanation": "Die Länge der Elbe in Altona zu bestimmen, erfordert eine räumliche Messung entlang des Flussverlaufs, was der Messaktion entspricht."
}

Text: "{input_text}"
Antwort (JSON):

"""

IONOS_API_TOKEN = "eyJ0eXAiOiJKV1QiLCJraWQiOiIyYzU5YWZjOS0yZTIyLTRiZjUtODRkNy1jZWZiNmYzNTUzY2UiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJpb25vc2Nsb3VkIiwiaWF0IjoxNzQ1ODU4NjgzLCJjbGllbnQiOiJVU0VSIiwiaWRlbnRpdHkiOnsicm9sZSI6Im93bmVyIiwicmVnRG9tYWluIjoiaW9ub3MuZGUiLCJyZXNlbGxlcklkIjoxLCJ1dWlkIjoiMTUwNTI3YjYtNTliNi00NTJiLWE5N2UtYjkwYTg0MjVhYTY2IiwicHJpdmlsZWdlcyI6WyJEQVRBX0NFTlRFUl9DUkVBVEUiLCJTTkFQU0hPVF9DUkVBVEUiLCJJUF9CTE9DS19SRVNFUlZFIiwiTUFOQUdFX0RBVEFQTEFURk9STSIsIkFDQ0VTU19BQ1RJVklUWV9MT0ciLCJQQ0NfQ1JFQVRFIiwiQUNDRVNTX1MzX09CSkVDVF9TVE9SQUdFIiwiQkFDS1VQX1VOSVRfQ1JFQVRFIiwiQ1JFQVRFX0lOVEVSTkVUX0FDQ0VTUyIsIks4U19DTFVTVEVSX0NSRUFURSIsIkZMT1dfTE9HX0NSRUFURSIsIkFDQ0VTU19BTkRfTUFOQUdFX01PTklUT1JJTkciLCJBQ0NFU1NfQU5EX01BTkFHRV9DRVJUSUZJQ0FURVMiLCJBQ0NFU1NfQU5EX01BTkFHRV9MT0dHSU5HIiwiTUFOQUdFX0RCQUFTIiwiQUNDRVNTX0FORF9NQU5BR0VfRE5TIiwiTUFOQUdFX1JFR0lTVFJZIiwiQUNDRVNTX0FORF9NQU5BR0VfQ0ROIiwiQUNDRVNTX0FORF9NQU5BR0VfVlBOIiwiQUNDRVNTX0FORF9NQU5BR0VfQVBJX0dBVEVXQVkiLCJBQ0NFU1NfQU5EX01BTkFHRV9OR1MiLCJBQ0NFU1NfQU5EX01BTkFHRV9LQUFTIiwiQUNDRVNTX0FORF9NQU5BR0VfTkVUV09SS19GSUxFX1NUT1JBR0UiLCJBQ0NFU1NfQU5EX01BTkFHRV9BSV9NT0RFTF9IVUIiLCJDUkVBVEVfTkVUV09SS19TRUNVUklUWV9HUk9VUFMiLCJBQ0NFU1NfQU5EX01BTkFHRV9JQU1fUkVTT1VSQ0VTIl0sImlzUGFyZW50IjpmYWxzZSwiY29udHJhY3ROdW1iZXIiOjM1NTYxMDU0fSwiZXhwIjoxNzUxMDQyNjgzfQ.huOVy_0XmcaqPakgCFWdzAfuxw0ix4AkhXTNGPwysrKvk28zUQxBgNpLTCXwB_B2IbX16C6vp1FWFS0SKhB8e2b3SR9MWOxTEvPzLqm1rqZ-TzDAHJMImQ_RgTDRF1kpGJRKy1HWEjL8tYT8vT1KYCZMZ94kBqSs7zZN82wAFw7wOmWNwADxwb1H2Zksr-cotwM5WOzWaLtmankkQ8ZnFIVT4KqXFg8HcN6jVPsGnTmf-zpTOOQEhk4j5T9ngBEpzuwisJUrv5b-fOiQVLVOO_iRiKatrPF-BlYzWB6gzgVniv6MC4MGCFgZIUGn6xbIVWFoJB6uBt2NLzzfXLQTZw"
MODEL_NAME = "Llama 3.3 Instruct"
endpoint = "https://openai.inference.de-txl.ionos.com/v1/models"

header = {
    "Authorization": f"Bearer {IONOS_API_TOKEN}",
    "Content-Type": "application/json"
}

body = {
    "model": MODEL_NAME,
    "messages": PROMPT,
}

@app.get("/")
def get_json():
    return requests.post(endpoint, json=body, headers=header).json()

