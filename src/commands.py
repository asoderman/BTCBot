import re
import datetime

import discord

from src.btcapi import BTCClient
from src.preferences import Preferences
from src.utils import load_text_commands

class Commands(object):
	'''
	Class containing static methods to handle messages the bot receives.
	'''
	def __init__(self, client):
		self.client = client
		self.commands = {
					'convert': {'function' : self.convert, 'description' : 'Convert USD to BTC'}, 
					'marketvalue' : {'function' : self.market_value, 'description' : 'Market value chart'},
					'circulation' : {'function' : self.BTC_in_circulation, 'description' : 'Bitcoins in circulation chart'},
					'marketcap' : {'function' : self.market_cap, 'description' : 'Market capitalization chart' },
					'tradevolume' : {'function' : self.trade_volume, 'description' : 'USD trade volume chart' },
					'commands' : {'function' : self.commands, 'description' : 'List of commands' },
					'balance' : {'function' : self.balance, 'description' : 'Shows balance info on a public address'},
					'ignore' : {'function' : self.ignore, 'description' : 'Have the bot stop posting here' },
					'unignore' : {'function' : self.unignore, 'description' : 'Have bot start posting again'}
					}

	async def _parse_command(self, channel, message):
		'''
		Parses message for command then calls proper command from dict.
		'''

		s = re.search(r'!([A-z]+) ?([A-z0-9]*)', message)
		if s:
			c = s.group(1) #command
			arg = s.group(2) #arg
			try:
				await self.commands[c]['function'](channel, arg)
			except KeyError as e:
				try:
					await self.text_command(channel, c)
				except (KeyError, NoCommandException) as ke:
					await self.client.send_message(channel, '{} is not a command. Use !commands for list of all commands.'.format(c))

	async def text_command(self, channel, command):
		j = load_text_commands()
		if j:
			await self.client.send_message(channel, j[command])
		else:
			raise NoCommandException()
	async def convert(self, channel, amount, currency):
		'''
		Calls the BTC API to convert a currency then responds to the user with the bitcoin value.
		Or calls the ticker api to convert BTC -> USD
		'''
		if currency.upper() == 'USD':
			result = BTCClient.tobtc(amount, currency)
			m = '{} {} -> {} BTC'.format(amount, currency, result)
		elif currency.upper() == 'BTC':
			result = BTCClient.ticker()['USD']['last'] * float(amount)
			m = '{} BTC -> ~${:,.2f} USD'.format(amount, result)
		e = discord.Embed(title='', description=m)
		e.set_author(name='blockchain.info')
		await self.client.send_message(channel, embed=e)

	async def chart(self, channel, timespan, api_call):
		'''
		General chart function
		'''
		if not timespan:
			timespan = '5weeks'
		api_call(timespan)
		await self.client.send_file(channel, 'plot.png')

	async def market_value(self, channel, timespan):
		'''
		Makes a call to the BTC api for market_value data then plots the data and responds.
		'''
		await self.chart(channel, timespan, BTCClient.market_price_chart)

	async def BTC_in_circulation(self, channel, timespan):
		await self.chart(channel, timespan, BTCClient.BTC_in_circulation_chart)

	async def market_cap(self, channel, timespan):
		await self.chart(channel, timespan, BTCClient.market_cap_chart)

	async def trade_volume(self, channel, timespan):
		await self.chart(channel, timespan, BTCClient.trade_volume_chart)

	async def commands(self, channel, arg):
		e = discord.Embed(title='BTCBot Commands', color=0x0dedf1)
		e.set_author(name=self.client.user.name, icon_url=self.client.user.default_avatar_url)
		message = ''
		for x in self.commands.keys():
			message += str('**!' + x +'** - ' + self.commands[x]['description'] + '\n')
		e.add_field(name='Commands', value=message, inline=False)

		message = ''
		for t in load_text_commands().keys():
			message += str('**!' + t + '**\n')
		e.add_field(name='Text Only Commands', value=message, inline=False)

		await self.client.send_message(channel, embed=e)

	async def balance(self, channel, address):
		j = BTCClient.balance(address)
		e = discord.Embed(title='Balance', color=0x56f442)
		for item in ['final_balance', 'n_tx', 'total_received']:
			if item is 'n_tx':
				name = 'Number of transactions'
			else:
				name = item.replace('_', ' ').capitalize()
			e.add_field(name=name, value=j[address][item], inline=True)
		foot = 'Balance generated on: {} UTC'.format(datetime.datetime.utcnow().strftime("%a, %d %B %Y %I:%M%p"))
		e.set_footer(text=foot)
		await self.client.send_message(channel, embed=e)

	async def ignore(self, channel, arg):
		Preferences.ignore(channel.id)

	async def unignore(self, channel, arg):
		Preferences.unignore(channel.id)
		
	def register(self, description=None):
		'''
		A decorator to register a function with the command class
		Usage: 
		@c.register('optional description')
		async def my_command(self):
			pass


		'''
		def wrapper(f):
			setattr(self, f.__name__, f)
			self.commands[f.__name__] = {'function' : getattr(self, f.__name__), 'description' : description}
		return wrapper

class NoCommandException(Exception):
	pass