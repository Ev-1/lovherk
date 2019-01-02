import os
import json
import codecs


class Settings:
    def __init__(self, default_prefix):
        self.DATA_PATH = 'data/settings/'
        self.SETTINGS_PATH = self.DATA_PATH + 'settings.json'
        self.default_prefix = default_prefix

        if not os.path.exists(self.DATA_PATH):
            os.makedirs(self.DATA_PATH)

        if not os.path.isfile(self.SETTINGS_PATH):
            with codecs.open(self.SETTINGS_PATH, "w+", encoding='utf8') as f:
                json.dump({"prefixes": {}}, f, indent=4)

        with codecs.open(self.SETTINGS_PATH, "r", encoding='utf8') as f:
            self.settings = json.load(f)

    def get_prefix(self, server_id):
        server_id = str(server_id)
        if server_id in self.settings["prefixes"].keys():
            return self.settings["prefixes"][server_id]
        else:
            return self.default_prefix

    def set_prefix(self, server_id, prefixes):
        if prefixes is None:
            self.settings["prefixes"].pop(str(server_id), None)
        else:
            self.settings["prefixes"][str(server_id)] = prefixes
        with codecs.open(self.SETTINGS_PATH, "w", encoding='utf8') as f:
            json.dump(self.settings, f, indent=4)
