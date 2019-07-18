import string

import pokebase as pb
import re
import typing
import discord
from discord.ext import commands
import utils.globals as GG
from utils import logger

log = logger.logger


async def getWeakness(type_):
    ty = pb.type_(GG.cleanWordSpace(type_))
    em = discord.Embed()
    name = GG.getNames(ty.names)
    em.set_author(name=name)
    color = GG.getColorOfType(name.lower())
    em.colour = int("0x" + color, 0)

    DDF = ""
    for y in ty.damage_relations.double_damage_from:
        DDF += f"{GG.cleanWordDash(y['name'])}\n"
    if DDF == "":
        DDF = "-"
    em.add_field(name="Weak against:", value=DDF)
    NDT = ""
    for y in ty.damage_relations.no_damage_to:
        NDT += f"{GG.cleanWordDash(y['name'])}\n"
    if NDT == "":
        NDT = "-"
    em.add_field(name="Deal no damage to:", value=NDT)

    return em


async def getStrength(type_):
    ty = pb.type_(GG.cleanWordSpace(type_))
    em = discord.Embed()
    name = GG.getNames(ty.names)
    em.set_author(name=name)
    color = GG.getColorOfType(name.lower())
    em.colour = int("0x" + color, 0)

    DDT = ""
    for y in ty.damage_relations.double_damage_to:
        DDT += f"{GG.cleanWordDash(y['name'])}\n"
    if DDT == "":
        DDT = "-"
    em.add_field(name="Strong against:", value=DDT)
    NDF = ""
    for y in ty.damage_relations.no_damage_from:
        NDF += f"{GG.cleanWordDash(y['name'])}\n"
    if NDF == "":
        NDF = "-"
    em.add_field(name="Take no damage from:", value=NDF)

    return em


class Type(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="type")
    async def type_(self, ctx, type=None):
        if type is None:
            await ctx.send("No type given.")
            return
        msg = await ctx.send("Looking up your Type! Please wait a moment...\n(*This can take a while, the api is slow. Nothing I can do.*)")
        em = await getType(type)
        await msg.edit(content=None, embed=em)

    @commands.command()
    async def weakness(self, ctx, type=None):
        if type is None:
            await ctx.send("No type given.")
            return
        msg = await ctx.send(
            "Looking up your Type Weaknesses! Please wait a moment...\n(*This can take a while, the api is slow. Nothing I can do.*)")
        em = await getWeakness(type)
        await msg.edit(content=None, embed=em)

    @commands.command()
    async def strength(self, ctx, type=None):
        if type is None:
            await ctx.send("No type given.")
            return
        msg = await ctx.send(
            "Looking up your Type Strengths! Please wait a moment...\n(*This can take a while, the api is slow. Nothing I can do.*)")
        em = await getStrength(type)
        await msg.edit(content=None, embed=em)

async def getType(type_):
    ty = pb.type_(GG.cleanWordSpace(type_))
    em = discord.Embed()
    name = GG.getNames(ty.names)
    em.set_author(name=name)
    color = GG.getColorOfType(name.lower())
    em.colour = int("0x" + color, 0)

    em.add_field(name="Take Damage:", value="\u200b", inline=False)
    NDF = ""
    for y in ty.damage_relations.no_damage_from:
        NDF += f"{GG.cleanWordDash(y['name'])}\n"
    if NDF == "":
        NDF = "-"
    em.add_field(name="No Effect (0%)", value=NDF)

    HDF = ""
    for y in ty.damage_relations.half_damage_from:
        HDF += f"{GG.cleanWordDash(y['name'])}\n"
    if HDF == "":
        HDF = "-"
    em.add_field(name="Not Very Effective (50%)", value=HDF)

    DDF = ""
    for y in ty.damage_relations.double_damage_from:
        DDF += f"{GG.cleanWordDash(y['name'])}\n"
    if DDF == "":
        DDF = "-"
    em.add_field(name="Super-Effective (200%)", value=DDF)

    em.add_field(name="Deal Damage:", value="\u200b", inline=False)
    NDT = ""
    for y in ty.damage_relations.no_damage_to:
        NDT += f"{GG.cleanWordDash(y['name'])}\n"
    if NDT == "":
        NDT = "-"
    em.add_field(name="No Effect (0%)", value=NDT)

    HDT = ""
    for y in ty.damage_relations.half_damage_to:
        HDT += f"{GG.cleanWordDash(y['name'])}\n"
    if HDT == "":
        HDT = "-"
    em.add_field(name="Not Very Effective (50%)", value=HDT)

    DDT = ""
    for y in ty.damage_relations.double_damage_to:
        DDT += f"{GG.cleanWordDash(y['name'])}\n"
    if DDT == "":
        DDT = "-"
    em.add_field(name="Super-Effective (200%)", value=DDT)

    return em

def setup(bot):
    log.info("Loading Type Cog...")
    bot.add_cog(Type(bot))