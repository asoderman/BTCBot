# BTC Bot for Discord

Features: 

* Bitcoin ticker in the "playing" section
* Convert USD -> BTC
* Check bitcoin balance via public key
* Upload chart in chat (on request)

Supported charts:
* Market Value
* Bitcoins in circulation
* Market capitalization
* Trade Volume

## Extending the project:
BTCBot has a modularized command system making it easy to add features in the form of commands.
To create a command:
1. Fork the repo
2. Create your script in src/commandext
3. Import the `commands` global from bot.py
4. Use the `@commands.register(<description>)` decorator on your function
5. The bot will use your function name for the command name
6. See [testcom.py](https://github.com/asoderman/BTCBot/blob/dev/src/commandext/testcom.py) for a reference implementation
7. Submit your pull request