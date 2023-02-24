from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



Base = declarative_base()


LB = '{'
RB = '}'


class Square(Base):
    __tablename__='square'

    id = Column('id', Integer, primary_key=True)
    hash = Column('hash', ForeignKey('hash.id'))

    sx = Column('sx', Integer)
    sy = Column('sy', Integer)

    state = Column('state', CHAR)

    def __init__(self, x, y, hash):
        self.sx = x
        self.sy = y
        self.id = x * 3 + y + hash * 9
        self.hash = hash
        self.state = '_'

    def __repr__(self):
        return f"<{self.hash}> [{self.sx},{self.sy}]:{self.state}"

class Hash(Base):
    __tablename__ = 'hash'

    id = Column('id', Integer, primary_key=True)
    game = Column("game", ForeignKey('game.id'))
    hx = Column('hx', Integer)
    hy = Column('hy', Integer)
    status = Column('status', CHAR)

    def __init__(self, hx, hy, game):
        self.hx = hx
        self.hy = hy
        self.id = hx * 3 + hy + game * 9
        self.game = game
        self.status = '_'

    def __repr__(self):
        return f"{LB}{self.game}{RB}<{self.hx},{self.hy}>:{self.status}"

class Game(Base):
    __tablename__ = 'game'
    id = Column('id', Integer, primary_key=True)
    winner = Column('winner', CHAR)

    def __init__(self, id):
        self.id = id
        self.winner = '_'

    def __repr__(self):
        return '{'+f"{self.id}:{self.winner}}}"


engine = create_engine('sqlite:///', echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()


game = Game(1)
session.add(game)

for x in range(3):
    for y in range(3):
        h = Hash(x,y, game.id)
        session.add(h)

        for sx in range(3):
            for sy in range(3):
                s = Square(sx, sy, h.id)
                session.add(s)


session.commit()


res = session.query(Hash, Square).filter(Hash.id == Square.hash)
for r in res:
    print (r)
