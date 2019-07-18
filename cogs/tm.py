import string

import pokebase as pb
import re
import typing
import discord
from discord.ext import commands
import utils.globals as GG
from utils import logger

log = logger.logger
APICallsPerTMTO50 = 18
APICallsPerTMTO50TOTAL = 50 * APICallsPerTMTO50
APICallsPerTMTO92 = 9
APICallsPerTMTO92TOTAL = APICallsPerTMTO50TOTAL + (42 * APICallsPerTMTO92)
APICallsPerTMTO95 = 6
APICallsPerTMTO95TOTAL = APICallsPerTMTO92TOTAL + (3 * APICallsPerTMTO95)
APICallsPerTMTO100 = 6


class TM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tm(self, ctx, tmID=None):
        if tmID is None:
            await ctx.send("No TM given, you can use it's name or id number.")
            return
        msg = await ctx.send(
            "Looking up your TM! Please wait a moment...\n(*This can take a while, the api is slow. Nothing I can do.*)")
        em = await getTM(tmID)
        await msg.edit(content=None, embed=em)


async def getTM(id):
    em = discord.Embed()
    if isinstance(id,int):
        id = int(id)
    else:
        em.description = "Please use the TM ID, and not the move name."
        return em

    if id < 10:
        em.set_author(name=f"TM0{id}")
    else:
        em.set_author(name=f"TM{id}")

    if id == 1:
        StartID = id
        EndID = StartID + (APICallsPerTMTO50)
    elif id in range(2,50):
        StartID = ((id - 1) * APICallsPerTMTO50) + 1
        EndID = StartID + (APICallsPerTMTO50)
    elif id in range(51, 92):
        StartID = APICallsPerTMTO50TOTAL + (((id - 51) * APICallsPerTMTO92)) + 1
        EndID = StartID + (APICallsPerTMTO92)
    elif id in range(93, 95):
        StartID = APICallsPerTMTO92TOTAL + (((id - 93) * APICallsPerTMTO95)) + 1
        EndID = StartID + (APICallsPerTMTO95)
    elif id in range(95, 100):
        StartID = APICallsPerTMTO95TOTAL + (((id - 95) * APICallsPerTMTO100)) + 1
        EndID = StartID + (APICallsPerTMTO100)
    else:
        em.description("This TM doesn't exist.")
        return em

    COLORS = []
    COLOROUTPUT = ''
    for x in range(StartID, EndID, 1):
        TM = pb.machine(x)
        em.add_field(name=f"{GG.cleanWordDash(TM.move.name)}", value=f"{GG.getGame(TM.version_group.name)}")

        move = pb.move(TM.move.name)
        if GG.getColorOfType(move.type.name) not in COLORS:
            COLORS.append(GG.getColorOfType(move.type.name))
    i = 0
    for x in range(i, len(COLORS), 2):
        i = x + 1
        if i != len(COLORS):
            COLORS.append(color_mixer(COLORS[x], COLORS[(i)]))
            COLOROUTPUT = color_mixer(COLORS[x], COLORS[(i)])
    COLOROUTPUT = COLOROUTPUT.replace("#", "")
    if COLOROUTPUT == "":
        COLOROUTPUT = COLORS[0]
    em.colour = int("0x" + COLOROUTPUT, 0)

    return em


# hex (string) to rgb (tuple3)
def hex2rgb(hex):
    hex_cleaned = hex.lstrip('#')
    return tuple(int(hex_cleaned[i:i + 2], 16) for i in (0, 2, 4))


# rgb (tuple3) to hex (string)
def rgb2hex(rgb):
    return '#' + ''.join([str('0' + hex(hh)[2:])[-2:] for hh in rgb])


# weighted mix of two colors in RGB space (takes and returns hex values)
def color_mixer(hex1, hex2, wt1=0.5):
    rgb1 = hex2rgb(hex1)
    rgb2 = hex2rgb(hex2)
    return rgb2hex(tuple([int(wt1 * tup[0] + (1.0 - wt1) * tup[1]) for tup in zip(rgb1, rgb2)]))


def setup(bot):
    log.info("Loading TM Cog...")
    bot.add_cog(TM(bot))
