import discord
import re
import asyncio
import typing
import os
import codecs
import json

from discord.ext import commands


class RuleManager(object):

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
            "alternate": alternaterule
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
            self._save()
            return True
        return False

    def get_rule_text(self, name, alternate: bool=False):
        if name is not None:
            name = name.lower()
        _rule = self._get_rule(name)
        if _rule is not None:
            if alternate:
                return _rule["alternate"]
            else:
                return _rule["rule_text"]
        return None

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


class Rules:

    DATA_PATH = 'data/rules/'
#    EMOJI_PATH = DATA_PATH + 'react_emoji.json'
    REACT_MSGS = DATA_PATH + 'react_msg_id.json'
    SERVERS_PATH = DATA_PATH + 'servers/'

    def __init__(self, bot):
        if not os.path.exists(self.DATA_PATH):
            os.makedirs(self.DATA_PATH)

        if not os.path.isfile(self.REACT_MSGS):
            with codecs.open(self.REACT_MSGS, "w+", encoding='utf8') as f:
                # "0"-id because empty lists makes json angry
                json.dump([111111111111111111], f, indent=4)

        with codecs.open(self.REACT_MSGS, "r", encoding='utf8') as f:
            self._react_messages = json.load(f)

        self.bot = bot
        self.emoji = '\N{INCOMING ENVELOPE}'

    @commands.guild_only()
    @commands.command(name="lov")
    async def rules(self, ctx,
                    lov: typing.Union[int, str]=None, *, num: str=None):
        """
        Se reglene i lovherket.
        """

        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)

        default = True

        if isinstance(lov, int):
            if num is None:
                num = str(lov)
            else:
                num = str(lov) + " " + num
            lov = rules.get_settings("default_rule")
        else:
            default = False

        rule_text = rules.get_rule_text(lov)

        if rule_text is None:
            await ctx.send('**Liste over lovene i lovherket:**\n' +
                           f'{rules.get_rules_formatted()}')
            return

        if rule_text == "":
            await ctx.send("Denne regelen er helt tom.")
            return

        # Get only specified rules
        if num is not None:
            await ctx.message.delete()
            partial_rules = ""
            for rule in num.split():
                lovregex = r"(§ *" + re.escape(rule) + r"[a-z]?: [\S ]*)"
                m = re.search(lovregex, rule_text)
                if m is not None:
                    partial_rules += m.groups()[0] + "\n"

            if partial_rules == "":
                await ctx.send(f'Fant ikke reglene du ser etter')
            else:
                if not default:
                    partial_rules = f'**I reglene for {lov}:**\n' \
                        + partial_rules
                await ctx.send(partial_rules)
        else:
            await ctx.send(rule_text)

    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.group(name="lovset")
    async def _rule_settings(self, ctx):
        """
        Innstillinger for regler.
        """
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command('help'),
                             ctx.command.qualified_name)

    @_rule_settings.command(name="ny")
    async def newrules(self, ctx, lov, *, newrule: str=None):
        """
        Legger til et nytt sett med regler i lovherket.
        """
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        added = rules.add_rule(lov, newrule)

        if not added:
            await ctx.send("Det finnes allerede regler med det navnet.")
        else:
            await ctx.send("Regler laget")

    @_rule_settings.command(name="plaintext")
    async def plaintext(self, ctx, lov):
        """
        Sender reglene så de enkelt kan kopieres med formatering.
        """
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        rule_text = rules.get_rule_text(lov)

        if rule_text is None:
            await ctx.send("Sjekk at du skrev riktig.")
        else:
            await ctx.send("```\n" + rule_text + "\n```")

    @_rule_settings.command(name="fjern")
    async def removerules(self, ctx, lov):
        """
        Fjerner regler fra lovherket.
        """
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        await self._remove_reactions(ctx, lov)
        removed = rules.remove_rule(lov)

        if removed:
            await ctx.send("Regler fjernet")
        else:
            await ctx.send("Reglene du skrev inn finnes ikke")

    @_rule_settings.command(name="oppdater")
    async def updaterules(self, ctx, lov, *, newrule):
        """
        Oppdaterer lover i lovherket.
        """
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        edited = rules.edit_rule(lov, newrule)
        if edited:
            await ctx.send("Oppdaterer meldinger")
            await self._update_messages(ctx, lov)
            await ctx.send("Regler oppdatert")
        else:
            await ctx.send("Sjekk at du skrev riktig.")

    @_rule_settings.command(name="default")
    async def set_default_rule(self, ctx, lov):
        """
        Setter default regler.
        """
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        rule_text = rules.get_rule_text(lov)

        if rule_text is None:
            await ctx.send(f'Den regelen er ikke i lovherket.\n\n' +
                            '**Liste over lovene i lovherket:**\n' +
                            f'{rules.get_rules_formatted()}')
            return

        rules.change_setting("default_rule", lov.lower())
        await ctx.send(f'{lov} er nå serverens default regel')

    """
    Auto rules
    """

    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.group(name="autoset")
    async def _auto_settings(self, ctx):
        """
        Innstillinger for automatisk regeloppdatering.
        """
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command('help'),
                             ctx.command.qualified_name)

    @_auto_settings.command(name="post")
    async def postauto(self, ctx, lov):
        """
        Sender en melding som automatisk oppdateres når reglene oppdateres.
        """
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        rule_text = rules.get_rule_text(lov)

        if rule_text is None:
            await ctx.send('Sjekk at reglene finnes.\n' +
                           '**Liste over lovene i lovherket:**\n' +
                           f'{rules.get_rules_formatted()}')
            return

        if rule_text == "":
            await ctx.send("Den regelen er helt tom.")
            return

        msg = await ctx.send(rule_text)
        added = rules.add_link_setting('auto_update',
                                       lov,
                                       f'{self._format_message_link(msg)}')

        conf_msg = await ctx.send("Meldingen oppdateres nå automatisk")
        await asyncio.sleep(5)
        await conf_msg.delete()

    @_auto_settings.command(name="add")
    async def autorules(self, ctx, lov, link):
        """
        Setter en gammel melding til å automatisk oppdateres når regler endres.
        """
        msg = await self._get_linked_message(ctx, link)
        if msg is None:
            await ctx.send("Klarte ikke finne meldingen")
            return
        if msg.author != self.bot.user:
            await ctx.send("Sjekk at meldingen tilhører botten")
            return

        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        added = rules.add_link_setting('auto_update',
                                       lov,
                                       f'{self._format_message_link(msg)}')

        if added == -1:
            await ctx.send("Melding allerede satt til å oppdateres automatisk")
        elif added:
            await ctx.send("Melding satt til å oppdateres automatisk")
        else:
            await ctx.send("Reglene du skrev inn finnes ikke")

        await ctx.send("Oppdaterer meldinger")
        await self._update_messages(ctx, lov)
        await ctx.send("Oppdatert")

    @_auto_settings.command(name="liste")
    async def _auto_list(self, ctx):
        """
        Gir en liste over meldinger som er satt til å oppdateres automatisk.
        """
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        auto_update_messages = rules.get_settings('auto_update')

        list_message = '**Meldinger satt til autooppdatering:**\n'

        if len(auto_update_messages) == 0:
            await ctx.send("Ingen meldinger er satt til autooppdatering")
            return

        for message in auto_update_messages:
            list_message += f'{message["name"]}: {message["link"]}\n'

        await ctx.send(list_message)

    @_auto_settings.command(name="fjern")
    async def remove_auto(self, ctx, link):
        """
        Fjerner en melding fra lista av meldinger som oppdateres automatisk.
        """
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        removed = rules.remove_link_setting("auto_update", "link", link)
        if removed:
            await ctx.send("autooppdatering fjernet")
        else:
            await ctx.send("Sjekk at linken er i bruk med §auto liste")

    @_auto_settings.command(name="fiks")
    async def fixauto(self, ctx):
        """
        Prøver å oppdatere meldingene som skal oppdateres automatisk.
        """
        await ctx.send("Oppdaterer meldinger")
        await self._update_messages(ctx)
        await ctx.send("Oppdatert")

    """
    React rules
    """
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.group(name="reactset")
    async def _react_settings(self, ctx):
        """
        Innstillinger for react-regles.
        """
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command('help'),
                             ctx.command.qualified_name)

    @_react_settings.command(name="oppdater")
    async def edit_alternate(self, ctx, lov, *, newrule):
        """
        Oppdaterer reaksjons-regler i lovherket.
        """
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        edited = rules.edit_rule(lov, newrule, alternate=True)
        if edited:
            await ctx.send("Alternative regler oppdatert")
        else:
            await ctx.send("Sjekk at du skrev riktig.")

    @_react_settings.command(name="fjern")
    async def remove_alternate(self, ctx, lov):
        """
        Fjerner reaksjons-regler fra lovherket.
        """
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        removed = rules.remove_rule(lov, alternate=True)
        if removed:
            await ctx.send("Alternative regler fjernet")
        else:
            await ctx.send("Reglene du skrev inn finnes ikke")

    @_react_settings.command(name="vis")
    async def show_alternate(self, ctx, lov: str=None):
        """
        Viser reaksjons-regler fra lovherket.
        """
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        rule_text = rules.get_rule_text(lov, alternate=True)
        if rule_text is not None:
            await ctx.send("```\n" + rule_text + "\n```")
        else:
            await ctx.send('**Liste over react-regler i lovherket:**\n' +
                           f'{rules.get_rules_formatted(alternate=True)}')

    @_react_settings.command(name="liste")
    async def _react_list(self, ctx):
        """
        Gir en liste over meldinger som er satt til å oppdateres automatisk.
        """
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        react_messages = rules.get_settings('react_rules')

        list_message = '**Meldinger med react-regler:**\n'

        if len(react_messages) == 0:
            await ctx.send("Ingen meldinger er satt opp for reacts")
            return

        for message in react_messages:
            list_message += f'{message["name"]}: {message["link"]}\n'

        await ctx.send(list_message)

    @_react_settings.command(name="link")
    async def link_alternate(self, ctx, lov, link):
        """
        Setter en gammel melding til å automatisk oppdateres når regler endres.
        """
        msg = await self._get_linked_message(ctx, link)
        if msg is None:
            await ctx.send("Klarte ikke finne meldingen")
            return

        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        added = rules.add_link_setting('react_rules',
                                       lov,
                                       f'{self._format_message_link(msg)}')

        self._react_messages.append(msg.id)
        with codecs.open(self.REACT_MSGS, "w+", encoding='utf8') as f:
            json.dump(self._react_messages, f, indent=4)

        if added == -1:
            await ctx.send("Melding allerede satt opp for reaksjoner")
        elif added:
            try:
                await msg.clear_reactions()
                await asyncio.sleep(1)
                await msg.add_reaction(self.emoji)
                await ctx.send("reaksjonsregler lagt til")
            except:
                await ctx.send("Får ikke reacta")
        else:
            await ctx.send("Reglene du skrev inn finnes ikke")

    @_react_settings.command(name="unlink")
    async def unlink_alternate(self, ctx, message_link):
        """
        Fjerner en reaksjons-regler til en reaksjon på en melding lovherket.
        """

        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)

        msg = await self._get_linked_message(ctx, message_link)
        if msg is None:
            await ctx.send("Sjekk at linken er gyldig")
            return
        link = self._format_message_link(msg)

        await self._remove_reactions(ctx, link)
        removed = rules.remove_link_setting("react_rules", "link", link)
        if removed:
            await ctx.send("Reaksjon-regler fjernet")
        else:
            await ctx.send("Meldingen var ikke satt til autooppdatering")

    """
    Events
    """
    # Call rules without using commands
    async def on_message(self, message):

        if message.author.id == self.bot.user.id:
            return

        if not isinstance(message.channel, discord.TextChannel):
            return

        content = message.content

        if content is '' or content[0] is not "§":  # hardcoded atm
            return

        split = content.split('§')
        num = split[1]

        if num is '':
            return

        # crap way to avoid runnin when a command runs
        try:
            int(num.split()[0])
        except:
            return

        rules = RuleManager(message.guild.id, self.SERVERS_PATH)

        lov = rules.get_settings("default_rule")
        rule_text = rules.get_rule_text(lov)

        context = message.channel

        if rule_text is None:
            await context.send('**Du må sette default før dette fungerer\n' +
                               'Liste over lovene i lovherket:**\n' +
                               f'{rules.get_rules_formatted()}')
            return

        if rule_text == "":
            await context.send("Denne regelen er helt tom.")
            return

        # Get only specified rules
        partial_rules = ""
        for rule in num.split():
            lovregex = r"(§ *" + re.escape(rule) + r"[a-z]?: [\S ]*)"
            m = re.search(lovregex, rule_text)
            if m is not None:
                partial_rules += m.groups()[0] + "\n"

        if partial_rules is '':
            return
        await context.send(partial_rules)

    async def on_raw_reaction_add(self, payload):
        await self.react_action(payload, True)

    async def on_raw_reaction_remove(self, payload):
        await self.react_action(payload, False)

    async def on_raw_reaction_clear(self, payload):
        if payload.message_id not in self._react_messages:
            return
        channel = self.bot.get_channel(payload.channel_id)
        msg = await channel.get_message(payload.message_id)
        await asyncio.sleep(1)
        await msg.add_reaction(self.emoji)

    async def react_action(self, payload, added):

        if payload.guild_id is None:
            return

        if payload.message_id not in self._react_messages:
            return

        if str(payload.emoji) == self.emoji:
            if not added and payload.user_id == self.bot.user.id:
                channel = self.bot.get_channel(payload.channel_id)
                msg = await channel.get_message(payload.message_id)
                await msg.add_reaction(self.emoji)

            if added and payload.user_id != self.bot.user.id:
                channel = self.bot.get_channel(payload.channel_id)
                msg = await channel.get_message(payload.message_id)
                user = self.bot.get_user(payload.user_id)
                try:
                    await msg.remove_reaction(self.emoji, user)
                except:
                    await channel.send("Tell a mod to fix my perms" +
                                       f"{user.mention}")
                await self._dm_rules(user, msg)
        else:
            if added and payload.user_id != self.bot.user.id:
                channel = self.bot.get_channel(payload.channel_id)
                msg = await channel.get_message(payload.message_id)
                await msg.clear_reactions()

        if str(payload.emoji) == self.emoji:
            rules = RuleManager

    """
    Non commands functions
    """

    def _format_message_link(sef, msg):
        message_link = f'https://discordapp.com/channels/' \
            + f'{msg.guild.id}/{msg.channel.id}/{msg.id}'
        return message_link

    async def _get_linked_message(self, ctx, message_link):
        try:
            message_split = message_link.split("/")
            message_id = int(message_split[-1])
            channel_id = int(message_split[-2])
            guild_id = int(message_split[-3])
        except:
            return None

        if ctx.guild.id != int(guild_id):
            return None

        channel = ctx.guild.get_channel(channel_id)
        if channel is None:
            return None

        try:
            msg = await channel.get_message(message_id)
            return msg
        except:
            return None

    async def _remove_reactions(self, ctx, to_match):
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        react_rules = rules.get_settings("react_rules")
        for rule in react_rules:
            if rule["name"] == to_match or rule["link"] == to_match:
                msg = await self._get_linked_message(ctx, rule["link"])
                if msg is None:
                    await ctx.send('Får ikke fjernet reaksjonen fra ' +
                                   f'følgende melding:\n{message["link"]}\n' +
                                   'Sjekk om den er tilgjengelig for botten' +
                                   ' eller slett reaksjonen manuelt')
                    continue

                await msg.remove_reaction(self.emoji, self.bot.user)

                self._react_messages.remove(msg.id)
                with codecs.open(self.REACT_MSGS, "w+", encoding='utf8') as f:
                    json.dump(self._react_messages, f, indent=4)

                await asyncio.sleep(2)

    async def _dm_rules(self, user, msg):

        rules = RuleManager(msg.guild.id, self.SERVERS_PATH)
        react_rules = rules.get_settings("react_rules")
        msg_link = self._format_message_link(msg)
        rule_name = None
        for rule in react_rules:
            if rule["link"] == msg_link:
                rule_name = rule["name"]

        if rule_name is None:
            return

        rule_text = rules.get_rule_text(rule_name, alternate=True)
        try:
            await user.send(rule_text)
        except discord.Forbidden:
            await msg.channel.send(f"I can't send you messages {user.mention}")

    async def _update_messages(self, ctx, name=None):
        rules = RuleManager(ctx.guild.id, self.SERVERS_PATH)
        auto_update_messages = rules.get_settings('auto_update')

        for message in auto_update_messages:
            if message["name"] == name or name is None:
                msg = await self._get_linked_message(ctx, message["link"])
                if msg is None:
                    await ctx.send('Klarer ikke finne følgende melding:\n' +
                                   f'{message["link"]}\nSjekk om den finnes,' +
                                   ' hvis ikke fjern den med `§auto fjern`')
                    continue

                updated_text = rules.get_rule_text(message["name"])
                if updated_text is None:
                    await ctx.send('Fant ikke en regel med følgende navn:\n' +
                                   f'{message["name"]}.')
                    continue

                await asyncio.sleep(2)
                await msg.edit(content=updated_text)


def setup(bot):
    bot.add_cog(Rules(bot))
