import datetime
import os
import time
from os.path import isfile, join

import discord

from DBService import DBService
import utils.globals as GG
from discord.ext import commands
from utils import logger

log = logger.logger


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.monotonic()

    @commands.command()
    async def support(self, ctx):
        em = GG.EmbedWithAuthor(ctx)
        em.title = 'Support Server'
        em.description = "So you want support for PokemonCrawler? You can easily join my discord [here](https://discord.gg/HEY6BWj).\n" \
                         "This server allows you to ask questions about the bot. Do feature requests, and talk with other bot users!\n\n" \
                         "If you want to somehow support my developer, you can buy me a cup of coffee (or 2) [here](https://ko-fi.com/5ecrawler)"
        await ctx.send(embed=em)

    @commands.command()
    async def invite(self, ctx):
        em = GG.EmbedWithAuthor(ctx)
        em.title = 'Invite Me!'
        em.description = "Hi, you can easily invite me to your own server by following [this link](" \
                         "https://discordapp.com/oauth2/authorize?client_id=574554734187380756&scope=bot&permissions" \
                         "=0)!"
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @GG.is_owner()
    async def prefix(self, ctx, prefix: str = None):
        """Sets the bot's prefix for this server.
        Forgot the prefix? Reset it with "PokemonCrawler#5165 prefix !".
        """
        guild_id = str(ctx.guild.id)
        if prefix is None:
            return await ctx.send(f"My current prefix is: `{self.bot.get_server_prefix(ctx.message)}`")
        DBService.exec(
            "REPLACE INTO Prefixes (Guild, Prefix) VALUES (" + str(ctx.guild.id) + ",'" + str(prefix) + "')")
        self.bot.prefixes[guild_id] = prefix
        GG.PREFIXES[guild_id] = prefix
        await ctx.send("Prefix set to `{}` for this server.".format(prefix))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, extension_name: str):
        """[OWNER ONLY]"""
        if ctx.author.id == GG.OWNER:
            try:
                ctx.bot.load_extension(GG.COGS + "." + extension_name)
            except (AttributeError, ImportError) as e:
                await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
                return
            await ctx.send("{} loaded".format(extension_name))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension_name: str):
        """[OWNER ONLY]"""
        if ctx.author.id == GG.OWNER:
            ctx.bot.unload_extension(GG.COGS + "." + extension_name)
            await ctx.send("{} unloaded".format(extension_name))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, extension_name: str):
        """[OWNER ONLY]"""
        if ctx.author.id == GG.OWNER:
            if extension_name == "all":
                for extension in [f.replace('.py', '') for f in os.listdir(GG.COGS) if isfile(join(GG.COGS, f))]:
                    ctx.bot.unload_extension(GG.COGS + "." + extension_name)
                    try:
                        ctx.bot.load_extension(GG.COGS + "." + extension)
                    except Exception as e:
                        log.error(f'Failed to load extension {extension}.')
                await ctx.send("Every module was reloaded!")
            else:
                ctx.bot.unload_extension(GG.COGS + "." + extension_name)
                try:
                    ctx.bot.load_extension(GG.COGS + "." + extension_name)
                except (AttributeError, ImportError) as e:
                    await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
                    return
                await ctx.send("{} reloaded".format(extension_name))


    @commands.command(aliases=['stats', 'info'])
    async def botinfo(self, ctx):
        """Shows info about bot"""
        em = discord.Embed(color=discord.Color.green(), description="PokemonCrawler, a lookup bot for Pokemon, their moves, abilities, etc.")
        em.title = 'Bot Info'
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        em.add_field(name="Servers", value=str(len(ctx.bot.guilds)))
        total_members = sum(len(s.members) for s in self.bot.guilds)
        unique_members = set(self.bot.get_all_members())
        members = '%s total\n%s unique' % (total_members, len(unique_members))
        em.add_field(name='Members', value=members)
        em.add_field(name='Uptime', value=str(datetime.timedelta(seconds=round(time.monotonic() - self.start_time))))
        totalText = 0
        totalVoice = 0
        for g in ctx.bot.guilds:
            text, voice = GG.countChannels(g.channels)
            totalText += text
            totalVoice += voice
        em.add_field(name='Text Channels', value=f"{totalText}")
        em.add_field(name='Voice Channels', value=f"{totalVoice}")
        em.add_field(name="Invite",
                     value="[Click Here](https://discordapp.com/oauth2/authorize?client_id=574554734187380756&scope=bot&permissions=0)")
        em.add_field(name='Source', value="[Click Here](https://github.com/5ecrawler/PokemonCrawler)")
        em.add_field(name='Issue Tracker', value="[Click Here](https://github.com/5ecrawler/PokemonCrawler)")
        em.add_field(name="About",
                     value='A Pokemon lookup bot made by LordDusk#0001 .\n[Support Server](https://discord.gg/HEY6BWj)')
        em.set_footer(text=f"PokemonCrawler {ctx.bot.version} | Powered by discord.py and PokéAPI.co")
        await ctx.send(embed=em)


    @commands.command()
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """Shows info about server"""
        HUMANS = ctx.guild.members
        BOTS = []
        for h in HUMANS:
            if h.bot is True:
                BOTS.append(h)
                HUMANS.remove(h)

        embed = discord.Embed(color=discord.Color.green())
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.add_field(name="Name", value=ctx.guild.name)
        embed.add_field(name="ID", value=ctx.guild.id)
        embed.add_field(name="Owner", value=f"{ctx.guild.owner.name}#{ctx.guild.owner.discriminator}")
        embed.add_field(name="Region", value=GG.REGION[ctx.guild.region])
        embed.add_field(name="Total | Humans | Bots", value=f"{len(ctx.guild.members)} | {len(HUMANS)} | {len(BOTS)}")
        embed.add_field(name="Verification Level", value=GG.VERIFLEVELS[ctx.guild.verification_level])
        text, voice = GG.countChannels(ctx.guild.channels)
        embed.add_field(name="Text Channels", value=str(text))
        embed.add_field(name="Voice Channels", value=str(voice))
        embed.add_field(name="Creation Date", value=f"{ctx.guild.created_at}\n{GG.checkDays(ctx.guild.created_at)}")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)


def setup(bot):
    log.info("Loading Info Cog...")
    bot.add_cog(Info(bot))
