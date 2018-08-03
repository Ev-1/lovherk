# -*- coding: utf-8 -*-

import json
import os
import codecs

from data import Bot
from utils import permissions

with codecs.open("config.json", 'r',encoding='utf8') as f:
    data = json.load(f)
    token = data["token"]
    prefix = data["prefix"]

print("Logging in...")
print(prefix)
bot = Bot(command_prefix=prefix, prefix=prefix, pm_help=True)

bot.load_extension("lover")  

bot.run(token)
