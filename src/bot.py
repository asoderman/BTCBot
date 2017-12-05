import json
import asyncio
import re
import logging

import discord
import requests

from src.btcapi import BTCClient
from src.utils import load_settings

logging.basicConfig(filename='info.log',level=logging.INFO)
logger = logging.getLogger(__name__)

SETTINGS = load_settings()

CURRENCY = ["USD"]

client = discord.Client()

@client.event
async def on_ready():
	'''
	Called once the bot is ready. Setup code goes here.
	'''
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	asyncio.get_event_loop().create_task(ticker())

@client.event
async def on_message(message):
	'''
	Handles every message the bot sees. Does not respond to its own messages.
	'''
	if client.user.name == message.author.name:
		return
	else:
		if message.content.startswith('!'):
			await Commands._parse_command(message.channel, message.content)
		else:
			for code in CURRENCY:
				s = re.search(r'([\d\.]+).?({})'.format(code), message.content)
				if s:
					logging.info('Converting currency for {}'.format(message.author))
					value = s.group(1)
					currency = s.group(2)
					await Commands.convert(message.channel, value, currency)

async def set_status(message):
	'''
	Sets what the bot is playing.
	'''
	g = discord.Game()
	g.name = message
	await client.change_presence(game=g)

async def ticker(debug=None):
	'''
	Runs infinitely updating the bot 'playing' message to ticker data.
	debug parameter ensures it only runs once and shortens sleep time
	'''
	if debug: 
		s = 0.001 # short sleep for testing/debugging
	else:
		s = 20 # regular sleep in seconds
	while True:
		messages = []
		logging.info('Getting new ticker data.')
		data = BTCClient.ticker()
		if data:
			for key in data['USD'].keys():
				if key == 'symbol':
					continue
				else:
					messages.append("{}: {}{}".format(key.capitalize(), data['USD']['symbol'], data['USD'][key]))	
			i = 0
			while i < 10:
				await set_status(messages[i % len(messages)])
				await asyncio.sleep(s)
				i += 1
		else:
			retry = 60
			await set_status('Could not retrieve BTC data. Retrying in {} seconds'.format(retry))
			asyncio.sleep(retry)
		if debug:
			break

class Commands(object):
	'''
	Class containing static methods to handle messages the bot receives.
	'''

	@classmethod
	async def _parse_command(cls, channel, message):
		'''
		Parses message for command then calls proper command from dict.
		'''
		commands = {'convert': cls.convert, 
					'marketvalue' : cls.market_value,
					'commands' : cls.commands}
		s = re.search(r'!([A-z]+) ?([A-z0-9]*)', message)
		if s:
			c = s.group(1) #command
			arg = s.group(2) #arg
			try:
				await commands[c](channel, arg)
			except KeyError as e:
				await client.send_message(channel, '{} is not a command. Use !commands for list of all commands.'.format(c))

	@classmethod
	async def convert(cls, channel, amount, currency):
		'''
		Calls the BTC API to convert a currency then responds to the user with the bitcoin value.
		'''
		result = BTCClient.tobtc(amount, currency)
		m = '{} {} -> {} BTC'.format(amount, currency, result)
		e = discord.Embed(title='', description=m)
		e.set_author(name='blockchain.info')
		await client.send_message(channel, embed=e)

	@classmethod
	async def market_value(cls, channel, timeframe):
		'''
		Makes a call to the BTC api for market_value data then plots the data and responds.
		'''
		if not timeframe:
			timeframe = '5weeks'
		BTCClient.market_price_chart(timeframe)
		await client.send_file(channel, 'plot.png')

	@classmethod
	async def commands(cls, channel, arg):
		e = discord.Embed(title='Commands', author=client.user.name)
		for x in cls.__dict__.keys():
			if not x.startswith('_'):
				e.add_field(name=x.replace('_', '', value='-'))

		await client.send_message(channel, embed=e)


def run():
	'''
	Runs the bot. (Should only be invoked by run.py)
	'''
	client.run(SETTINGS['token'])