import json
import os

def load_settings():
	try:
		with open('settings.json', 'r') as f:
			return json.load(f)
	except:
		return {'token' : os.environ['DISCORD_TOKEN']}

def load_text_commands():
	try:
		with open('text_commands.json', 'r') as f:
			return json.load(f)
	except:
		return None