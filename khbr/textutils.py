def final_fight_text(source_enemy, new_name):
    key = "{}-{}-{}".format(source_enemy["ObjectId"], source_enemy["Argument1"], source_enemy["Argument2"])
    texts = {
        "2079-1-0": { # Final Xemnas
            "id": 18453,
            "en": """{0} has problem grown even
stronger, and is waiting for us.{{:clear }}This battle began with Ansem's
research, Let´s finish it for him!"""},
        "2140-0-0": { # AX 2
            "id": 18456,
            "en": """Don´t let your guard down. 
{0} may separate us at any time.{{:clear }}Come on, let´s save the world again!"""},
        "2140-1-0": { # AX1
            "id": 18457,
            "en": """The Kingdom Hearts opened the door
to {0}.{{:clear }}We can´t let this chance slip by. It´s
going to be a tough fight, but we can do it!"""}
}
    if key not in texts:
        return ''
    text = dict(texts[key])
    text["en"] = text["en"].format(new_name)
    return text

def create_spoiler_text(spoilers):
    text = ''
    if spoilers["boss"]:
        text += 'BOSSES\n'
        for oldboss in sorted(spoilers["boss"]):
            text += "\t{} became {}\n".format(oldboss, spoilers["boss"][oldboss])
        text += '\n'
    if spoilers["enemy"]:
        text += 'ENEMIES\n'
        for oldenemy in sorted(spoilers["enemy"]):
            text += "\t{} became {}\n".format(oldenemy, spoilers["enemy"][oldenemy])
    return text