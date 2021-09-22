from operator import and_
from models.tables import serials, seazons, CONNECTION


def GetSeazonById(id):
    result = seazons.select().where(seazons.c.id == str(id))
    return CONNECTION.execute(result).fetchall()


def GetSeazonByTitle_SerialId(title, serialId):
    result = seazons.select().where(
        and_(
            seazons.c.title == str(title),
            seazons.c.serialId == str(serialId)
        )
    )
    return CONNECTION.execute(result).fetchall()


def InsertSeazon(title, description, number, serialId, link):
    ins = seazons.insert().values(title = title, description = description, number = number, serialId = serialId, link = link) 
    result = CONNECTION.execute(ins)
    return result.lastrowid