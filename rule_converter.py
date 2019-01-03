import os
import codecs
import json
from datetime import datetime

for file in os.listdir("data/rules/servers"):
    if file.endswith(".json"):
        with open("data/rules/servers/" + file, 'r') as f:
            data = json.load(f)

        for rule in data["rules"]:
            ''' Future shit
            rule["main"] = {
                "text" : rule["rule_text"],
                "date" : str(datetime.utcnow())
            }
            rule["alt"] = {
                "text" : rule["alternate"],
                "date" : str(datetime.utcnow())
            }
            rule.pop("alternate")
            rule.pop("rule_text")
            '''
            rule["edited"] = str(datetime.utcnow())

        with open("data/rules/servers/" + file, 'w+') as f:
            json.dump(data, f, indent=4)