import pokebase as pb
import discord
import utils.globals as GG
import json


def getWeakness(pokemon):
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
    else:
        type = pb.type_(GG.cleanWordSpace(type.name))
        for y in type.damage_relations.double_damage_from:
            WT1.append(f"{GG.cleanWordDash(y['name'])}")
        for y in type.damage_relations.no_damage_from:
            IT1.append(f"{GG.cleanWordDash(y['name'])}")
        for y in type.damage_relations.half_damage_from:
            RT1.append(f"{GG.cleanWordDash(y['name'])}")

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

    ITString = ""
    for x in IT:
        x = json.loads(x)
        ITString += f"{x['type']}: {x['effectiveness']}\n"

    RTString = ""
    for x in RT:
        x = json.loads(x)
        RTString += f"{x['type']}: {x['effectiveness']}\n"

    em.add_field(name="Damaged normally by", value=DNBString)
    em.add_field(name="Weak to", value=WTString)
    em.add_field(name="Immune to", value=ITString)
    em.add_field(name="Resistant to", value=RTString)

    return em


if __name__ == '__main__':
    print("Wooper:")
    getWeakness('wooper')
    print("\nGyarados:")
    getWeakness('Gyarados')
