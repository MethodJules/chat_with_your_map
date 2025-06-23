import os

from dotenv import load_dotenv

MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct"
#MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
load_dotenv()
IONOS_API_TOKEN = os.getenv("IONOS_API_TOKEN")
endpoint = "https://openai.inference.de-txl.ionos.com/v1/chat/completions"
system_prompt = """
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
 
 Text: "Zoome um den Faktor 5 ?"
 Antwort (Json):{
 "action":"Zoomen",
 "zoom": 5,
 explanation:""
 }

 Text: "Wie lang fließt die Elbe durch Altona?"
 Antwort (JSON): {
 "action": "Messen",
 "explanation": "Die Länge der Elbe in Altona zu bestimmen, erfordert eine räumliche Messung entlang des Flussverlaufs, was der Messaktion entspricht."
 }
"""
input_text = "Zeige mir alle Fahrradstationen in Altona."
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel


class Action(BaseModel):
    action: str
    explanation: str


model = OpenAIModel(
    MODEL_NAME,  # model library available at https://www.together.ai/models
    provider=OpenAIProvider(
        base_url='https://openai.inference.de-txl.ionos.com/v1',
        api_key=IONOS_API_TOKEN,
    ),
)

agent = Agent(
    model=model,
    system_prompt=system_prompt,
)


def detect_action_type(input_text: str) :
    result = agent.run_sync(input_text)
    return result.output
