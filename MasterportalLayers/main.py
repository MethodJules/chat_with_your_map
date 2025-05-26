from agents.actiontype_agent import detect_action_type
from agents.dataset_agent import resolve_dataset
from agents.location_agent import detect_location

print("Hallo")
input_text = "Zeige mir alle Fahrradstationen in Altona."
input_text2 = "Zeige mir S-Bahn in Hamburg"

detect_action_type(input_text)
resolve_dataset(input_text2)
detect_location(input_text2)
