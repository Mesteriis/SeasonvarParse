from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, TEXT
from middleware.config import DB_DIALECT, DB_HOST, DB_NAME, DB_PASSWORD, DB_USER

engine = create_engine(f"{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4")
meta = MetaData()

voices = Table(
    'voices', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('voice', String(255, collation="utf8mb4_bin"), nullable=False, unique=True)
)

serials = Table(
    'serials', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255, collation="utf8mb4_bin"), nullable=False, unique=True)
)

seazons = Table(
    'seasons', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255, collation="utf8mb4_bin"), nullable=False),
    Column('description', TEXT(collation="utf8mb4_bin"), nullable=False),
    Column('number', Integer),
    Column('serialId', Integer, ForeignKey('serials.id')),
    Column('link', String(255, collation="utf8mb4_bin")),
    Column('image', String(255, collation="utf8mb4_bin"), nullable=False)
)

episodes = Table(
    'episodes', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255, collation="utf8mb4_bin")),
    Column('seazonId', Integer, ForeignKey('seasons.id')),
    Column('voiceId', Integer, ForeignKey('voices.id')),
    Column('number', Integer, nullable=False),
    Column('link', String(255, collation="utf8mb4_bin"), nullable=False),
    Column('subtitles', String(255, collation="utf8mb4_bin"))
)

meta.create_all(engine)

CONNECTION = engine.connect()
result = voices.select()
result = CONNECTION.execute(result).fetchall()
if(result == []):
    data = ['','HDRezka', 'BaibaKo','FOX','LostFilm','NewStudio','AniDub','Оригинал','Пифагор','Субтитры','кубик в кубе']
    for i in data:
        ins = voices.insert().values(voice = i) 
        CONNECTION.execute(ins)