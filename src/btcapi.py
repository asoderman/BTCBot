import json

import requests

from src.plot import plot_api

BASE = 'https://blockchain.info'

class BTCClient(object):

	@classmethod
	def ticker(cls):
		'''
		/ticker API endpoint.
		returns python dict from the JSON data.
		'''
		r = requests.get(BASE + '/ticker')
		if r.ok:
			return json.loads(r.content)
		else:
			return None

	@classmethod
	def tobtc(cls, value, currency):
		'''
		/tobtc API endpoint.
		'''
		d = {'value' : value, 'currency' : currency}
		r = requests.get(BASE + '/tobtc', params=d)
		return r.content.decode('UTF-8')

	@classmethod
	def chart_api(cls, chart, timespan):
		'''
		Partial function for charts API
		chart specifies the chart being accessed
		returns json data
		'''

		d = {'timespan' : timespan, 'format': 'json'}
		r = requests.get(BASE + '/charts/{}'.format(chart), params=d)
		return json.load(r.content)

	@classmethod
	def market_price_chart(cls, timespan):
		'''
		/market-price API endpoint.
		Does not return anything however a plot is saved to plot.png
		'''
		j = chart_api('market-price', timespan)
		plot_api(j)

