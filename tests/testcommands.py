from unittest.mock import Mock, patch
import asyncio

from nose.tools import assert_true, assert_equals

from src.commands import Commands

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

    def test_btc_in_circulation(self):
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
            test_data = {
                'ADDRESS' : {
                    'final_balance' : 0.004,
                    'n_tx': 2,
                    'total_received' : 0.004
                }
            }

            api.return_value = test_data
            async def assert_message(channel, embed=None):
                if embed:
                    for field in embed.fields:
                        if field.name in pretty_names.keys():
                            assert_equals(str(test_data['ADDRESS'][pretty_names[field.name]]),
                                          field.value)
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

    def test_conversion_to_usd(self):
        test_input = ('0.004', 'BTC')
        test_result = 60
        with patch('src.btcapi.BTCClient.ticker') as api:
            api.return_value = {'USD' : {'last' : test_result}}
            async def assert_message(channel, embed=None):
                if embed:
                    out = '{} BTC -> ~${} USD'.format(test_input[0],
                                                      float(test_input[0]) * test_result)
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
