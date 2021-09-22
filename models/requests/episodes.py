from operator import and_
from models.tables import episodes, seazons, CONNECTION


def GetEpisodeById(id):
    result = episodes.select().where(episodes.c.id == str(id))
    return CONNECTION.execute(result).fetchall()


def GetEpisodeByLink(link):
    result = episodes.select().where(episodes.c.link == str(link))
    return CONNECTION.execute(result).fetchall()


def GetEpisodeByTitle_SeazonId(title, seazonId):
    result = seazons.select().where(
        and_(
            episodes.c.title == str(title),
            episodes.c.seazonId == str(seazonId)
        )
    )
    return CONNECTION.execute(result).fetchall()


def InsertEpisode(title, voiceId, number, seazonId, link, subtitles = ''):
    ins = episodes.insert().values(title = title, voiceId = voiceId, number = number, seazonId = seazonId, link = link, subtitles = subtitles) 
    result = CONNECTION.execute(ins)
    return result.lastrowid