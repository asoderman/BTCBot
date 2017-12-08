import json
from unittest.mock import Mock, patch

from nose.tools import assert_dict_equal, assert_equals

from src.btcapi import BTCClient

class TestBTCAPIClient(object):

    @classmethod
    def setup_class(cls):
        cls.mock_get_patcher = patch('src.bot.requests.get')
        cls.mock_get = cls.mock_get_patcher.start()

    @classmethod
    def teardown_class(cls):
        cls.mock_get_patcher.stop()

    def test_ticker_when_200(self):

        test_data = ('{"USD" : {"15m" : 478.68, "last" : 478.68, "buy" : 478.55, '
                     '"sell" : 478.68,  "symbol" : "$"}}')

        self.mock_get.return_value = Mock()
        self.mock_get.return_value.content = test_data

        output = BTCClient.ticker()
        assert_dict_equal(output, json.loads(test_data))

    def test_ticker_when_not_200(self):
        self.mock_get.return_value = Mock()
        self.mock_get.return_value.ok = False

        output = BTCClient.ticker()

        assert_equals(output, None)
