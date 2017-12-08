import discord

from src.data import session, Server, Channel

class Preferences(object):

	def __init__(self):
		pass

	@classmethod
	def ignored(cls, channel_id):
		return Channel.get_channel(channel_id).ignore

	@classmethod
	def ignore(cls, channel_id):
		c = Channel.get_channel(channel_id)
		c.ignore = True
		session.commit()

	@classmethod
	def unignore(cls, channel_id):
		c = Channel.get_channel(channel_id)
		c.ignore = False
		session.commit()

	@classmethod
	def collect_channels(cls, servers):
		for s in servers:
			db_item = Server.add_server(s.name, s.id)
			for c in s.channels:
				if c.type == discord.ChannelType.text:
					Channel.add_channel(c.name, c.id, db_item)

	@classmethod
	def new_server(cls, server):
		d = Server.add_server(s.name, s.id)
		for c in server.channels:
			if c.type == discord.ChannelType.text:
				Channel.add_channel(c.name, c.id, db_item)

