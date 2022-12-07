from sqlalchemy import create_engine, Column, Integer, String, func, DateTime, TEXT, JSON
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool

import json

DATABASE_CONNECTION_URI = f'postgresql+psycopg2://admin:admin_password@database:5432/db?gssencmode=disable'
engine = create_engine(DATABASE_CONNECTION_URI)


Base = declarative_base()

db_session = scoped_session(sessionmaker(bind=engine))


class User(Base):
    __tablename__ = 'registered_users'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, nullable=True)
    username = Column(String(255))


class Record(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)

    name = Column(String(255))
    phone = Column(String(255))
    cheque_photo = Column(String(255))
    cheque_number = Column(String(255))

    # create_time = Column(DateTime, nullable=True)


Base.metadata.create_all(engine)