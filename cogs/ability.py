import string

import pokebase as pb
import re
import typing
import discord
from discord.ext import commands
import utils.globals as GG
from utils import logger

log = logger.logger


class Ability(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ability(self, ctx, ability=None):
        if ability is None:
            await ctx.send("No ability given, you can use it's name or id number.")
            return
        msg = await ctx.send("Looking up your Ability! Please wait a moment...\n(*This can take a while, the api is slow. Nothing I can do.*)")
        em = await getAbility(ability)
        await msg.edit(content=None, embed=em)

async def getAbility(ability):
    abi = ""
    if isinstance(ability, str):
        abi = pb.ability(GG.cleanWordSpace(ability))
    if isinstance(ability, int):
        abi = pb.ability(ability)
    em = discord.Embed()
    em.set_author(name=GG.getNames(abi.names))
    em.description = GG.getFlavorText(abi.flavor_text_entries)

    for x in abi.effect_entries:
        shortEffect = x.short_effect
        longEffect = x.effect
        if shortEffect == longEffect:
            em.add_field(name="Effect", value=shortEffect)
        else:
            em.add_field(name="Short Effect", value=shortEffect)
            em.add_field(name="Long Effect", value=longEffect)

    POKEMON = ""
    for x in abi.pokemon:
        if x.is_hidden:
            POKEMON += (f"{x.pokemon.name.capitalize()} (★)\n")
        else:
            POKEMON += (f"{x.pokemon.name.capitalize()}\n")
    POKEMON += "\n(★) Indicates a Pokémon's Hidden Ability"

    em.add_field(name="Pokémon that have this ability", value=POKEMON)
    return em


def setup(bot):
    log.info("Loading Ability Cog...")
    bot.add_cog(Ability(bot))