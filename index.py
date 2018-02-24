# -*- coding: utf-8 -*-

import json
import os

from data import Bot
from utils import permissions


with open("config.json") as f:
    data = json.load(f)
    token = data["token"]
    prefix = data["prefix"]

print("Logging in...")
bot = Bot(command_prefix="§", prefix=prefix, pm_help=True)

bot.load_extension("lover")  

bot.run(token)
