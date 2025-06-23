from xml.etree.ElementTree import tostring

from agents.actiontype_agent import detect_action_type
from agents.dataset_agent import resolve_dataset
from agents.location_agent import detect_location, geocode_location
from data.jsonserv import json_to_key_value_table

print("Hallo")
input_text = "Zoome mir auf Faktor 2 in wandsbek."

detect_action_type(input_text)
resolve_dataset(input_text)
detect_location(input_text)

extracted_data = detect_location(input_text)
coordinates = geocode_location(extracted_data)

json_to_key_value_table(detect_action_type(input_text))
json_to_key_value_table(resolve_dataset(input_text))
json_to_key_value_table(coordinates)


