from ..bot import commands

@commands.register('An example of the command extension system (for developers).')
async def extension_example(channel, arg):
	await commands.client.send_message(channel, 'Hello world!')
