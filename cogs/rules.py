import discord
import re
import asyncio
import typing
import os
import codecs
import json
from datetime import datetime
from cogs.utils.rulemanager import RuleManager
from discord.ext import commands


class Rules(commands.Cog):

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

        if isinstance(lov, int):
            if num is None:
                num = str(lov)
            else:
                num = str(lov) + " " + num
            lov = rules.get_settings("default_rule")

        rule_text, date = rules.get_rule_text(lov)

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

            no_dupes = remove_duplicates(num.split())

            for rule in no_dupes:
                ruleregex = r"(§ *" + re.escape(rule) + r"[a-z]?: [\S ]*)"
                m = re.search(ruleregex, rule_text)
                if m is not None:
                    partial_rules += m.groups()[0] + "\n"

            if partial_rules == "":
                await ctx.send(f'Fant ikke reglene du ser etter')
            else:
                if lov != rules.get_settings("default_rule"):
                    partial_rules = f'**I reglene for {lov}:**\n' \
                        + partial_rules
                await ctx.send(partial_rules)
        else:
            embed = await self._create_embed(rule_text, date)
            await ctx.send(embed=embed)

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
        rule_text, date = rules.get_rule_text(lov)

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
        rule_text, date = rules.get_rule_text(lov)

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
        rule_text, date = rules.get_rule_text(lov)

        if rule_text is None:
            await ctx.send('Sjekk at reglene finnes.\n' +
                           '**Liste over lovene i lovherket:**\n' +
                           f'{rules.get_rules_formatted()}')
            return

        if rule_text == "":
            await ctx.send("Den regelen er helt tom.")
            return

        embed = await self._create_embed(rule_text, date)
        msg = await ctx.send(embed=embed)
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
        rule_text, date = rules.get_rule_text(lov, alternate=True)
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

        # crap way to avoid running when a command runs
        try:
            int(num.split()[0])
        except:
            return

        rules = RuleManager(message.guild.id, self.SERVERS_PATH)

        lov = rules.get_settings("default_rule")
        rule_text, date = rules.get_rule_text(lov)

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
        no_dupes = remove_duplicates(num.split())
        for rule in no_dupes:
            ruleregex = r"(§ *" + re.escape(rule) + r"[a-z]?: [\S ]*)"
            m = re.search(ruleregex, rule_text)
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
            msg = await channel.fetch_message(message_id)
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

        rule_text, date = rules.get_rule_text(rule_name, alternate=True)
        try:
            embed = await self._create_embed(rule_text, date)
            await user.send(embed=embed)
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

                updated_text, date = rules.get_rule_text(message["name"])
                if updated_text is None:
                    await ctx.send('Fant ikke en regel med følgende navn:\n' +
                                   f'{message["name"]}.')
                    continue

                await asyncio.sleep(2)
                embed = await self._create_embed(updated_text, date)
                await msg.edit(content=None, embed=embed)

    async def _create_embed(self, text, date):
        avatar = self.bot.user.avatar_url_as(format=None,
                                             static_format='png',
                                             size=1024)

        embed = discord.Embed(color=0xD9C04D)
        embed.set_author(name=self.bot.user.name, icon_url=avatar)
        embed.description = text
        embed.set_footer(text='Sist oppdatert')
        embed.timestamp = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')

        return embed

    @commands.command(name='embed', hidden=True)
    async def _test(self, ctx):
        try:
            embed = discord.Embed(title="Grunnreglene for /r/Norge", colour=discord.Colour(0xD9C04D), timestamp=datetime.now())

            embed.set_author(name="LovHerket", icon_url="https://images-ext-2.discordapp.net/external/CLn-yVj427nAOadeqchtoKz4O2KZ0hNKP6kL0g6zv_c/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/413267882496098305/3dc2c25811a515257399c6b5144b7700.png")
            embed.set_footer(text="Sist oppdatert")

            embed.add_field(name="Generelt", value="**§  1**: Denne discordserveren er norskspråklig, så vi holder oss til norsk så langt det går.*\n**§  2**: Sjekk pinned messages, her finner du både informasjon og underholdning.\n")
            embed.add_field(name="Krav til oppførsel", value="**§  3**: Ikke spam - vi slår særlig ned på pingspam. \n**§  4**: Hold deg til riktig kanal. \n**§  5**: Forhold deg til norsk lov. \n**§  6**: Ingen rasisme, homofobi, antisemittisme, diskriminering eller andre hatytringer.\n**§  7**: Ingen personangrep, ingen doxxing. \n**§  8**: Ikke lag kvalme eller oppfør deg på en måte som kun virker tergende og forstyrrende. \n**§  9**: Ingen heksejaging/brigadering.\n**§ 10**: Ikke noe støtende eller ubehagelige megmeger/media (Eksempler: Mobbing, gore, unødvendig slemhet) eller pornografi.")
            embed.add_field(name="Diverse", value="**§ 11**: Ingen posting av invitasjonslinker til andre discordservere uten godkjenning fra mods/admins (bruk gjerne <@372155256341135360> for dette). \n**§ 12**: <#298511909236375552> har noe annerledes håndheving av visse regler, så se pin i kanalen for egne regler.\n**§ 13**: NSFW megmeger kan postes i <#398969290662871041>, men vær anstendig. NSFL innhold er ikke tillatt. \n**§ 14**: Moderering blir ikke diskutert offentlig, dette tas gjennom <@372155256341135360>.")

            msg = await ctx.send(embed=embed)
            return msg
        except Exception as e:
            print(e)


def remove_duplicates(dupe_list):
    seen = {}
    result = []
    for item in dupe_list:
        if item in seen:
            continue
        seen[item] = 1
        result.append(item)
    return result


def setup(bot):
    bot.add_cog(Rules(bot))
