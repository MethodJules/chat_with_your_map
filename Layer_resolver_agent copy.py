import pandas as pd
import re

class LayerResolverAgent:
    def __init__(self, excel_path):
        self.df = pd.read_excel(excel_path, sheet_name='Sheet1')
        self.df["Name"] = self.df["Name"].str.lower()
        self.df["description"] = self.df["description"].astype(str).str.lower()
        self.keyword_mapping = self._build_keyword_mapping()

# Hier kannst du die Keywords zuordnen
    def _build_keyword_mapping(self):
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
            "elektro": ["ladestation", "emobility", "elektro"],
            "behinderten": ["behinderten", "barrierefrei"],
            "kamera": ["kamera", "überwachung", "verkehrskamera"],
            "verkehr": ["verkehr", "autobahn", "verkehrslage", "straßenverkehr"],
        # dazu kann hinzugefügt werden
            "polizei": [
            "polizei", "polizeiwache", "wache", "reviere", "kripo", "ordnung", "sicherheitsdienst"],
            "krankenhaus": [
            "krankenhaus", "klinik", "gesundheitszentrum", "notaufnahme", "arzt", 
            "spital", "medizinische einrichtung"],
            "bibliothek": [
            "bibliothek", "bücherei", "stadtbücherei", "lesesaal", "leseraum", 
            "mediathek", "leihbücherei"],
            "spielplatz": [
            "spielplatz", "spielplätze", "kinderplatz", "spielbereich", "kinderspielplatz"],
            "see": [
            "see", "seen", "gewässer", "seeufer", "teich", "weiher", "wasserfläche"],
            "bezirksgrenze": [
            "grenze", "bezirksgrenze", "stadtgrenze", "stadtteilgrenze", "verwaltungsgrenze"],
            "kultur": [
            "kultur", "theater", "museum", "konzerthaus", "ausstellung", "veranstaltungshaus"],
            "denkmäler": [
            "denkmal", "denkmäler", "historisches gebäude", "gedenkstätte", "kulturdenkmal", 
            "gedenken", "geschichtsdenkmal"],
            "parkhaus": [
            "parkhaus", "parkplätze", "tiefgarage", "auto parken", "parkanlage", "stellplatz"]
        }

                


    def resolve_input(self, user_input):
        user_input = user_input.lower()
        matched_ids = set()

        for category, keywords in self.keyword_mapping.items():
            if any(re.search(rf"\b{kw}\b", user_input) for kw in keywords):
                filtered = self.df[
                    self.df["Name"].str.contains(category) |
                    self.df["description"].str.contains(category)
                ]
                matched_ids.update(filtered["ID"].tolist())

        if matched_ids:
            return list(matched_ids)
        else:
            return ["Kein passender Layer gefunden."]

# Beispielnutzung
if __name__ == "__main__":
    agent = LayerResolverAgent("Datensaetze_mit_Beschreibung.xlsx")

    beispiele = [
        "Zeige mir alle Parks",
        "Ich will die T-Stationen sehen",
        "Wo sind die Kindergärten?",
        "Zeige mir die Haltestellen des ÖPNV",
        "Wo finde ich das Rathaus?",
        "Zeige mir die Verkehrskameras",
        "Wo ist der Verkehr am dichtesten?",
        "Gibt es Baustellen auf den Straßen?",
        "Zeig mir die Ladestationen für E-Autos",
        "Gibt es Behindertenparkplätze?"
    ]

    for eingabe in beispiele:
        result = agent.resolve_input(eingabe)
        print(f"Eingabe: {eingabe}\nGefundene Layer-IDs: {result}\n")
