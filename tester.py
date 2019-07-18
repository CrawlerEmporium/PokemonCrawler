import pokebase as pb
import discord
import utils.globals as GG

def getMove(move):
    mv = pb.move(GG.cleanWordSpace(move))
    print(GG.cleanWordDash(mv.name))
    print(GG.getFlavorText(mv.flavor_text_entries))
    print("Type: " + GG.cleanWordDash(mv.type.name))
    print("Move Class: " + GG.cleanWordDash(mv.damage_class.name))
    print("Power: " + str(mv.power))
    if mv.accuracy is None:
        print("Accuracy: " + str(mv.accuracy))
    else:
        print("Accuracy: " + str(mv.accuracy) + "%")
    print("PP: " + str(mv.pp))
    if mv.priority > 1:
        print(f"Priority: +{mv.priority}")
    elif mv.priority < 0:
        print(f"Priority: {mv.priority}")
    else:
        print("Priority: Normal")
    target = pb.move_target(mv.target.name)
    print("Targets: " + GG.getDescriptionText(target.descriptions))

    print("Ailment: " + GG.cleanWordDash(mv.meta.ailment.name))
    print("Ailment Chance: " + str(mv.meta.ailment_chance))





if __name__ == '__main__':
    getMove("mega-punch")
    print("--------------------")
    getMove("Thunder-WaVe")
    print("--------------------")
    getMove("EmBeR")
    print("--------------------")
    getMove("Earthquake")
    print("--------------------")
    getMove("helping hand")
    print("--------------------")
    getMove("trick-room")
