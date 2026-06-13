import codecs
import json
import logging
import os
import time

import discord
from discord.ext import commands
from discord.flags import MemberCacheFlags

from cogs.utils.settings import Settings

log = logging.getLogger("lovherk")


def _get_prefix(bot, message):
    if not message.guild:
        prefixes = bot.settings.default_prefix
    else:
        prefixes = bot.settings.get_prefix(message.guild.id)
    return commands.when_mentioned_or(*prefixes)(bot, message)


class LovHerk(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=_get_prefix,
                         intents=intents,
                         member_cache_flags=MemberCacheFlags.from_intents(intents)
                         )

        # This is kinda stupid, TODO: make not stupid
        with codecs.open("config.json", 'r', encoding='utf8') as f:
            self.config = json.load(f)

        self.settings = Settings(self.config['default_prefix'])
        self.uptime = time.time()

    async def setup_hook(self):
        # Load all cogs once, before connecting. on_ready can fire multiple
        # times (every reconnect), which would raise ExtensionAlreadyLoaded.
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                try:
                    await self.load_extension(f"cogs.{name}")
                    log.info("Loaded cog: %s", name)
                except Exception:
                    log.exception("Failed to load cog: %s", name)

    async def on_ready(self):
        log.info("Logged in as %s in %d servers (discord.py %s)",
                 self.user, len(self.guilds), discord.__version__)

        await self.change_presence(activity=discord.Game(type=0,
                                   name=self.config["playing"]),
                                   status=discord.Status.online)

    async def on_command_error(self, ctx, err):
        if (isinstance(err, commands.MissingRequiredArgument) or
                isinstance(err, commands.BadArgument)):
            formatter = ctx.bot.formatter
            if ctx.invoked_subcommand is None:
                _help = await formatter.format_help_for(ctx, ctx.command)
            else:
                _help = await formatter.format_help_for(ctx,
                                                        ctx.invoked_subcommand)

            for message in _help:
                await ctx.send(message)

        if isinstance(err, commands.CommandInvokeError):
            # The actual error is wrapped in err.original. Log it with a
            # traceback so command failures are debuggable instead of silent.
            log.error("Error invoking command %s",
                      ctx.command, exc_info=err.original)

        elif isinstance(err, commands.NoPrivateMessage):
            await ctx.send("Denne kommandoen er ikke tilgjengelig i DMs")

        elif isinstance(err, commands.CheckFailure):
            pass

        elif isinstance(err, commands.CommandNotFound):
            pass

    def run(self):
        # Disable discord.py's own logging setup; we configure the root
        # logger ourselves in run_bot() so our logs share the same format.
        try:
            super().run(self.config["token"], reconnect=True, log_handler=None)
        except Exception:
            log.exception("Bot stopped with an unhandled exception")


def run_bot():
    # Set LOG_LEVEL=DEBUG in the environment to get more verbose output.
    level = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(),
                    logging.INFO)
    discord.utils.setup_logging(level=level)
    bot = LovHerk()
    bot.run()

if __name__ == '__main__':
    run_bot()
