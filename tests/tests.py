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

	@classmethod
	def teardown_class(cls):
		cls.mock_BTC_ticker_patcher.stop()
		cls.mock_client_instance_patcher.stop()

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
		
		loop = asyncio.get_event_loop()
		loop.run_until_complete(go())
		loop.close()

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


def assert_in_list(element, l):
	for e in l:
		if element.name == e.name:
			return True

	raise AssertionError('Element does not exist in list. {}'.format(element))



