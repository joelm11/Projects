import discord
from discord.ext import commands
import random
import os
from dotenv import load_dotenv
from soupscrape import scraper

load_dotenv()
token = os.getenv('Discord_Token')

bot = commands.Bot(command_prefix='!')
output = scraper()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

"""
ToDo:
    Eliminate command after it has been typed
"""
@bot.command(name='commands')
async def messager(ctx):
    commands ="""\n!getwinrate <SummonerName> :    Gets winrate for given summoner name
\n!getcounters <ChamptoCounter> :     Gets highest winrate counters for given champion
\n!getbuild <ChampName> :     Gets core build order for given champion
\n!getskills <ChampName> :    Gets skill levelling order for given champion
\n!getbs <ChampName> :    Combination of !getbuild and !getskills
\n!getrunes <ChampName> :     Gets runepage for given champion
\n!getall <ChampName> :   Combination of !getbuild, !getskills, and !getrunes
 """
    await ctx.send(commands)
    
@bot.command(name='getwinrate')
async def messager(ctx,summonerName):
    #context.message to see context of command
    #print(arg1)
    output = scraper()
    output.getWinrate(summonerName)
    await ctx.send(output.infoString)

@bot.command(name='getcounters')
async def messager(ctx, *, champName):
    champName = champName.replace(" ", "")
    output = scraper()
    output.getCounters(champName)
    await ctx.send(output.infoString)

@bot.command(name = 'getbuild')
async def messager(ctx, *, champName):
    champName = champName.replace(" ", "")
    output = scraper()
    output.getbuildsbetter(champName)
    await ctx.send(file=discord.File(output.infoString))

@bot.command(name = 'getskills')
async def messager(ctx, *, champName):
    champName = champName.replace(" ", "")
    output = scraper()
    output.getskills(champName)
    await ctx.send(file=discord.File(output.infoString))

@bot.command(name = 'getbs')
async def messager(ctx, *, champName):
    champName = champName.replace(" ", "")
    output = scraper()
    output.getbuildandskills(champName)
    await ctx.send(file=discord.File(output.infoString))

@bot.command(name = 'getrunes')
async def messager(ctx, *, champName):
    champName = champName.replace(" ", "")
    output = scraper()
    output.getrunes(champName)
    await ctx.send(file=discord.File(output.infoString))

@bot.command(name = 'getall')
async def messager(ctx, *, champName):
    champName = champName.replace(" ", "")
    output = scraper()
    SkillsandItems, Runes = output.getall(champName)
    await ctx.send(file=discord.File(SkillsandItems, Runes))
    await ctx.send(file=discord.File(Runes))

@bot.event
async def on_command_error(ctx, error):
    await ctx.send('That is not a valid command! For a list of valid commands, use !commands')
    print(error)

bot.run(token)
