from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pro_diplom.config_keys import owner_db, db_name, db_password

engine = create_engine(f"postgresql+psycopg2://{owner_db}:{db_password}@localhost:5432/{db_name}")

Session = sessionmaker(bind=engine)
session = Session()

BASE = declarative_base()


class AllVkUsers(BASE):
    __tablename__ = "all_vk_users"

    Vk_ID = Column(Integer, primary_key=True)
    Name_surname = Column(String(100))


class BotUsers(BASE):
    __tablename__ = "bot_users"

    ID = Column(Integer, primary_key=True)
    bots_owner_vk_id = Column(Integer, ForeignKey("all_vk_users.Vk_ID"))


class SearchedUsers(BASE):
    __tablename__ = "searched_users"
    ID = Column(Integer, primary_key=__tablename__)
    vk_user_id = Column(Integer, ForeignKey("all_vk_users.Vk_ID"))
    owner_search_id = Column(Integer, ForeignKey("bot_users.ID"))
    Name_surname = Column(String(100))
    town = Column(String)
    gender = Column(String(10))


# BASE.metadata.create_all(engine)

def add_users_to_all_vk_users(vk_id, name):
    user = AllVkUsers(Vk_ID=vk_id, Name_surname=name.lower())
    session.add(user)
    session.commit()


def checkallusers(vk_id, name):
    inserting_name = ""
    inserting_id = 0
    userlist = session.query(AllVkUsers).first()
    print(userlist.Vk_ID, userlist.Name_surname)


checkallusers(23432, "ozod ochilov")