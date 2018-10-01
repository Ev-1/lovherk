import discord
import os
import codecs
import re
import asyncio

from discord.ext import commands


class Rules:
    def __init__(self, bot):
        self.bot = bot

    # Commands for viewing and editing rules
    @commands.guild_only()
    @commands.group(invoke_without_command=True, name="lov")
    async def rules(self, ctx, lov: str = None,*, num: str = None):
        """Viser reglene i lovherket."""

        if lov == None:
            await ctx.send("**Liste over lovene i lovherket:**\n{}".format(get_rules_list(ctx.guild.id)))
            return

        rule_file = get_file_name(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules/"

        if rule_file in os.listdir(rules_path):
            rulepath = rules_path + rule_file
            with codecs.open(rulepath,'r',encoding='utf8') as f:
                lovtekst = f.read()
                if lovtekst == "":
                    await ctx.send("Denne regelen er helt tom.")
                    return

            if num != None:
                temp_lov = ""
                for rule in num.split():
                    lovregex = r"(§ *" + re.escape(rule) + r"[a-z]?: [\S ]*)"
                    m = re.search(lovregex,lovtekst)
                    temp_lov += m.groups()[0] + "\n"
                lovtekst = temp_lov

            if lovtekst == "":
                await ctx.send("**Liste over lovene i lovherket:**\n{}".format(get_rules_list(ctx.guild.id)))
                return

            await ctx.send(lovtekst)
        else:
            await ctx.send("Sjekk at du skrev riktig.")


    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @rules.command(name="ny")
    async def newrules(self, ctx, lov, *, newrule: str = None):
        """Legger til et nytt sett med regler i lovherket."""

        rule_file = get_file_name(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules/"

        if rule_file in os.listdir(rules_path):
            await ctx.send("Det finnes allerede et sett med regler med det navnet.")
            return
        
        rulepath = rules_path + rule_file
        with codecs.open(rulepath, 'w+', encoding='utf8') as f:
            if newrule != None:
                f.write(newrule)

        await ctx.send("Regler laget")


    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @rules.command(name="plaintext")
    async def plaintext(self, ctx, lov):
        """Sender reglene i en kodeblokk så de enkelt kan kopieres med formatering."""

        rule_file = get_file_name(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules/"

        if rule_file in os.listdir(rules_path):
            rulepath = rules_path + rule_file
            with codecs.open(rulepath,'r',encoding='utf8') as f:
                lovtekst = f.read()
            await ctx.send("```\n" + lovtekst + "\n```")
        else:
            await ctx.send("Sjekk at du skrev riktig.")


    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @rules.command(name="fjern")
    async def removerules(self, ctx, lov):
        """Fjerner regler fra lovherket."""

        rule_file = get_file_name(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules/"
        if rule_file in os.listdir(rules_path):
            rulepath = rules_path + rule_file
            os.remove(rulepath)
            await self.remove_auto(ctx, lov)
            await ctx.send("Regler fjernet")
        else:
            await ctx.send("Reglene du skrev inn finnes ikke")


    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @rules.command(name="oppdater")
    async def updaterules(self, ctx, lov, *, newrule: str = None):
        """Oppdaterer lover i lovherket."""

        if newrule == None:
            await ctx.send("Du skrev ikke inn noe")
            return

        rule_file = get_file_name(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules/"

        if rule_file in os.listdir(rules_path):
            rulepath = rules_path + rule_file
            with codecs.open(rulepath,'w',encoding='utf8') as f:
                f.write(newrule)
            await self.update_messages(ctx)
            await ctx.send("Regler oppdatert")

        else:
            await ctx.send("Sjekk at du skrev riktig.")


    """ Below here are commands used to update previous messages when the rules are updated

        
    """
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.group(invoke_without_command=True, name = "auto")
    async def autorules(self, ctx, lov, message_link):
        """Setter en gammel melding til å automatisk oppdateres når regler endres."""

        try:
            message_split = message_link.split("/")
        except:
            await ctx.send("Det er noe feil med linken")
    
        message_id = int(message_split[-1])
        channel_id = int(message_split[-2])
        guild_id = int(message_split[-3])

        if ctx.guild.id != int(guild_id):
            await ctx.send("Den meldingen er ikke på denne serveren")
            return

        # Try to find the message
        try:        
            channel = ctx.guild.get_channel(channel_id)
        except:
            await ctx.send("Kanal ikke funnet")
            return

        try:
            message = await channel.get_message(message_id)
        except:
            await ctx.send("Melding ikke funnet")
            return

        if message.author != self.bot.user:
            await ctx.send("Sjekk at meldingen tilhører botten")
            return

        update_path = get_server_path(ctx.guild.id) + 'autoupdate.txt'
        check_auto(update_path)
        
        with codecs.open(update_path, 'r', encoding='utf8') as f:
            auto_list = f.read()
            f.close()

            new_auto = "{} {} {}\n".format(lov, channel_id, message_id)

            if new_auto in auto_list:
                await ctx.send("Allerede satt til å oppdateres")
            else:
                with codecs.open(update_path, 'a', encoding='utf8') as f:
                    f.write(new_auto)
                await ctx.send("Regel satt til å oppdateres automatisk")

        await self.update_messages(ctx)


    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @autorules.command(name="fiks")
    async def fixauto(self, ctx):
        """Prøver å oppdatere meldingene som skal oppdateres automatisk."""
        await self.update_messages(ctx)
        await ctx.send("Oppdatert")


    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @rules.command(name="auto")
    async def postauto(self, ctx, lov: str = None):
        """Sender en melding som automatisk oppdateres når reglene oppdateres"""

        if lov == None:
            await ctx.send("**Liste over lovene i lovherket:**\n{}".format(get_rules_list(ctx.guild.id)))
            return

        rule_file = get_file_name(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules/"

        if rule_file in os.listdir(rules_path):
            rulepath = rules_path + rule_file
            with codecs.open(rulepath,'r',encoding='utf8') as f:
                lovtekst = f.read()
                if lovtekst == "":
                    await ctx.send("Denne regelen er helt tom.")
                    return

            if lovtekst == "":
                await ctx.send("**Liste over lovene i lovherket:**\n{}".format(get_rules_list(ctx.guild.id)))
                return

            msg = await ctx.send(lovtekst)

            update_path = get_server_path(msg.guild.id) + 'autoupdate.txt'
            check_auto(update_path)
            
            with codecs.open(update_path, 'r', encoding='utf8') as f:
                auto_list = f.read()
                f.close()
                new_auto = "{} {} {}\n".format(lov, msg.channel.id, msg.id)

                with codecs.open(update_path, 'a', encoding='utf8') as f:
                    f.write(new_auto)
        else:
            await ctx.send("Sjekk at du skrev riktig.")


    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @autorules.command(name="fjern")
    async def _remauto(self, ctx, message_id):
        """Fjerner en melding fra lista av meldinger som oppdateres automatisk."""    
        await self.remove_auto(ctx, message_id)
        await ctx.send("autooppdatering fjernet")


    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @autorules.command(name="liste")
    async def list(self, ctx):
        """Gir en liste over meldinger på serveren som er satt til å oppdateres automatisk.""" 

        update_path = get_server_path(ctx.guild.id) + 'autoupdate.txt'
        check_auto(update_path)
   
        with codecs.open(update_path, 'r', encoding='utf8') as f:
            auto_list = f.readlines()
            f.close()

        if auto_list == "" or auto_list == "\n":
            await ctx.send("Ingen meldinger er satt til autooppdatering")
        else:
            auto_list_message = "**Meldinger satt til autooppdatering:**\nRegel: *link til melding*\n"

            for auto in auto_list:
                if auto.strip() != "":
                    guild_id = str(ctx.guild.id)
                    lov, channel_id, message_id = auto.split(" ")
                    auto_list_message += lov + ": https://discordapp.com/channels/" + guild_id + "/" + channel_id + "/" + message_id
            await ctx.send(auto_list_message)


    async def update_messages(self, ctx):
        update_path = get_server_path(ctx.guild.id) + 'autoupdate.txt'
        rules_path = get_server_path(ctx.guild.id) + "rules/"

        check_auto(update_path)

        with codecs.open(update_path, 'r', encoding='utf8') as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            
            for line in content:
                if line.strip() != "":
                    lov, channel_id, message_id = line.split(" ")
                    
                    try:
                        channel = ctx.guild.get_channel(int(channel_id))
                        message = await channel.get_message(message_id)

                    except:
                        await ctx.send("En melding er ikke funnet, det kan hende den er slettet. Kanal: <#{}>, ID: {}".format(channel_id, message_id))
                        return

                    rule_file = get_file_name(lov)

                    if rule_file in os.listdir(rules_path):
                        rulepath = rules_path + rule_file
                        with codecs.open(rulepath,'r',encoding='utf8') as g:
                            lovtekst = g.read()
                        if lovtekst == "":
                            return
                        else:
                            await asyncio.sleep(1)
                            await message.edit(content=lovtekst)


    async def remove_auto(self, ctx, search_term):
        update_path = get_server_path(ctx.guild.id) + 'autoupdate.txt'
        check_auto(update_path)
        to_remove = search_term

        with codecs.open(update_path, 'r', encoding='utf8') as f:
            lines = f.readlines()
            f.close()

        with codecs.open(update_path, 'w', encoding='utf8') as f:
            for line in lines:
                if to_remove not in line:
                    f.write(line)


def setup(bot):
    bot.add_cog(Rules(bot))
    check_folder()


def get_rules_list(server_ID):
    temp = get_server_path(server_ID)
    rules_path = temp + 'rules'
    lover = ""
    
    for lov in os.listdir(rules_path):
        if lov == None:
            continue
        elif lov == "grunnloven.txt":
            lover = '•' + lov.replace(".txt","").capitalize() + "\n" + lover
        elif lov[0] == '#':
            lover += '•' + '<' + lov.replace(".txt","") + '>' + "\n"
        else:
            lover += '•' + lov.replace(".txt","").capitalize() + "\n"
    return lover


def get_file_name(lov):
    lov = lov.lower()
    if lov[1] == '#':
        lov = lov[1:-1]
    lov += '.txt'
    return lov


def check_folder():
    if not os.path.exists('servers/'):
        os.makedirs('servers/')


def get_server_path(server_ID):
    serverpath = "servers/" + str(server_ID) + "/"
    if not os.path.exists(serverpath + "rules"):
        os.makedirs(serverpath + "rules")
    return serverpath


# bullshit
def check_auto(path):
    with codecs.open(path, 'a+', encoding='utf8') as f:
        _ = f.read()
        f.close()
    return
