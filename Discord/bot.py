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
import helper_functions as hf

from constants import pvm_list, skill_list, command_list

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    
@bot.command(name='goose')
async def send_goose(ctx):
    await ctx.send("Geese are cool!")
    
@bot.command(name='commands')
async def list_commands(ctx):
    return_string = "**LIST OF BOT COMMANDS**\n"
    for command in command_list:
        command_text = "*"+command+"* -"
        return_string += command_text + ' '*(20-len(command_text))
        return_string += command_list[command]+"\n"
    await ctx.send(return_string)
    
@bot.command(name='update')
async def update_name(ctx, *argv):
    if len(argv) == 0:
        await ctx.send("'*!update <player_name>*'")
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
        await ctx.send("'*!remove <player_name>*'")
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
        return_string = "'*!xp <skill> <player_name>*'\n"
        return_string += "**I am a smart command and can recognize most shorthands for skills**"
        await ctx.send(return_string)
    else:
        name = ""
        for arg in argv[1:]:
            name+=arg+" "
        name = name[:-1]
        
        skill = hf.find_skill(argv[0])
        data = json_updater.read_json('clan.json')
        
        if skill not in skill_list:
            return_string = "Could not find skill: "+argv[0]+"\n"
            return_string += "@ Hardc0reBruh to add it to skill name shorthands\n"
        elif name.lower() not in data.keys():
            return_string = name+" not found in clan database.\n"
            return_string += "Use: '*!update <player_name>*' to add to database"
        else:
            return_string = plotter.plot_xp(name,skill)
        await ctx.send(return_string)
        
@bot.command(name='rank')
async def rank(ctx, *argv):
    if len(argv) == 0:
        await ctx.send("'*!rank <player_name>*'")
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
                           "Use: '*!update <player_name>*' to add to database")
        else:
            plotter.plot_ranks(name,False)
            await ctx.send(file=discord.File('rank_plot.png'))
            os.remove('rank_plot.png')
            
@bot.command(name='points')
async def plot_point_table(ctx, *argv):
    if len(argv) == 0:
        plotter.plot_point_table()
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
                           "Use: '*!update <player_name>*' to add to database")
        else:
            plotter.plot_point_table(name)
            await ctx.send(file=discord.File('pvm_points.jpg'))
            
@bot.command(name='top')
async def plot_top_boss(ctx, *argv):
    if len(argv) == 0:
        return_string = "'*!top <boss>*' returns top 10 hc killers of that boss w/ kc\n"
        return_string += "'*!top <x> <boss>*' returns top x hc killers of that boss w/ kc\n"
        return_string += "'*!top rank <boss>*' returns top 10 hc killers of that boss w/ rank\n"
        return_string += "'*!top rank <x> <boss>*' returns top x hc killers of that boss w/ rank\n"
        return_string += "**I am a smart command and can recognize most shorthands for bosses**"
        await ctx.send(return_string)
    else:
        boss = ""
        num = 10
        mode = 'value'
        for arg in argv:
            if arg.isdigit():
                num = int(arg)
                continue
            if arg == "rank":
                mode = 'rank'
                continue
            boss+=arg+" "
        boss = boss[:-1]
        boss = hf.find_boss(boss)
        if boss in pvm_list:
            plotter.plot_top_boss(boss,num,mode)
            await ctx.send(file=discord.File('top_boss.png'))
        else:
            return_string = "Unrecognized boss name - @ Hardc0reBruh to add it to shorthands\n"
            return_string += "type '*!top*' for help"
            await ctx.send(return_string) 
    
nest_asyncio.apply()
bot.run(TOKEN)