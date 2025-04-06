import csv
import os
import json

class FileManager:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file = self._load_file()
    def _load_file(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r') as file:
                return json.load(file)
        return {}


    def json_to_csv(self, csv_file_path):

        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)

            header = ['ID', 'Name', 'URL', 'Type', 'Feature Type', 'Output Format', 'Version', 'Visible']
            writer.writerow(header)

            if isinstance(self.file, list):
                for item in self.file:
                    row = [
                        item.get('id', ''),
                        item.get('name', ''),
                        item.get('url', ''),
                        item.get('typ', ''),
                        item.get('featureType', ''),
                        item.get('outputFormat', ''),
                        item.get('version', ''),
                        'Yes' if item.get('urlIsVisible', False) else 'No'
                    ]
                    writer.writerow(row)
            else:
                raise ValueError("JSON data must be a list of dictionaries.")




