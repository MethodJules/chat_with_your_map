import pandas as pd
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
IONOS_API_TOKEN = os.getenv("IONOS_API_TOKEN")
MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct"
CSV_PATH = "./data/csv datei.csv"

# Load CSV as dictionary
df = pd.read_csv(CSV_PATH)
layer_dict = {row["Name"]: row["ID"] for _, row in df.iterrows()}

# System prompt
layer_list = "\n".join([f"- {name} (ID: {layer_id})" for name, layer_id in layer_dict.items()])
system_prompt = f"""
Du bist ein GIS-Datenexperte. Du erhältst einen deutschen Text und musst bestimmen, welche Layer aus einer GIS-Anwendung am besten passen.

Verfügbare Layer:
{layer_list}

Deine Antwort muss JSON sein im Format:
{{
  "layers": ["layer_id_1", "layer_id_2"],
  "explanation": "Kurze Begründung, warum diese Layer passen"
}}
"""

# Output model
class DatasetMatch(BaseModel):
    layers: list[str]
    explanation: str

# Model config
model = OpenAIModel(
    MODEL_NAME,
    provider=OpenAIProvider(
        base_url="https://openai.inference.de-txl.ionos.com/v1",
        api_key=IONOS_API_TOKEN,
    ),
)

# Agent init
agent = Agent(
    model=model,
    system_prompt=system_prompt,
)

# Entry function
def resolve_dataset(input_text: str) -> DatasetMatch:
    result = agent.run_sync(input_text)
    print(result)
