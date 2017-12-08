import os, sys
from unittest.mock import Mock, patch
import json
import asyncio

from nose.tools import assert_true, assert_list_equal, assert_dict_equal, assert_equals
import discord

sys.path.append('../src')

from btcapi import *
from commands import Commands
import bot
from preferences import *

class TestBTCAPIClient(object):

	@classmethod
	def setup_class(cls):
		cls.mock_get_patcher = patch('src.bot.requests.get')
		cls.mock_get = cls.mock_get_patcher.start()

	@classmethod
	def teardown_class(cls):
		cls.mock_get_patcher.stop()

	
	def test_ticker_when_200(self):

		test_data = '{"USD" : {"15m" : 478.68, "last" : 478.68, "buy" : 478.55, "sell" : 478.68,  "symbol" : "$"}}'
		
		self.mock_get.return_value = Mock()
		self.mock_get.return_value.content = test_data
		
		output = BTCClient.ticker()
		assert_dict_equal(output, json.loads(test_data))

	def test_ticker_when_not_200(self):
		self.mock_get.return_value = Mock()
		self.mock_get.return_value.ok = False

		output = BTCClient.ticker()

		assert_equals(output, None)


class TestBot(object):

	@classmethod
	def setup_class(cls):
		cls.mock_BTC_ticker_patcher = patch('src.btcapi.BTCClient.ticker')
		cls.mock_BTC_ticker = cls.mock_BTC_ticker_patcher.start()
		cls.mock_client_instance_patcher = patch('src.bot.client')
		cls.mock_client_instance = cls.mock_client_instance_patcher.start()
		cls.loop = asyncio.get_event_loop()

	@classmethod
	def teardown_class(cls):
		cls.mock_BTC_ticker_patcher.stop()
		cls.mock_client_instance_patcher.stop()
		cls.loop.close()

	def test_ticker(self):
		'''
		Tests the bot ticker functionality.
		Mocks the client instance to absorb calls to the change_presence method.
		Asserts value passed to change_presence is in the possible_results list.
		Passes debug to the ticker function to cause it to terminate (which it normally will never do)
		and to make the calls to sleep a lot shorter.
		'''
		async def go():
			test_data = {'USD' : {"15m" : 478.68, "last" : 478.68, "buy" : 478.55, "sell" : 478.68,  "symbol" : "$"}}

			async def test_change_presence(game=None):
				possible_results = [discord.Game(name='15m: $478.68'),
									discord.Game(name='Last: $478.68'),
									discord.Game(name='Buy: $478.55'),
									discord.Game(name='Sell: $478.68')]

				assert_in_list(game, possible_results)
				return asyncio.sleep(0.001)

			self.mock_BTC_ticker.return_value = test_data

			self.mock_client_instance = Mock()
			self.mock_client_instance.change_presence.side_effect = test_change_presence
			bot.client = self.mock_client_instance
			await bot.ticker(debug=True)
		
		self.loop.run_until_complete(go())

	def test_responds_if_ignored(self):
		'''
		Ensures the bot will not respond to a channel that is ignored
		'''
		with patch('src.preferences.Preferences.ignored') as check:
			check.return_value = True
			
			self.mock_client_instance.send_message = Mock()
			self.mock_client_instance = Mock(spec=discord.Client)
			self.mock_client_instance.user = Mock(spec=discord.User)
			self.mock_client_instance.user.name = 'baz'
			
			message = Mock(spec=discord.Message)
			message.author = Mock(spec=discord.User)
			message.author.name = 'bar'
			message.content = 'do nothing'
		
			self.loop.run_until_complete(bot.handle_message(message, self.mock_client_instance))
			assert_true(not self.mock_client_instance.send_message.called)
			

class TestCommands(object):

	@classmethod
	def setup_class(cls):
		cls.c = Commands(Mock())
		async def assert_fileuploaded(channel, filename):
			'''
			Ensures the filename is expected and that the file upload is called
			'''
			assert_equals(filename, 'plot.png')
		cls.c.client.send_file = assert_fileuploaded
		asyncio.set_event_loop(asyncio.new_event_loop())
		cls.loop = asyncio.get_event_loop()


	@classmethod
	def teardown_class(cls):
		cls.loop.close()

	def test_market_value(self):
		'''
		Ensures the correct api endpoint is called and the file is uploaded
		'''
		with patch('src.btcapi.BTCClient.market_price_chart') as api:
			api.side_effect = Mock()
			self.loop.run_until_complete(self.c.market_value(None, None))
			assert_true(api.side_effect.called)

	def test_BTC_in_circulation(self):
		with patch('src.btcapi.BTCClient.BTC_in_circulation_chart') as api:
			api.side_effect = Mock()
			self.loop.run_until_complete(self.c.BTC_in_circulation(None, None))
			assert_true(api.side_effect.called)

	def test_market_cap(self):
		with patch('src.btcapi.BTCClient.market_cap_chart') as api:
			api.side_effect = Mock()
			self.loop.run_until_complete(self.c.market_cap(None, None))
			assert_true(api.side_effect.called)

	def test_trade_volume(self):
		with patch('src.btcapi.BTCClient.trade_volume_chart') as api:
			api.side_effect = Mock()
			self.loop.run_until_complete(self.c.trade_volume(None, None))
			assert_true(api.side_effect.called)

	def test_balance(self):
		with patch('src.btcapi.BTCClient.balance') as api:
			pretty_names = {
				'Final balance' : 'final_balance', 
				'Number of transactions' : 'n_tx', 
				'Total received' : 'total_received'
				}
			test_data= {'ADDRESS' : {
						'final_balance' : 0.004, 
						'n_tx': 2, 
						'total_received' : 0.004
						}}

			api.return_value = test_data
			async def assert_message(channel, embed=None):
				if embed:
					for field in embed.fields:
						if field.name in pretty_names.keys():
							assert_equals(str(test_data['ADDRESS'][pretty_names[field.name]]), field.value)
						else:
							raise AssertionError('Unexpected field name.')
				else:
					raise AssertionError('No embed provided with message.')
			self.c.client.send_message.side_effect = assert_message
			self.loop.run_until_complete(self.c.balance(None, 'ADDRESS'))

	def test_conversion_to_bitcoin(self):
		test_input = ('60', 'USD')
		test_result = 0.004
		with patch('src.btcapi.BTCClient.tobtc') as api:
			api.return_value = test_result
			async def assert_message(channel, embed=None):
				if embed:
					assert_equals(embed.description, '60 USD -> 0.004 BTC')
				else:
					raise AssertionError('No embed provided with message')
			self.c.client.send_message.side_effect = assert_message
			self.loop.run_until_complete(self.c.convert(None, test_input[0], test_input[1]))

	def test_conversion_to_USD(self):
		test_input = ('0.004', 'BTC')
		test_result = 60
		with patch('src.btcapi.BTCClient.ticker') as api:
			api.return_value = {'USD' : {'last' : test_result}}
			async def assert_message(channel, embed=None):
				if embed:
					out = '{} BTC -> ~${} USD'.format(test_input[0], float(test_input[0]) * test_result)
					assert_equals(embed.description, out)
				else:
					raise AssertionError('No embed provided with message')
			self.c.client.send_message.side_effect = assert_message
			self.loop.run_until_complete(self.c.convert(None, test_input[0], test_input[1]))

	def test_ignore(self):
		'''
		Ensures the ignore command ignores properly
		'''
		with patch('src.preferences.Preferences.ignore') as api:
			api.side_effect = Mock()
			channel = Mock()
			channel.id = '1'
			self.loop.run_until_complete(self.c.ignore(channel, None))
			assert_true(api.side_effect.called)

	def test_unignore(self):
		'''
		Ensures the unignore command works properly
		'''
		with patch('src.preferences.Preferences.unignore') as api:
			api.side_effect = Mock()
			channel = Mock()
			channel.id = '1'
			self.loop.run_until_complete(self.c.unignore(channel, None))
			assert_true(api.side_effect.called)

def assert_in_list(element, l):
	for e in l:
		if element.name == e.name:
			return True

	raise AssertionError('Element does not exist in list. {}'.format(element))



