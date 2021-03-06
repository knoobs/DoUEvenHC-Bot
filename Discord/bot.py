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
import helper_functions as hf

from constants import pvm_list, skill_list, command_list, bot_channel, blacklist_channels

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
nest_asyncio.apply()

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send("Hey there bucko... you don't have permission for that!")
    
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
    
    # Check channel
    message_channel = ctx.message.channel
    if str(message_channel) in blacklist_channels:
        print("Command received in unapproved channel")
        approved_channel = discord.utils.get(ctx.guild.channels, name=bot_channel)
        await approved_channel.send(f"{ctx.author.mention} Please use this channel for the bot.")
        return
        
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
        return_string += "\n**USE !updatebingo IF TRYING TO UPDATE BINGO**"
        await ctx.send(return_string)
        
@bot.command(name='update_all')
@commands.has_permissions(administrator=True)
async def update_all(ctx):
    await ctx.send("Updating all players... expect 20+ minute downtime.")
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game("Updating Players..."))
    return_string = json_updater.update_all()
    await bot.change_presence(status=discord.Status.online)
    await ctx.send(return_string)
        
@bot.command(name='remove')
@commands.has_permissions(administrator=True)
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
    
    # Check channel
    message_channel = ctx.message.channel
    if str(message_channel) in blacklist_channels:
        print("Command received in unapproved channel")
        approved_channel = discord.utils.get(ctx.guild.channels, name=bot_channel)
        await approved_channel.send(f"{ctx.author.mention} Please use this channel for the bot.")
        return
    
    if len(argv) == 0:
        return_string = "'*!rank <player_name>*' returns rank plot with highlighted player\n"
        return_string += "'*!rank <player_name> zoom+*' zooms in on lower rank\n"
        return_string += "\tAdd as many +'s as you'd like: i.e. zoom++++"
        await ctx.send(return_string)
    else:
        name = ""
        zoom = 'none'
        for arg in argv:
            if 'zoom+' in arg:
                zoom = str(arg.count('+'))
                continue
            name+=arg+" "
        name = name[:-1]
        data = json_updater.read_json('clan.json')
        if name.lower() not in data.keys():
            await ctx.send(name+" not found in clan database.\n"+
                           "Use: '*!update <player_name>*' to add to database")
        else:
            plotter.plot_ranks(name,False,zoom)
            await ctx.send(file=discord.File('rank_plot.png'))
            #os.remove('rank_plot.png')
            
@bot.command(name='points')
async def plot_point_table(ctx, *argv):
    
    # Check channel
    message_channel = ctx.message.channel
    if str(message_channel) in blacklist_channels:
        print("Command received in unapproved channel")
        approved_channel = discord.utils.get(ctx.guild.channels, name=bot_channel)
        await approved_channel.send(f"{ctx.author.mention} Please use this channel for the bot.")
        return
    
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
    
    # Check channel
    message_channel = ctx.message.channel
    if str(message_channel) in blacklist_channels:
        print("Command received in unapproved channel")
        approved_channel = discord.utils.get(ctx.guild.channels, name=bot_channel)
        await approved_channel.send(f"{ctx.author.mention} Please use this channel for the bot.")
        return
    
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
            
@bot.command(name='getrank')
async def getrank(ctx, *argv):          
    if len(argv) <= 1:
        return_string = "'*!getrank <hc_rank> <pvm_points>*' returns rank of player with that rank and points\n"
        await ctx.send(return_string)
    else:
        hc_rank = argv[0]
        pvm_points = argv[1]
        if not (hc_rank.isdigit() and pvm_points.replace('.','').isdigit()):
            await ctx.send("'*!getrank <hc_rank> <pvm_points>*' (inputs must be numbers)")
        else:
            cc_rank = modeling.get_rank(hc_rank,pvm_points)
            await ctx.send("Hc Rank: "+hc_rank+", Points: "+pvm_points+", => Clan Rank: "+str(cc_rank.title()))
            
@bot.command(name='reload')
async def reload_cog(ctx, extension):
    await ctx.send(f"Attempting to reload cog: {extension}")
    bot.unload_extension(f"Cogs.{extension}")
    bot.load_extension(f"Cogs.{extension}")
    
for cog in os.listdir("./Cogs"):
    if cog.endswith('.py'):
        bot.load_extension(f'Cogs.{cog[:-3]}')
        
bot.run(TOKEN)