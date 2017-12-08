from unittest.mock import Mock, patch
import json
import asyncio

import discord
from nose.tools import assert_true, assert_list_equal, assert_dict_equal, assert_equals

from src import bot
from tests.utils import assert_in_list

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