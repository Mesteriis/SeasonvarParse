from models.tables import serials, CONNECTION


def GetAllSerials():
    result = serials.select()
    return CONNECTION.execute(result).fetchall()


def GetSerialsById(id):
    result = serials.select().where(serials.c.id == str(id))
    return CONNECTION.execute(result).fetchall()


def GetSerialsByTitle(title):
    result = serials.select().where(serials.c.title == str(title))
    return CONNECTION.execute(result).fetchall()


def InsertSerial(title):
    ins = serials.insert().values(title = title) 
    result = CONNECTION.execute(ins)
    return result.lastrowid