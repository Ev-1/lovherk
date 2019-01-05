import os
import codecs
import json
from datetime import datetime

class RuleManager:

    SETTINGS_JSON = {
                        "auto_update": [],
                        "react_rules": [],
                        "default_rule": None,
                        "rule_prefix": "§"
                    }

    def __init__(self, server_id, path):

        if not os.path.exists(path):
            os.makedirs(path)

        self._path = path + str(server_id) + '.json'

        if not os.path.isfile(self._path):
            with codecs.open(self._path, "w+", encoding='utf8') as write_file:
                json.dump({
                            "id": int(server_id),
                            "rules": [],
                            "settings": self.SETTINGS_JSON
                        }, write_file, indent=4)

        with codecs.open(self._path, "r", encoding='utf8') as read_file:
            self._server = json.load(read_file)

    def add_rule(self, name, rule_text, alternaterule: str=None):
        if name is not None:
            name = name.lower()
        if any(rule for rule in self._server["rules"] if rule["name"] == name):
            return False

        if rule_text is None:
            rule_text = ""

        self._server["rules"].append({
            "name": name,
            "rule_text": rule_text,
            "alternate": alternaterule,
            "edited": str(datetime.utcnow())
        })
        self._save()
        return True

    def remove_rule(self, name, alternate: bool=False):
        # Add handling for removing rules with autoupdate
        if name is not None:
            name = name.lower()
        _rule = self._get_rule(name)
        if _rule is not None:
            if alternate:
                _rule["alternate"] = None
                self.remove_link_setting("react_rules", "name", name)
            else:
                self._server["rules"].remove(_rule)
                self.remove_link_setting("auto_update", "name", name)
                self.remove_link_setting("react_rules", "name", name)
                if name == self.get_settings("default_rule"):
                    self.change_setting("default_rule", None)
            self._save()
            return True
        return False

    def edit_rule(self, name, new_rule_text, alternate: bool=False):
        if name is not None:
            name = name.lower()
        _rule = self._get_rule(name)
        if _rule is not None:
            if alternate:
                _rule["alternate"] = new_rule_text
            else:
                _rule["rule_text"] = new_rule_text
            _rule["edited"] = str(datetime.utcnow())
            self._save()
            return True
        return False

    def get_rule_text(self, name, alternate: bool=False):
        if name is not None:
            name = name.lower()
        _rule = self._get_rule(name)
        if _rule is not None:
            if alternate:
                return _rule["alternate"], _rule["edited"]
            else:
                return _rule["rule_text"], _rule["edited"]
        return None, None

    def get_rules_formatted(self, alternate: bool=False):
        rules = self._get_rule_names(alternate)
        formatted_rules = ""
        for rule in rules:
            if rule == self._server["settings"]["default_rule"]:
                formatted_rules = '•' + rule.capitalize() + '\n' \
                                      + formatted_rules
            else:
                formatted_rules += '•' + rule.capitalize() + '\n'
        return formatted_rules

    def add_link_setting(self, setting, name, link):
        if name is not None:
            name = name.lower()
        rule = self._get_rule(name)
        if rule is not None:
            if any(msg for msg in self._server["settings"][setting]
                   if msg["link"] == link):
                return -1
            self._server["settings"][setting].append({"name": name,
                                                     "link": link})
            self._save()
            return True
        return False

    def remove_link_setting(self, setting, match_type, to_match):
        if to_match is not None:
            to_match = to_match.lower()

        removed = False
        for message in reversed(self._server["settings"][setting]):
            if message[match_type] == to_match:
                self._server["settings"][setting].remove(message)
                removed = True
        self._save()
        return removed

    def get_settings(self, setting):
        return self._server["settings"][setting]

    def change_setting(self, setting, value):
        self._server["settings"][setting] = value
        self._save()

    def _get_rule_names(self, alternate):
        if alternate:
            return [rule["name"] for rule in self._server["rules"]
                    if rule["alternate"] is not None]
        else:
            return [rule["name"] for rule in self._server["rules"]]

    def _get_rule(self, name=None):
        return next((rule for rule in self._server["rules"]
                     if rule["name"] == name), None)

    def _save(self):
        with codecs.open(self._path, "w", encoding='utf8') as write_file:
            json.dump(self._server, write_file, indent=4)
