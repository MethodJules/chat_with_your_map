import pandas as pd
import re
from typing import List, Dict, Any
import os

# Komponente: Layer-Resolver

class LayerResolver:
    def __init__(self, layer_df: pd.DataFrame):
        self.layer_df = layer_df
        self.keyword_mapping = self._build_keyword_mapping()

    def _build_keyword_mapping(self):
        # Mapping von Kategorien zu Suchbegriffen
        return {
            "park": ["park", "grünanlage", "grünflächen", "spielplatz", "freiraum"],
            "schule": ["schule", "schulen", "bildung"],
            "kindergarten": ["kita", "kindergarten", "vorschule"],
            "öpnv": ["haltestelle", "öpnv", "s-bahn", "u-bahn", "bus", "bahn"],
            "trafostation": ["trafostation", "umspannwerk", "strom"],
            "toilette": ["toilette", "wc", "sanitär"],
            "fahrrad": ["fahrrad", "radweg", "fahrradweg"],
            "brücke": ["brücke", "überführung"],
            "rathaus": ["rathaus", "verwaltung", "behörde"],
            "baustelle": ["baustelle", "baustellen"],
            "elektro": ["ladestation", "emobility", "elektro", "e-auto"],
            "behinderten": ["behinderten", "barrierefrei"],
            "kamera": ["kamera", "überwachung", "verkehrskamera"],
            "verkehr": ["verkehr", "autobahn", "verkehrslage", "straßenverkehr"],
            "polizei": ["polizei", "polizeiwache", "wache", "reviere", "kripo", "ordnung", "sicherheitsdienst"],
            "krankenhaus": ["krankenhaus", "klinik", "gesundheitszentrum", "notaufnahme", "arzt", "spital", "medizinische einrichtung"],
            "bibliothek": ["bibliothek", "bücherei", "stadtbücherei", "lesesaal", "leseraum", "mediathek", "leihbücherei"],
            "spielplatz": ["spielplatz", "spielplätze", "kinderplatz", "spielbereich", "kinderspielplatz"],
            "see": ["see", "seen", "gewässer", "seeufer", "teich", "weiher", "wasserfläche"],
            "bezirksgrenze": ["grenze", "bezirksgrenze", "stadtgrenze", "stadtteilgrenze", "verwaltungsgrenze"],
            "kultur": ["kultur", "theater", "museum", "konzerthaus", "ausstellung", "veranstaltungshaus"],
            "denkmäler": ["denkmal", "denkmäler", "historisches gebäude", "gedenkstätte", "kulturdenkmal", "gedenken", "geschichtsdenkmal"],
            "parkhaus": ["parkhaus", "parkplätze", "tiefgarage", "auto parken", "parkanlage", "stellplatz"]
        }

    def resolve(self, user_input: str) -> List[str]:
         # Eingabe in Kleinbuchstaben umwandeln
        matches = []
        user_input = user_input.lower()
        for category, keywords in self.keyword_mapping.items():
            if any(keyword in user_input for keyword in keywords):
                filtered = self.layer_df[self.layer_df['Kategorie'].str.lower().str.contains(category)]
                matches.extend(filtered['Layer ID'].tolist())
        return list(set(matches))

# Parser für Benutzerbefehle

class CommandParser:
    def parse(self, user_input: str) -> Dict[str, Any]:
        user_input = user_input.lower()

        # Aktion erkennen
        if any(kw in user_input for kw in ["zeige", "anzeigen", "seh", "will", "möchte"]):
            if "auch" in user_input or "zusätzlich" in user_input:
                action = "zeigen_add"
            else:
                action = "zeigen"
        elif any(kw in user_input for kw in ["nahe", "in der nähe", "umkreis"]):
            action = "filtern_räumlich"
        elif any(kw in user_input for kw in ["mindestens", "mehr als", "größer als"]):
            action = "filtern_eigenschaft"
        elif any(kw in user_input for kw in ["öffne", "öffnen"]):
            action = "öffnen"
        elif any(kw in user_input for kw in ["zoome", "zoomen"]):
            action = "zoomen"
        elif any(kw in user_input for kw in ["messe", "messen"]):
            action = "messen"
        else:
            action = "unbekannt"

        return {
            "action": action,
            "text": user_input
        }

# Zentrale Ausführungseinheit

class MapCommandExecutor:
    def __init__(self, layer_resolver: LayerResolver):
        self.layer_resolver = layer_resolver
        self.current_state = {
            "layers": [],
            "filters": [],
            "actions": []
        }

    def execute(self, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        action = parsed_command["action"]
        text = parsed_command["text"]

        if action.startswith("zeigen"):
            layers = self.layer_resolver.resolve(text)
            if action == "zeigen":
                self.current_state["layers"] = layers
            elif action == "zeigen_add":
                self.current_state["layers"].extend(layers)

        elif action.startswith("filtern"):
            self.current_state["filters"].append(text)

        elif action in ["öffnen", "zoomen", "messen"]:
            self.current_state["actions"].append(action)

        return self.current_state

# Demo & Testausführung

def main():
    # Lade den Pfad zur Datei vom Desktop
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "ChatBot_amin", "Datensaetze_mit_Beschreibung.xlsx")
    layer_df = pd.read_excel(desktop_path)

    # Initialisiere Komponenten
    resolver = LayerResolver(layer_df)
    parser = CommandParser()
    executor = MapCommandExecutor(resolver)

    # Testfälle
    print("--- TESTFÄLLE ---")
    commands = [
        "Zeige mir alle Fahrradstationen in Altona.",
        "Zeige mir auch die Parks an.",
        "Zeige mir die Stationen, die mindestens 5 Fahrräder haben.",
        "Zoome auf Altona.",
        "Öffne die Verkehrsdaten."
    ]

    for command in commands:
        parsed = parser.parse(command)
        state = executor.execute(parsed)
        print(f"\nUser: {command}\nParser: {parsed}\nAktueller Zustand: {state}")

if __name__ == "__main__":
    main()
