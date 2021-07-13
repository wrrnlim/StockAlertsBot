import discord
from discord_slash import SlashCommand # pip install -U discord-py-slash-command
import requests
from discord.ext import tasks

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)

@client.event
async def on_ready():
  print('Logged in as {0.user}'.format(client))
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='tickers'))
  checkForex.start()

guild_ids = ['YOUR SERVER ID']

########## PING ##########
@slash.slash(name='ping',description='Shows latency (connection speed) of bot', guild_ids=guild_ids)
async def ping(ctx):
  embed = discord.Embed(
    description = f'I am up and running with a latency of {round(client.latency * 1000)}ms!',
    color=0x29a8dd
  )
  await ctx.send(embed=embed)

########## FOREX ##########
@slash.slash(name='forex',description='Get forex rate. Syntax: /forex USD CAD', guild_ids=guild_ids)
async def forex(ctx, cur1, cur2):
  cur1 = cur1.upper()
  cur2 = cur2.upper()

  # get exchange rate
  rate = getForex(cur1,cur2)

  # send reply
  embed = discord.Embed(
    description = f'The current exchange rate for {cur1}/{cur2} is ```{rate}```\nData retrieved from [European Central Bank](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html)',
    color=0x29a8dd
  )
  embed.set_author(name = 'Foreign Exchange Conversion')
  await ctx.send(embed=embed)

def getForex(cur1, cur2):
  # get exchange rate
  url = 'https://theforexapi.com/api/latest?'
  params = {'base':cur1, 'symbols':cur2}
  response = requests.get(url, params=params).json()
  rate = response['rates'][cur2]
  print(f'{cur1}/{cur2} rate: {rate}')
  return rate

########## ALERTS ##########
@slash.slash(name='setAlert',description='Sets an alert for forex prices', guild_ids=guild_ids)
async def setAlert(ctx, cur1, cur2, limit):
  cur1 = cur1.upper()
  cur2 = cur2.upper()

  # Store reminder
  if 'alerts' not in db:
    db['alerts'] = []
  
  db['alerts'].append({'cur1':cur1, 'cur2':cur2, 'limit':float(limit)})

  embed = discord.Embed(
    description = f'You will be alerted when {cur1}/{cur2} forex rate is < {limit}. Exchange rates are checked every hour.',
    color=0x29a8dd
  )
  await ctx.send(embed=embed)

@slash.slash(name='clearAlerts',description='Removes all forex rate alerts', guild_ids=guild_ids)
async def clearAlerts(ctx):
  if 'alerts' in db:
    db['alerts'] = []
    embed = discord.Embed(
      description = 'All alerts have been removed.',
      color=0x29a8dd
    )
    await ctx.send(embed=embed)
  else:
    embed = discord.Embed(
      description = 'There are no alerts set. Use `/setAlert` to set one!',
      color=0x29a8dd
    )
    await ctx.send(embed=embed)

@slash.slash(name='viewAlerts',description='Lists all forex rate alerts', guild_ids=guild_ids)
async def viewAlerts(ctx):
  if 'alerts' in db and len(db['alerts']) > 0:
    alerts = db['alerts']
    alertList = ''
    for alert in alerts:
      alertList = alertList + '●    ' + alert['cur1'] + '/' + alert['cur2'] +' @ ' + str(alert['limit']) + '\n'
    embed = discord.Embed(
      description = 'Foreign Exchange Rate Alerts',
      color=0x29a8dd
    )
    embed.add_field(name='Current Alerts', value= alertList, inline = True)
    await ctx.send(embed=embed)
  else:
    embed = discord.Embed(
      description = 'There are no alerts set. Use `/setAlert` to set one!',
      color=0x29a8dd
    )
    await ctx.send(embed=embed)

# @slash.slash(name='clear',description='Clears repl dictionary', guild_ids=guild_ids)
# async def clear(ctx):
#   db.clear()
#   await ctx.send('Database cleared.')

# @slash.slash(name='ratetest',description='sets rate for testing', guild_ids=guild_ids)
# async def ratetest(ctx, rate):
#   db['USDCAD'] = float(rate)
#   await ctx.send(f'USD/CAD rate set to {rate} for testing purposes')

########## BACKGROUND TASK ##########
@tasks.loop(seconds=3600) # checks every hour
async def checkForex():
  store = False
  # get alerts
  if 'alerts' not in db:
    db['alerts'] = []
  for alert in db['alerts']:
    cur1 = alert['cur1'].upper()
    cur2 = alert['cur2'].upper()
    limit =  alert['limit']
    
    # get exchange rate
    forexKey = cur1 + cur2
    rate = getForex(cur1, cur2)

    if forexKey not in db:
      db[forexKey] = -1
    
    if rate != db[forexKey]: # if rate is new
      store = True
      if db[forexKey] < limit and db[forexKey] > 0:
        # get channel
        channel = client.get_channel(864298120632336406)
        print(channel)
        # send message
        embed = discord.Embed(
          description = f'The exchange rate for {cur1}/{cur2} is currently less than {limit}! The current rate is ```{rate}```',
          color=0x29a8dd
        )
        embed.set_author(name = 'Foreign Exchange Alert')
        await channel.send(embed=embed)
        print(f'The exchange rate for {cur1}/{cur2} is currently less than {limit}! The current rate is {rate}')
    else:
      print(f'No new exchange rate was found. Current rate: {db[forexKey]}')
    
  # Store new rate
  if store:
    db[forexKey] = rate # store rate as {USDCAD:1.249...}
    print(f'New rate of {db[forexKey]} stored!')
    store = False
    
client.run('Place your Discord Bot secret key here')