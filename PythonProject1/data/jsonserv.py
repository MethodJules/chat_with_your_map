import json


def json_to_key_value_table(json_string: str):

    try:
        data = json.loads(json_string)
    except json.JSONDecodeError:
        print("Fehler: Der übergebene String ist kein valides JSON.")
        return

    def flatten_json(nested_dict, parent_key='', sep='.'):
        items = []
        for key, value in nested_dict.items():
            new_key = parent_key + sep + key if parent_key else key
            if isinstance(value, dict):
                items.extend(flatten_json(value, new_key, sep=sep))
            else:
                items.append((new_key, value))
        return items

    flat_list = flatten_json(data)
    if not flat_list:
        print("Das JSON-Objekt ist leer.")
        return

    max_key_length = max(len(key) for key, value in flat_list)

    for key, value in flat_list:
        print(f"{key.ljust(max_key_length)} : {value}")

