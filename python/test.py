import requests

#MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"
MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct"
IONOS_API_TOKEN = "eyJ0eXAiOiJKV1QiLCJraWQiOiJmMjA3YTk0OS1mM2NmLTQ0NzUtOTNmNi05OGQ5MTQxODE1OGUiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJpb25vc2Nsb3VkIiwiaWF0IjoxNzQ2NTQzMjQ4LCJjbGllbnQiOiJVU0VSIiwiaWRlbnRpdHkiOnsicHJpdmlsZWdlcyI6WyJBQ0NFU1NfQU5EX01BTkFHRV9BSV9NT0RFTF9IVUIiXSwidXVpZCI6ImEwNjMxN2EyLWRiNDktNDFmYi05ZDc0LWY1ZDhhM2M5MTUxYyIsInJlc2VsbGVySWQiOjEsInJlZ0RvbWFpbiI6Imlvbm9zLmRlIiwicm9sZSI6InVzZXIiLCJjb250cmFjdE51bWJlciI6MzU1NjEwNTQsImlzUGFyZW50IjpmYWxzZX0sImV4cCI6MTc1NDMxOTI0OH0.IhdDLdPnrx1ZKQ1YiMRQ1cSnV0LD0Gx4yuYfB8RGOZjWbHph1omqqw8gSfg2vEv5sk1H_FtFP0VFPGLGry6wc0ouXq7Y-geBftfgAFTV1vhR6D_cTkgaKKHTMHDpE0vNCBMb0vulx9ariMJQ1bsg6lecirVnZipygos4GcBGbmGCeAEL9amC7qT5W43PS8m30nvJ1fGwQDz-ebipeQ0VUnc4rVNy2rfbtdblHzguwaXNY38-H4FU6i4H8QuTV6GO_8PHtVka2qaUarqgdpbw0e3sK9zi67GQn6WLj22PVoUgV3CiAvgws6ZSiXy_-enssCcjzNVBH_5A1W1244BvyQ"
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
 
 Text: "Wie lang fließt die Elbe durch Altona?"
 Antwort (JSON): {
 "action": "Messen",
 "explanation": "Die Länge der Elbe in Altona zu bestimmen, erfordert eine räumliche Messung entlang des Flussverlaufs, was der Messaktion entspricht."
 }
"""

input_text = "Zeige mir alle Fahrradstationen in Altona."
PROMPT = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": input_text}
  ]

#endpoint = "https://openai.inference.de-txl.ionos.com/v1/models"
endpoint = "https://openai.inference.de-txl.ionos.com/v1/chat/completions"

 
header = {
     "Authorization": f"Bearer {IONOS_API_TOKEN}",
     "Content-Type": "application/json"
}
 
body = {
     "model": MODEL_NAME,
     "messages": PROMPT,
}

result = requests.post(endpoint, json=body, headers=header).json()
#result = requests.get(endpoint, headers=header).json()
print(result)
