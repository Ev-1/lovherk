import discord
import os
import codecs
import re
import asyncio

from discord.ext import commands


class RulesReact:
    def __init__(self, bot):
        self.bot = bot
        self.emoji = '\N{INCOMING ENVELOPE}'



    """ This cog is an addition to the rules cog. 

        The cog it lets you have a separate set of rules that gets DMed to people
        when they react to a message. Can be useful for DMing people a translated version of the rules.

        It is kinda shit, but I think it works. 

    """

    # Commands for viewing and editing rules, this code is almost the same as for rules
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.group(invoke_without_command=True, name="elov")
    async def rules(self, ctx, lov: str = None,*, num: str = None):
        """Viser reglene i det engelske lovherket."""

        if lov == None:
            await ctx.send("**Liste over lovene i det engelske lovherket:**\n{}".format(get_rules_list(ctx.guild.id)))
            return

        rule_file = get_file_name(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules_react/"

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
                await ctx.send("**Liste over lovene i det engelske lovherket:**\n{}".format(get_rules_list(ctx.guild.id)))
                return

            await ctx.send(lovtekst)
        else:
            await ctx.send("Sjekk at du skrev riktig.")


    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @rules.command(name="ny")
    async def newrules(self, ctx, lov, *, newrule: str = None):
        """Legger til et nytt sett med regler i det engelske lovherket."""

        rule_file = get_file_name(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules_react/"

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
        rules_path = get_server_path(ctx.guild.id) + "rules_react/"

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
        """Fjerner regler fra det engelske lovherket."""

        rule_file = get_file_name(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules_react/"
        if rule_file in os.listdir(rules_path):
            rulepath = rules_path + rule_file
            os.remove(rulepath)
            await self.remove_react_rule(ctx, lov)
            await ctx.send("Regler fjernet")
        else:
            await ctx.send("Reglene du skrev inn finnes ikke")


    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @rules.command(name="oppdater")
    async def updaterules(self, ctx, lov, *, newrule: str = None):
        """Oppdaterer lover i det engelske lovherket."""

        if newrule == None:
            await ctx.send("Du skrev ikke inn noe")
            return

        rule_file = get_file_name(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules_react/"

        if rule_file in os.listdir(rules_path):
            rulepath = rules_path + rule_file
            with codecs.open(rulepath,'w',encoding='utf8') as f:
                f.write(newrule)
            await ctx.send("Regler oppdatert")

        else:
            await ctx.send("Sjekk at du skrev riktig.")


    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.group(invoke_without_command=True, name="reaksjon")
    async def add_react(self, ctx, lov, message_link):
        """Kobler et sett med regler til en reaksjon på en melding"""

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

        update_path = get_server_path(ctx.guild.id) + 'react_messages.txt'
        check_auto(update_path)
        
        with codecs.open(update_path, 'r', encoding='utf8') as f:
            react_list = f.read()
            f.close()

            new_react = "{} {} {}\n".format(lov, channel_id, message_id)

            if new_react in react_list:
                await ctx.send("Meldingen har allerede regler som DMes")
            else:
                with codecs.open(update_path, 'a', encoding='utf8') as f:
                    f.write(new_react)
                await message.add_reaction(self.emoji)
                await ctx.send("reaksjonsregler lagt til")


    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @add_react.command(name="fjern")
    async def _remove_react(self, ctx, message_id):   
        """Fjerner en melding fra lista av meldinger som oppdateres automatisk."""    
        await self.remove_react_rule(ctx, message_id)
        await ctx.send("Reaksjon fjernet fjernet")


    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @add_react.command(name="liste")
    async def list(self, ctx):
        """Gir en liste over meldinger på serveren som er satt til å oppdateres automatisk.""" 

        update_path = get_server_path(ctx.guild.id) + 'react_messages.txt'
        check_auto(update_path)
   
        with codecs.open(update_path, 'r', encoding='utf8') as f:
            auto_list = f.readlines()
            f.close()

        if auto_list == "" or auto_list == "\n":
            await ctx.send("Ingen meldinger har reaksjonsregler")
        else:
            auto_list_message = "**Meldinger med reaksjonsregler:**\nRegel: *link til melding*\n"
            for auto in auto_list:
                if auto.strip() != "":
                    guild_id = str(ctx.guild.id)
                    lov, channel_id, message_id = auto.split(" ")
                    auto_list_message += lov + ": https://discordapp.com/channels/" + guild_id + "/" + channel_id + "/" + message_id
            await ctx.send(auto_list_message) 


    async def remove_react_rule(self, ctx, search_term):
        update_path = get_server_path(ctx.guild.id) + 'react_messages.txt'
        check_auto(update_path)
        to_remove = search_term

        with codecs.open(update_path, 'r', encoding='utf8') as f:
            lines = f.readlines()
            f.close()

        with codecs.open(update_path, 'w', encoding='utf8') as f:
            for line in lines:
                if to_remove not in line:
                    f.write(line)
        
        print(lines)
        for line in lines:
            if to_remove in line:
                channel_id, message_id = line.split(" ")[-2], line.split(" ")[-1]
                channel = ctx.guild.get_channel(int(channel_id))
                message = await channel.get_message(message_id)
                await message.remove_reaction(self.emoji, self.bot.user)
                await asyncio.sleep(2)


    async def on_raw_reaction_add(self, payload):
        await self.react_action(payload, True)


    async def on_raw_reaction_remove(self, payload):
        await self.react_action(payload, False)


    async def on_raw_reaction_clear(self, payload):
        if check_message_in_list(payload.guild_id, payload.message_id):        
            channel = self.bot.get_channel(payload.channel_id)
            msg = await channel.get_message(payload.message_id)
            await msg.add_reaction(self.emoji)


    async def react_action(self, payload, added):
        if check_message_in_list(payload.guild_id, payload.message_id):
            if str(payload.emoji) == self.emoji:
                if not added and payload.user_id == self.bot.user.id:
                    channel = self.bot.get_channel(payload.channel_id)
                    msg = await channel.get_message(payload.message_id)
                    await msg.add_reaction(self.emoji)

                if added and payload.user_id != self.bot.user.id:
                    channel = self.bot.get_channel(payload.channel_id)
                    msg = await channel.get_message(payload.message_id)
                    user = self.bot.get_user(payload.user_id)
                    await msg.remove_reaction(self.emoji,user)
                    await self.dm_rules(user, payload.guild_id, channel, payload.message_id)
            else:
                channel = self.bot.get_channel(payload.channel_id)
                msg = await channel.get_message(payload.message_id)
                await msg.clear_reactions()


    async def dm_rules(self, user, guild_id, channel, message_id):

        update_path = get_server_path(guild_id) + 'react_messages.txt'
        check_auto(update_path)

        with codecs.open(update_path, 'r', encoding='utf8') as f:
            auto_list = f.readlines()
            f.close()

        if auto_list == "" or auto_list == "\n":
            await user.send("An error occured, please contact Even")
        else:
            for line in auto_list:
                if str(message_id) in line:
                    rule_name = ' '.join(line.split(" ")[0:-2]) #uff nei
                    rule_file = get_file_name(rule_name)
                    break

            rules_path = get_server_path(guild_id) + "rules_react/"

            if rule_file in os.listdir(rules_path):
                rulepath = rules_path + rule_file
                with codecs.open(rulepath,'r',encoding='utf8') as f:
                    rules = f.read()
                try:
                    await user.send(rules)
                except discord.Forbidden:
                    await channel.send(f"I can't send you messages {user.mention}")


def setup(bot):
    bot.add_cog(RulesReact(bot))
    check_folder()


def get_rules_list(server_ID):
    temp = get_server_path(server_ID)
    rules_path = temp + 'rules_react'
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
    if not os.path.exists(serverpath + "rules_react"):
        os.makedirs(serverpath + "rules_react")
    return serverpath


# bullshit
def check_auto(path):
    with codecs.open(path, 'a+', encoding='utf8') as f:
        _ = f.read()
        f.close()
    return


def check_message_in_list(guild_id, message_id):
    update_path = get_server_path(guild_id) + 'react_messages.txt'
    check_auto(update_path)
    
    with codecs.open(update_path, 'r', encoding='utf8') as f:
        react_list = f.read()
        f.close()

    if str(message_id) in react_list:
        return True
    else:
        return False