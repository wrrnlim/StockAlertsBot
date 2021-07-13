# StockAlertsBot
![work in progress](https://img.shields.io/badge/build-work%20in%20progress-yellow)
Discord bot for setting your own stock/forex price alerts!

## Dependencies
- [Discord.py](https://discordpy.readthedocs.io/en/stable/)
- Discord slash commands: `pip install -U discord-py-slash-command`

## Current commands
Currently, the bot has the following commands:
- `/ping` - check the latency of the bot.
- `/forex currency1 currency2` - View current exchange rate of the currencies.
- `/setalert cur1 cur2 limit` - Set an alert for forex rate. Bot will send a message when exchange rate is less than `limit`.
- `/clearalerts` - Clear all previously set alerts.
- `/viewalerts` - View all set alerts.



