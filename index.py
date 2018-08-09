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
bot = Bot(command_prefix=prefix, prefix=prefix)


for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension("cogs.%s" % (name))

bot.run(token)
