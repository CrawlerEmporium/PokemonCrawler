import string

import pokebase as pb
import re
import typing
import json
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





async def getMatchup(pokemon):
    pkmn = ""
    if isinstance(pokemon, str):
        pkmn = pb.pokemon(pokemon.lower().replace("'", ""))
    if isinstance(pokemon, int):
        pkmn = pb.pokemon(pokemon)
    em = discord.Embed()
    em.set_author(name=GG.cleanWordDash(pkmn.name))
    em.set_thumbnail(url="http://play.pokemonshowdown.com/sprites/xyani/" + pkmn.name.lower() + ".gif")

    types = pkmn.types
    if len(types) == 2:
        type = GG.cleanWordDash(types[1].type.name)
        color = GG.getColorOfType(type.lower())
    else:
        type = GG.cleanWordDash(types[0].type.name)
        color = GG.getColorOfType(type.lower())
    em.colour = int("0x" + color, 0)

    DNB = []
    USEDTYPES = []

    WT1 = []
    IT1 = []
    RT1 = []

    WT2 = []
    IT2 = []
    RT2 = []

    WT = []
    IT = []
    RT = []

    if len(types) == 2:
        type1_ = pb.type_(GG.cleanWordSpace(types[0].type.name))
        for y in type1_.damage_relations.double_damage_from:
            WT1.append(f"{GG.cleanWordDash(y['name'])}")
        for y in type1_.damage_relations.no_damage_from:
            IT1.append(f"{GG.cleanWordDash(y['name'])}")
        for y in type1_.damage_relations.half_damage_from:
            RT1.append(f"{GG.cleanWordDash(y['name'])}")
        type2_ = pb.type_(GG.cleanWordSpace(types[1].type.name))
        for y in type2_.damage_relations.double_damage_from:
            WT2.append(f"{GG.cleanWordDash(y['name'])}")
        for y in type2_.damage_relations.no_damage_from:
            IT2.append(f"{GG.cleanWordDash(y['name'])}")
        for y in type2_.damage_relations.half_damage_from:
            RT2.append(f"{GG.cleanWordDash(y['name'])}")
        await doubleType(DNB, IT, IT1, IT2, RT, RT1, RT2, USEDTYPES, WT, WT1, WT2)
    else:
        type_ = pb.type_(GG.cleanWordSpace(types[0].type.name))
        for y in type_.damage_relations.double_damage_from:
            WT1.append(f"{GG.cleanWordDash(y['name'])}")
        for y in type_.damage_relations.no_damage_from:
            IT1.append(f"{GG.cleanWordDash(y['name'])}")
        for y in type_.damage_relations.half_damage_from:
            RT1.append(f"{GG.cleanWordDash(y['name'])}")
        await singleType(IT,RT,WT,IT1,RT1,WT1,USEDTYPES)

    for x in GG.TYPES:
        if x not in USEDTYPES:
            DNB.append('{"type":"' + GG.cleanWordDash(x) + '","effectiveness":"1x"}')

    DNBString = ""
    for x in DNB:
        x = json.loads(x)
        DNBString += f"{x['type']}: {x['effectiveness']}\n"

    WTString = ""
    for x in WT:
        x = json.loads(x)
        WTString += f"{x['type']}: {x['effectiveness']}\n"
    if WTString == "":
        WTString = "\u200b"

    ITString = ""
    for x in IT:
        x = json.loads(x)
        ITString += f"{x['type']}: {x['effectiveness']}\n"
    if ITString == "":
        ITString = "\u200b"

    RTString = ""
    for x in RT:
        x = json.loads(x)
        RTString += f"{x['type']}: {x['effectiveness']}\n"
    if RTString == "":
        RTString = "\u200b"

    em.add_field(name="Damaged normally by", value=DNBString)
    em.add_field(name="Weak to", value=WTString)
    em.add_field(name="Immune to", value=ITString)
    em.add_field(name="Resistant to", value=RTString)

    return em


async def doubleType(DNB, IT, IT1, IT2, RT, RT1, RT2, USEDTYPES, WT, WT1, WT2):
    for x in WT1:
        if x in WT2:
            WT.append('{"type":"' + x + '","effectiveness":"4x"}')
            USEDTYPES.append(x.lower())
        else:
            if x in RT2:
                DNB.append('{"type":"' + x + '","effectiveness":"1x"}')
                USEDTYPES.append(x.lower())
            else:
                WT.append('{"type":"' + x + '","effectiveness":"2x"}')
                USEDTYPES.append(x.lower())
    for x in WT2:
        if x not in WT1 and x not in RT1 and x not in IT1 and x not in IT2:
            WT.append('{"type":"' + x + '","effectiveness":"2x"}')
            USEDTYPES.append(x.lower())
    for x in IT1:
        IT.append('{"type":"' + x + '","effectiveness":"0x"}')
        USEDTYPES.append(x.lower())
    for x in IT2:
        IT.append('{"type":"' + x + '","effectiveness":"0x"}')
        USEDTYPES.append(x.lower())
    for x in RT1:
        if x in RT2:
            RT.append('{"type":"' + x + '","effectiveness":"0.25x"}')
            USEDTYPES.append(x.lower())
        else:
            if x in WT2:
                DNB.append('{"type":"' + x + '","effectiveness":"1x"}')
                USEDTYPES.append(x.lower())
            else:
                RT.append('{"type":"' + x + '","effectiveness":"0.5x"}')
                USEDTYPES.append(x.lower())
    for x in RT2:
        if x not in RT1 and x not in WT1 and x not in IT1 and x not in IT2:
            RT.append('{"type":"' + x + '","effectiveness":"0.5x"}')
            USEDTYPES.append(x.lower())

async def singleType(IT, RT, WT, IT1, RT1, WT1, USEDTYPES):
    for x in WT1:
        WT.append('{"type":"' + x + '","effectiveness":"2x"}')
        USEDTYPES.append(x.lower())
    for x in RT1:
        RT.append('{"type":"' + x + '","effectiveness":"0.5x"}')
        USEDTYPES.append(x.lower())
    for x in IT1:
        IT.append('{"type":"' + x + '","effectiveness":"0x"}')
        USEDTYPES.append(x.lower())
    pass

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

    @commands.command(aliases=['effectiveness','match'])
    async def matchup(self, ctx, pokemon=None):
        if pokemon is None:
            await ctx.send("No Pokémon given.")
            return
        msg = await ctx.send("Looking up your Pokémon Type Effectiveness! Please wait a moment...\n(*This can take a while, the api is slow. Nothing I can do.*)")
        em = await getMatchup(pokemon)
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