from models.tables import voices, CONNECTION


def GetAllVoices():
    result = voices.select()
    return CONNECTION.execute(result).fetchall()


def GetVoicesById(id):
    result = voices.select().where(voices.c.id == str(id))
    return CONNECTION.execute(result).fetchall()


def GetVoicesByVoice(voice):
    result = voices.select().where(voices.c.voice == str(voice))
    return CONNECTION.execute(result).fetchall()


def InsertVoice(voice):
    ins = voices.insert().values(voice = voice) 
    result = CONNECTION.execute(ins)
    return result.lastrowid