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
    
nest_asyncio.apply()
bot.run(TOKEN)