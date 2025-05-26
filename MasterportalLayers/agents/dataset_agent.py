import pandas as pd
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel
import os
from dotenv import load_dotenv

IONOS_API_TOKEN = "eyJ0eXAiOiJKV1QiLCJraWQiOiJmMjA3YTk0OS1mM2NmLTQ0NzUtOTNmNi05OGQ5MTQxODE1OGUiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJpb25vc2Nsb3VkIiwiaWF0IjoxNzQ2NTQzMjQ4LCJjbGllbnQiOiJVU0VSIiwiaWRlbnRpdHkiOnsicHJpdmlsZWdlcyI6WyJBQ0NFU1NfQU5EX01BTkFHRV9BSV9NT0RFTF9IVUIiXSwidXVpZCI6ImEwNjMxN2EyLWRiNDktNDFmYi05ZDc0LWY1ZDhhM2M5MTUxYyIsInJlc2VsbGVySWQiOjEsInJlZ0RvbWFpbiI6Imlvbm9zLmRlIiwicm9sZSI6InVzZXIiLCJjb250cmFjdE51bWJlciI6MzU1NjEwNTQsImlzUGFyZW50IjpmYWxzZX0sImV4cCI6MTc1NDMxOTI0OH0.IhdDLdPnrx1ZKQ1YiMRQ1cSnV0LD0Gx4yuYfB8RGOZjWbHph1omqqw8gSfg2vEv5sk1H_FtFP0VFPGLGry6wc0ouXq7Y-geBftfgAFTV1vhR6D_cTkgaKKHTMHDpE0vNCBMb0vulx9ariMJQ1bsg6lecirVnZipygos4GcBGbmGCeAEL9amC7qT5W43PS8m30nvJ1fGwQDz-ebipeQ0VUnc4rVNy2rfbtdblHzguwaXNY38-H4FU6i4H8QuTV6GO_8PHtVka2qaUarqgdpbw0e3sK9zi67GQn6WLj22PVoUgV3CiAvgws6ZSiXy_-enssCcjzNVBH_5A1W1244BvyQ"

MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct"
CSV_PATH = "./data/csv datei.csv"

df = pd.read_csv(CSV_PATH)
layer_dict = {row["Name"]: row["ID"] for _, row in df.iterrows()}

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

class DatasetMatch(BaseModel):
    layers: list[str]
    explanation: str

model = OpenAIModel(
    MODEL_NAME,
    provider=OpenAIProvider(
        base_url="https://openai.inference.de-txl.ionos.com/v1",
        api_key=IONOS_API_TOKEN,
    ),
)

agent = Agent(
    model=model,
    system_prompt=system_prompt,
)

def resolve_dataset(input_text: str) -> DatasetMatch:
    result = agent.run_sync(input_text)
    print(result)
