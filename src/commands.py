import re

import discord

from src.btcapi import BTCClient

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
					'commands' : {'function' : self.commands, 'description' : 'List of commands' }
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
				await self.client.send_message(channel, '{} is not a command. Use !commands for list of all commands.'.format(c))

	async def convert(self, channel, amount, currency):
		'''
		Calls the BTC API to convert a currency then responds to the user with the bitcoin value.
		'''
		result = BTCClient.tobtc(amount, currency)
		m = '{} {} -> {} BTC'.format(amount, currency, result)
		e = discord.Embed(title='', description=m)
		e.set_author(name='blockchain.info')
		await self.client.send_message(channel, embed=e)

	async def market_value(self, channel, timespan):
		'''
		Makes a call to the BTC api for market_value data then plots the data and responds.
		'''
		if not timespan:
			timespan = '5weeks'
		BTCClient.market_price_chart(timespan)
		await self.client.send_file(channel, 'plot.png')

	async def BTC_in_circulation(self, channel, timespan):

		if not timespan:
			timespan = '5weeks'
		BTCClient.BTC_in_circulation_chart(timespan)
		await self.client.send_file(channel, 'plot.png')

	async def market_cap(self, channel, timespan):
		if not timespan:
			timespan = '5weeks'
		BTCClient.market_cap_chart(timespan)
		await self.client.send_file(channel, 'plot.png')

	async def trade_volume(self, channel, timespan):
		if not timespan:
			timespan = '5weeks'
		BTCClient.trade_volume_chart(timespan)
		await self.client.send_file(channel, 'plot.png')

	async def commands(self, channel, arg):
		e = discord.Embed(title='Commands', author=self.client.user.name)
		for x in self.commands.keys():
			e.add_field(name=x, value=self.commands[x]['description'])

		await self.client.send_message(channel, embed=e)