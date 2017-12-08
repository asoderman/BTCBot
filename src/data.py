import os 
import sys

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

try:
	engine = create_engine(os.environ('DATABASE_URL')) # Production
except:
	engine = create_engine('sqlite:///dev.db') # Development/Tests

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Models

class Server(Base):
	__tablename__ = 'server'

	id = Column(Integer, primary_key=True)
	name = Column(String(64), nullable=False)
	channels = relationship('Channel', back_populates='server')

	@classmethod
	def add_server(cls, name, server_id):
		try:
			s = Server(name=name, id=int(server_id))
			session.add(s)
			session.commit()
			return s
		except:
			session.rollback()
			return cls.get_server(server_id)

	@classmethod
	def get_server(cls, server_id):
		return session.query(Server).filter_by(id=server_id).first()

class Channel(Base):
	__tablename__ = 'channel'

	id = Column(Integer, primary_key=True)
	server_id = Column(Integer, ForeignKey('server.id'))
	server = relationship('Server', back_populates='channels')
	name = Column(String(64), nullable=False)
	ignore = Column(Boolean, nullable=False)

	# Queries
	@classmethod
	def add_channel(cls, name, channel_id, server):
		try:
			c = Channel(id=int(channel_id), name=name, ignore=False)
			server.channels.append(c)
			session.add(c)
			session.commit()
			return c
		except:
			session.rollback()
			return cls.get_channel(channel_id)

	@classmethod
	def get_channel(cls, channel_id):
		return session.query(Channel).filter_by(id=channel_id).first()

Base.metadata.create_all(engine)

class AlreadyExistsException(Exception):
	pass
