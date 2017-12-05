import datetime

import matplotlib.pyplot as plt

def plot_api(j):
	'''
	Plots data from the blockchain.info api.
	'''
	x = [datetime.datetime.utcfromtimestamp(value['x']) for value in j['values']]
	y = [value['y'] for value in j['values']]
	plt.title(j['name'])
	plt.ylabel(j['unit'])
	plt.xlabel(j['period'])
	plt.plot_date(x, y, linestyle='-')
	plt.savefig('plot.png')