# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 23:37:59 2021

@author: kneub
"""

import os
import nest_asyncio

import discord
from dotenv import load_dotenv

from discord.ext import commands

import json_updater
import plotter
import modeling

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    
@bot.command(name='goose')
async def send_goose(ctx):
    await ctx.send("Geese are cool!")
    
@bot.command(name='update')
async def update_name(ctx, *argv):
    if len(argv) == 0:
        await ctx.send("'!update <player_name>' (don't include the <'s)")
    else:
        name = ""
        if len(argv) == 1:
            name = argv[0]
        else:
            for arg in argv:
                name+=arg+" "
            name = name[:-1]
        return_string = json_updater.update_player(name.lower())
        await ctx.send(return_string)
        
@bot.command(name='remove')
async def remove_name(ctx, *argv):
    if len(argv) == 0:
        await ctx.send("'!remove <player_name>' (don't include the <'s)")
    else:
        name = ""
        if len(argv) == 1:
            name = argv[0]
        else:
            for arg in argv:
                name+=arg+" "
            name = name[:-1]
        return_string = json_updater.remove_player(name.lower())
        await ctx.send(return_string)

@bot.command(name='xp')
async def xp(ctx, *argv):
    if len(argv) == 0 or len(argv) == 1:
        await ctx.send("'!xp <skill> <player_name>' (don't include the <'s)")
    else:
        name = ""
        if len(argv) == 2:
            name = argv[1]
        else:
            for arg in argv[1:]:
                name+=arg+" "
            name = name[:-1]
        return_string = plotter.xp(name,argv[0])
        await ctx.send(return_string)
        
@bot.command(name='rank')
async def rank(ctx, *argv):
    if len(argv) == 0:
        await ctx.send("'!rank <player_name>' (don't include the <'s)")
    else:
        name = ""
        if len(argv) == 1:
            name = argv[0]
        else:
            for arg in argv:
                name+=arg+" "
            name = name[:-1]
        data = json_updater.read_json('clan.json')
        if name.lower() not in data.keys():
            await ctx.send(name+" not found in clan database.\n"+
                           "Use: !update <player_name>' to add to database (don't include the <'s)")
        else:
            modeling.plot_ranks(name,False)
            await ctx.send(file=discord.File('rank_plot.png'))
            os.remove('rank_plot.png')
            
@bot.command(name='points')
async def plot_point_table(ctx, *argv):
    if len(argv) == 0:
        modeling.plot_point_table()
        await ctx.send(file=discord.File('pvm_points.jpg'))
    else:
        name = ""
        if len(argv) == 1:
            name = argv[0]
        else:
            for arg in argv:
                name+=arg+" "
            name = name[:-1]
        data = json_updater.read_json('clan.json')
        if name.lower() not in data.keys():
            await ctx.send(name+" not found in clan database.\n"+
                           "Use: !update <player_name>' to add to database (don't include the <'s)")
        else:
            modeling.plot_point_table(name)
            await ctx.send(file=discord.File('pvm_points.jpg'))
    
    
nest_asyncio.apply()
bot.run(TOKEN)