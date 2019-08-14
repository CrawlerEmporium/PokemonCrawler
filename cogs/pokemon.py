import string

import pokebase as pb
import re
import typing
import discord
from discord.ext import commands
import utils.globals as GG
from utils import logger

log = logger.logger


class Pokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pokemon(self, ctx, pokemon=None):
        if pokemon is None:
            await ctx.send("No pokemon given, you can use it's name or national pokemon dex number.")
            return
        msg = await ctx.send("Looking up your Pokémon! Please wait a moment...\n(*This can take a while, the api is slow. Nothing I can do.*)")
        try:
            em = await getPokemon(pokemon)
            await msg.edit(content=None, embed=em)
        except:
            error = "Error looking up the Pokémon, please check if you used the command correctly, and if the Pokémon name is spelled correctly.\nUsage: ``#pokemon <pokemon name or national id>``"
            await msg.edit(content=error)

    @commands.command(aliases=['evo','chain'])
    async def evolution(self, ctx, pokemon=None):
        if pokemon is None:
            await ctx.send("No pokemon given, you can use it's name or national pokemon dex number.")
            return
        msg = await ctx.send("Looking up your Pokémon Evolutions! Please wait a moment...\n(*This can take a while, the api is slow. Nothing I can do.*)")
        try:
            em = await getPokemonEvolution(pokemon)
            await msg.edit(content=None, embed=em)
        except:
            error = "Error looking up the Pokémon, please check if you used the command correctly, and if the Pokémon name is spelled correctly.\nUsage: ``#pokemon <pokemon name or national id>``"
            await msg.edit(content=error)


def getEvolution(chain):
    startingPoint = chain.species.name
    log.info(f"Looking up: {GG.cleanWordDash(startingPoint)}")
    endPoint = ""
    if len(chain.evolves_to) > 0:
        for x in chain.evolves_to:
            method, name = EvolveChain(x)
            string = f"**{startingPoint.capitalize()}** > {method.rstrip(', ').rstrip(' ')} > **{name.capitalize()}**"
            startPoint = string
            endPoint += f"{getEvolutionDeeper(startPoint, string, x)}\n"
    return startPoint, endPoint


def getEvolutionDeeper(startPoint, string, chain):
    if len(chain['evolves_to']) > 0:
        for x in chain['evolves_to']:
            method, name = EvolveChain(x)
            string += f"\n{startPoint} > {method.rstrip(', ').rstrip(' ')} > **{name.capitalize()}**"
    return string


def EvolveChain(x):
    name = x['species']['name']
    length = len(x['evolution_details'])
    i = 0
    method = ""
    for y in range(length):
        if i != 0:
            method += ", "
        details = x['evolution_details'][i]
        trigger = details['trigger']['name']
        if trigger == "use-item":
            if details['gender'] is not None:
                if details['gender'] == 1:
                    method += f"Must be female, "
                if details['gender'] == 2:
                    method += f"Must be male, "
            method += f"Use ``{GG.cleanWordDash(details['item']['name'])}``"
        if trigger == "level-up":
            if details['gender'] is not None:
                if details['gender'] == 1:
                    method += f"Must be female, "
                if details['gender'] == 2:
                    method += f"Must be male, "
            if details['relative_physical_stats'] is not None:
                if details['relative_physical_stats'] == 1:
                    method += f"``Attack > Defense``, "
                if details['relative_physical_stats'] == -1:
                    method += f"``Defense > Attack``, "
                if details['relative_physical_stats'] == 0:
                    method += f"``Attack == Defense``, "
            if details['party_species'] is not None:
                method += f"Having ``{GG.cleanWordDash(details['party_species']['name'])}`` in party, then Lv. up "
            if details['known_move'] is not None:
                method += f"Must know ``{GG.cleanWordDash(details['known_move']['name'])}``, then Lv. up "
            if details['known_move_type'] is not None:
                method += f"Must know a ``{GG.cleanWordDash(details['known_move_type']['name'])}`` type move, "
            if details['min_happiness'] is not None:
                if details['min_level'] is None:
                    method += f"Min. Happiness: ``{str(details['min_happiness'])}``, then Lv. up "
                else:
                    method += f"Min. Happiness: ``{str(details['min_happiness'])}``, "
            if details['party_type'] is not None:
                method += f"Having a ``{GG.cleanWordDash(details['party_type']['name'])}`` type pokemon in party, "
            if details['time_of_day'] is not None and details['time_of_day'] != "":
                if details['min_level'] is not None:
                    if details['time_of_day'] == "night":
                        time = "🌙"
                    if details['time_of_day'] == "day":
                        time = "☀"
                    method = method.rstrip("Lv. up ")
                    method += f" Lv. up ``{str(details['min_level'])}`` at {time}"
                else:
                    if details['time_of_day'] == "night":
                        time = "🌙"
                    if details['time_of_day'] == "day":
                        time = "☀"
                    method = method.rstrip("Lv. up ")
                    method += f" Lv. up at {time}"
            else:
                if details['min_level'] is not None:
                    method += f"Lv. up ``{str(details['min_level'])}``"
            if details['location'] is not None:
                method += f" Lv. up in ``{GG.cleanWordDash(details['location']['name'])}``"
            if details['min_affection'] is not None:
                method += f"Min. ❤: ``{str(details['min_affection'])}``"
            if details['needs_overworld_rain'] is True:
                method += " while raining"
            if details['turn_upside_down'] is True:
                method += " while holding device upside down"
            if details['held_item'] is not None:
                method += f" while holding ``{GG.cleanWordDash(details['held_item']['name'])}``"
        if trigger == "trade":
            if details['held_item'] is not None:
                method = f"Trade while holding ``{GG.cleanWordDash(details['held_item']['name'])}``"
            elif details['trade_species'] is not None:
                method = f"Trade with ``{GG.cleanWordDash(details['trade_species']['name'])}``"
            else:
                method = f"Trade"
        if trigger == "shed":
            method = f"Having an extra Poke Ball and empty party slot while evolving"
        i += 1
        method = method.lstrip(" ")
    return method, name


async def getPokemon(pokemon):
    pkmn = ""
    if isinstance(pokemon, str):
        pkmn = pb.pokemon(pokemon.lower().replace("'",""))
    if isinstance(pokemon, int):
        pkmn = pb.pokemon(pokemon)
    em = discord.Embed()

    id = pkmn.id
    spriteUrl = pkmn.sprites.front_default
    spriteUrlShiny = pkmn.sprites.front_shiny
    spriteUrlFemale = pkmn.sprites.front_female
    spriteUrlFemaleShiny = pkmn.sprites.front_shiny_female

    em.set_author(name=GG.cleanWordDash(pkmn.name))
    em.set_thumbnail(url="http://play.pokemonshowdown.com/sprites/xyani/"+ pkmn.name.lower() + ".gif")

    abilities = pkmn.abilities
    if len(abilities) == 3:
        hiddenAbility = GG.cleanWordDash(abilities[0].ability.name)
        ability = GG.cleanWordDash(abilities[1].ability.name)
        ability2 = GG.cleanWordDash(abilities[2].ability.name)
    elif len(abilities) == 2:
        hiddenAbility = GG.cleanWordDash(abilities[0].ability.name)
        ability = GG.cleanWordDash(abilities[1].ability.name)
        ability2 = None
    else:
        hiddenAbility = None
        ability = GG.cleanWordDash(abilities[0].ability.name)
        ability2 = None

    speed = pkmn.stats[0].base_stat
    speedEffort = pkmn.stats[0].effort
    specialDefense = pkmn.stats[1].base_stat
    specialDefenseEffort = pkmn.stats[1].effort
    specialAttack = pkmn.stats[2].base_stat
    specialAttackEffort = pkmn.stats[2].effort
    defense = pkmn.stats[3].base_stat
    defenseEffort = pkmn.stats[3].effort
    attack = pkmn.stats[4].base_stat
    attackEffort = pkmn.stats[4].effort
    hp = pkmn.stats[5].base_stat
    hpEffort = pkmn.stats[5].effort

    types = pkmn.types
    if len(types) == 2:
        type = GG.cleanWordDash(types[1].type.name)
        type2 = GG.cleanWordDash(types[0].type.name)
        color = GG.getColorOfType(type.lower())
    else:
        type = GG.cleanWordDash(types[0].type.name)
        type2 = None
        color = GG.getColorOfType(type.lower())

    height = pkmn.height
    weight = pkmn.weight

    getSpecieName = pkmn.species.url.replace("http://pokeapi.co/api/v2/pokemon-species/","")
    species = pb.pokemon_species(getSpecieName)
    eggGroups = ""
    for x in species.egg_groups:
        eggGroups += f"{GG.cleanWordDash(x.name)}\n"

    flavorText = GG.getFlavorText(species.flavor_text_entries)
    em.description = flavorText

    em.add_field(name="National Dex #", value=id)

    if ability2 is not None:
        em.add_field(name="Ability", value=ability)
        em.add_field(name="Ability", value=ability2)
    else:
        em.add_field(name="Ability", value=ability)
    if hiddenAbility is not None:
        em.add_field(name="Hidden Ability", value=hiddenAbility)

    if type2 is not None:
        em.add_field(name="Type", value=f"{type}/{type2}")
    else:
        em.add_field(name="Type", value=type)

    stats = f"HP: **{hp}**\nAttack: **{attack}**\nDefense: **{defense}**\nSp.Atk: **{specialAttack}**\nSp.Def: **{specialDefense}**\nSpeed: **{speed}**\nTotal: **{int(speed) + int(specialDefense) + int(specialAttack) + int(defense) + int(attack) + int(hp)} ** "
    em.add_field(name="Height", value=f"{round(int(height) * 3.937, 1)}\"")  # decimeters to inches
    em.add_field(name="Weight", value=f"{round(int(weight) * 0.2205, 2)} lbs")  # hectograms to pounds
    em.add_field(name="Egg Groups", value=eggGroups)
    if hpEffort != 0:
        em.add_field(name="EV Gained", value=f"HP: {hpEffort}")
    if attackEffort != 0:
        em.add_field(name="EV Gained", value=f"Attack: {attackEffort}")
    if defenseEffort != 0:
        em.add_field(name="EV Gained", value=f"Defense: {defenseEffort}")
    if specialAttackEffort != 0:
        em.add_field(name="EV Gained", value=f"Sp.Atk: {specialAttackEffort}")
    if specialDefenseEffort != 0:
        em.add_field(name="EV Gained", value=f"Sp.Def: {specialDefenseEffort}")
    if speedEffort != 0:
        em.add_field(name="EV Gained", value=f"Speed: {speedEffort}")

    em.add_field(name="Base Stats", value=stats, inline=False)
    em.colour = int("0x" + color, 0)

    return em

async def getPokemonEvolution(pokemon):
    pkmn = ""
    if isinstance(pokemon, str):
        pkmn = pb.pokemon(pokemon.lower().replace("'",""))
    if isinstance(pokemon, int):
        pkmn = pb.pokemon(pokemon)
    em = discord.Embed()
    em.set_author(name=GG.cleanWordDash(pkmn.name))

    spriteUrl = pkmn.sprites.front_default
    types = pkmn.types
    if len(types) == 2:
        type = GG.cleanWordDash(types[1].type.name)
        type2 = GG.cleanWordDash(types[0].type.name)
        color = GG.getColorOfType(type.lower())
    else:
        type = GG.cleanWordDash(types[0].type.name)
        type2 = None
        color = GG.getColorOfType(type.lower())

    getSpecieName = pkmn.species.url.replace("http://pokeapi.co/api/v2/pokemon-species/","")
    species = pb.pokemon_species(getSpecieName)

    flavorText = GG.getFlavorText(species.flavor_text_entries)
    em.description = flavorText

    getId = re.search(r"/([0-9]*)/$", str(species.evolution_chain.url) + "/").group().replace("/", "")
    evolutionChain = pb.evolution_chain(getId)

    start, chain = getEvolution(evolutionChain.chain)
    if chain != f"{start}\n":
        if chain.startswith(f"{start}\n"):
            chain = chain.replace(f"{start}\n", "", 1)

    em.set_thumbnail(url=spriteUrl)
    if chain != "":
        em.add_field(name="Evolution Chain", value=chain, inline=False)
    else:
        em.add_field(name="Evolution Chain", value="This Pokémon has no evolution chain.")

    em.colour = int("0x" + color, 0)

    return em


def setup(bot):
    log.info("Loading Pokemon Cog...")
    bot.add_cog(Pokemon(bot))
