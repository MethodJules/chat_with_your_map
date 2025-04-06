from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from service.layer_service import LayerService
import ollama

model_name = 'mistral'

def add_two_numbers(a: int, b: int) -> int:
    return a + b

messages = [
    {"role": "system", "content": "You can do math by calling a function 'add_two_numbers'."},
    {"role": "user", "content": "gib mir die Bunden von 4 und 2."},
]

layer_service = LayerService()


response = ollama.chat(model=model_name, messages=messages, tools=[add_two_numbers])





app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:2025"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    layer_service.make_csv()
    return layer_service.get_all_layers()
    #return "Bot:", response['message']['tool_calls'][0]['function']['arguments']['a'] + response['message']['tool_calls'][0]['function']['arguments']['b']

