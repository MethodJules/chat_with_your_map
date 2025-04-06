from datetime import datetime

from file.file_manager import FileManager


class LayerService:
    def __init__(self):
        self.FILE_NAME = f"./file/layers.json"
        self.file = FileManager(self.FILE_NAME)
    def get_all_layers(self):
        if not self.file.file:
            return "No layers in the file."
        else:
            return self.file.file
    def make_csv(self):
        if not self.file.file:
            return "No layers in the file."
        else:
            self.file.json_to_csv("./file/layers"+datetime.now().strftime("%Y%m%d%H%M%S")+".csv")