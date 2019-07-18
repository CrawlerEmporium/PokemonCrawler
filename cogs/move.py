import string

import pokebase as pb
import re
import typing
import discord
from discord.ext import commands
import utils.globals as GG
from utils import logger

log = logger.logger


class Move(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def move(self, ctx, *, move=None):
        if move is None:
            await ctx.send("No move given.")
            return
        msg = await ctx.send(
            "Looking up your Move! Please wait a moment...\n(*This can take a while, the api is slow. Nothing I can do.*)")
        # try:
        em = await getMove(move)
        await msg.edit(content=None, embed=em)
        # except:
        #     error = "Error looking up the Move, please check if you used the command correctly, and if the Move name is spelled correctly.\nUsage: ``#move <move name>``"
        #     await msg.edit(content=error)


async def getMove(move):
    move = GG.cleanWordSpace(move)
    mv = pb.move(move)
    em = discord.Embed()

    em.set_author(name=GG.cleanWordDash(mv.name))
    em.description = GG.getEffectText(mv.effect_entries).replace("$effect_chance",str(mv.effect_chance))
    color = GG.getColorOfType(mv.type.name)
    em.colour = int("0x" + color, 0)

    em.add_field(name="Type", value=GG.cleanWordDash(mv.type.name))
    em.add_field(name="Move Class", value=GG.cleanWordDash(mv.damage_class.name))
    em.add_field(name="Power", value=str(mv.power))
    if mv.accuracy is None:
        em.add_field(name="Accuracy", value=str(mv.accuracy))
    else:
        em.add_field(name="Accuracy", value=str(mv.accuracy) + "%")
    em.add_field(name="PP", value=str(mv.pp))
    if mv.priority > 1:
        em.add_field(name=f"Priority", value=f"+{mv.priority}")
    elif mv.priority < 0:
        em.add_field(name=f"Priority", value=f"{mv.priority}")
    else:
        em.add_field(name="Priority", value="Normal")

    if mv.meta.crit_rate > 0:
        em.add_field(name="Crit Rate", value=f"{mv.meta.crit_rate}%")
    if mv.meta.drain > 0:
        em.add_field(name="Drain", value=f"{mv.meta.drain}%")
    if mv.meta.flinch_chance > 0:
        em.add_field(name="Flinch Chance", value=f"{mv.meta.flinch_chance}%")
    if mv.meta.healing > 0:
        em.add_field(name="Healing", value=f"{mv.meta.healing}%")
    if mv.meta.max_hits is not None:
        em.add_field(name="Number of Hits", value=f"{mv.meta.min_hits}-{mv.meta.max_hits}")
    if mv.meta.max_turns is not None:
        em.add_field(name="Number of Turns", value=f"{mv.meta.min_turns}-{mv.meta.max_turns}")

    if GG.cleanWordDash(mv.meta.ailment.name) != "None":
        em.add_field(name="Ailment", value=GG.cleanWordDash(mv.meta.ailment.name))
        if mv.damage_class.name == "status":
            em.add_field(name="Ailment Chance", value=f"100%")
        else:
            em.add_field(name="Ailment Chance", value=f"{str(mv.meta.ailment_chance)}%")

    target = pb.move_target(mv.target.name)
    em.add_field(name="Targets", value=GG.getDescriptionText(target.descriptions), inline=False)

    return em


def setup(bot):
    log.info("Loading Move Cog...")
    bot.add_cog(Move(bot))
