import discord
from discord.ext import commands
import os
import io
from dotenv import load_dotenv
from datetime import datetime
import yfinance as yf

load_dotenv()
intents = discord.Intents.all()  # or whichever intents you require
client = commands.Bot(command_prefix='.', intents=intents, help_command=None)

## written by Jovan Milicev

@client.event
async def on_ready():
    print("Initiating....")
    print('We have logged in as {0.user}'.format(client))
    print ("FinanceBot is ready to recieve commands!")
    print ("My ID is : " + str(client.user.id))

@client.command()
async def ping(ctx):
    await ctx.send(f'Response Time: {round(client.latency * 1000)}ms')

@client.command()
async def help(ctx):
    embed = discord.Embed(title="FinanceBot Help Page", description="Documentation for all FinanceBot Commands", color=0x00ff00)
    embed.add_field(name="stock", value="Get info about a stock", inline=False)
    embed.add_field(name="compound", value="Calculate compound interest", inline=False)
    await ctx.send(embed=embed)

@client.group(name = 'compound', invoke_without_command=True)
async def compound(ctx):
        embed = discord.Embed(title="compound", description="compound [type] (capital) (interest) (years)", color=0x00ff00)
        embed.add_field(name="type", value="annual, quarter, monthly", inline=False)
        embed.add_field(name="capital", value="Initial starting quanitity", inline=False)
        embed.add_field(name="interest", value="Written in percent form: 7.5.", inline=False)
        embed.add_field(name="time", value="Amount of years to compound", inline=False)
        await ctx.send(embed=embed)

@compound.command(name = 'annual')
async def compoundCalculate(ctx, capital, interest, time):
    bracket=  (1+float(interest)/(100)) ** float(time)
    final=(bracket*float(capital))
    final = round(final, 2)
    embed = discord.Embed(title=""+str(final), description="Total capital after "+str(time)+" years at "+str(interest)+"%", color=0x00ff00)
    await ctx.send(embed=embed)

@compound.command(name = 'quarter')
async def compoundCalculate(ctx, capital, interest, time):
    bracket=  (1+float(interest)/(100*4)) ** (float(time) * 4)
    final=(bracket*float(capital))
    final = round(final, 2)
    embed = discord.Embed(title="$"+str(final), description="Total capital after "+str(time)+" years at "+str(interest)+"%", color=0x00ff00)
    await ctx.send(embed=embed)

@compound.command(name = 'monthly')
async def compoundCalculate(ctx, capital, interest, time):
    bracket=  (1+float(interest)/(100*12)) ** (float(time) * 12)
    final=(bracket*float(capital))
    final = round(final, 2)
    embed = discord.Embed(title="$"+str(final), description="Total capital after "+str(time)+" years at "+str(interest)+"%", color=0x00ff00)
    await ctx.send(embed=embed)

@client.group(name = 'stock', invoke_without_command=True)
async def stock(ctx):
    embed = discord.Embed(title="stock", description="get stock quotes and related info", color=0x00ff00)
    embed.add_field(name="stock price [ticker]", value="Return the price of a stock", inline=False)
    embed.add_field(name="stock info [ticker]", value="Detailed info on [ticker]", inline=False)
    embed.add_field(name="stock explain [ticker]", value="Detailed business description on [ticker]", inline=False)
    embed.add_field(name="stock optionexp [ticker] [range]", value="List [range] number of option expiry dates from [ticker]", inline=False)
    embed.add_field(name="stock option [ticker] [date]", value="Shows option chain for [ticker] on [date], date in YYYY-MM-DD.", inline=False)
    await ctx.send(embed=embed)

@stock.command(name = 'price')
async def stockprice(ctx, ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period='1d')
    price = data['Close'][0]
    price = round(price, 2)
    name = stock.info['longName']
    currency = stock.info['currency']

    embed = discord.Embed(title=""+str(name), description="$"+str(price)+" "+str(currency), color=0x00ff00)
    await ctx.send(embed=embed)

@stock.command(name = 'info')
async def stockinfo(ctx, ticker):

    stock = yf.Ticker(ticker)
    data = stock.history(period='1d')
    price = data['Close'][0]
    price = round(price, 2)

    name = stock.info['longName']
    currency = stock.info['currency']
    industry = stock.info['industry']
    try:
        pe = stock.info['trailingPE']
    except KeyError:
        pe = "N/A"

    dividendrate = "N/A"
    dividendyield = "N/A"
    dividendyield = "0"
    exdividendstamp = "N/A"
    exdividend = "N/A"

    try:
        dividendrate = stock.info['dividendRate']
        dividendyield = (float(dividendrate)/float(price))*100
        dividendyield = round(dividendyield,2)
        exdividendstamp = stock.info['exDividendDate']
        exdividend = datetime.fromtimestamp(exdividendstamp)
    except TypeError:
        print("internal error was handled (missing dividends)")

    assettype = stock.info['quoteType']

    embed = discord.Embed(title=""+str(name), description=""+str(industry), color=0x00ff00)
    embed.add_field(name="$"+str(price)+" "+str(currency), value="Price", inline=False)
    embed.add_field(name=""+str(dividendrate), value="Dividend Rate", inline=False)
    embed.add_field(name=""+str(dividendyield)+"%", value="Yield", inline=False)
    embed.add_field(name=""+str(pe), value="Trailing P/E", inline=False)
    embed.add_field(name=""+str(assettype), value="Asset Type", inline=False)
    await ctx.send(embed=embed)

@stock.command(name = 'explain')
async def stockinfo(ctx, ticker):

    stock = yf.Ticker(ticker)

    name = stock.info['longName']
    desc = stock.info['longBusinessSummary']

    embed = discord.Embed(title=""+str(name), description=""+str(desc), color=0x00ff00)
    await ctx.send(embed=embed)

@stock.command(name = 'optionexp')
async def stockOptions(ctx, ticker, distance):
    stock = yf.Ticker(ticker)
    name = stock.info['longName']

    opt = stock.options

    embed = discord.Embed(title=""+str(name), description="Option Expiry Dates", color=0x00ff00)

    try:
        for x in range (int(distance)):
            embed.add_field(name=""+str(opt[x]), value=""+str(name), inline=False)
    except IndexError:
            embed.add_field(name="Halted", value="Displayed all available option expiry cycles", inline=False)
    await ctx.send(embed=embed)

@stock.command(name = 'option')
async def stockOptions(ctx, ticker, date):
    stock = yf.Ticker(ticker)
    name = stock.info['longName']

    link = "https://www.barchart.com/stocks/quotes/"+str(ticker)+"/options?expiration="+str(date)+"-m"

    embed = discord.Embed(title=""+str(name), description="Option Chain for date", color=0x00ff00)
    embed.add_field(name=""+str(link), value="Click to view chain", inline=False)

    await ctx.send(embed=embed)



client.run(os.getenv("DISCORD_TOKEN"))
