# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 13:28:20 2021

@author: kneub
"""

import discord
from discord.ext import commands

import read_hiscores as rh
import json_updater as ju
import bingo_helper as bh
import helper_functions as hf
from constants import pvm_list, skill_list, bot_channel, blacklist_channels

import json
import os
import shutil
from datetime import date
from datetime import datetime
import random
import time

class Bingo(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='debug')
    async def bingo(self, ctx):
        
        message_channel = ctx.message.channel
        if str(message_channel) in blacklist_channels:
            print("Command received in unapproved channel")
            approved_channel = discord.utils.get(ctx.guild.channels, name=bot_channel)
            await approved_channel.send(f"{ctx.author.mention} Please use this channel for the bot.")
            return
        
        names = [i.name for i in ctx.guild.channels]
        print(names)
        
        #await ctx.send(str(is_admin))
        
    @commands.command(name='signupcount')
    async def signupcount(self, ctx):
        bingo_data = ju.read_json("Bingo/bingo.json")
        players = len(bingo_data)
        await ctx.send(players)
        
    @commands.command(name='signupbingobundle')
    async def troll(self, ctx):
        await ctx.send(f"Nice try you silly goose {ctx.author.mention}")
        
    @commands.command(name='create_bingo')
    @commands.has_permissions(administrator=True)
    async def create_category(self, ctx, *, name):
        await ctx.guild.create_category(name)
        
        category = discord.utils.get(ctx.guild.categories, name=name)
        await ctx.guild.create_text_channel("bingo-signups", category=category)
        
        channel = discord.utils.get(ctx.guild.channels, name="bingo-signups")
        message = "Please send a message with the RSN of the account you wish to signup on"
        await channel.send(message)
        
        empty_data = {}
        if os.path.isfile("./Bingo/bingo.json"):
            date_string = str(date.today())
            shutil.move("./Bingo/bingo.json",f"./Archive/bingo_{date_string}.json")
            
        with open("./Bingo/bingo.json", 'w') as write_file:
            json.dump(empty_data, write_file)
            
    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel) == "bingo-signups":
            name = message.author.name
            number = message.author.discriminator
            content = message.content
            
            if name != "BeepBoopTestingTime" or content.startswith('!'):
            
                print(f"{name}#{number}: {content}")
                
                soup = rh.read_hiscores(content.lower())
                text = [i for i in soup.text.split('\n') if i != '']
                rsn = rh.check_existence(text)
                print(f"\t{rsn}")
                
                if rsn:
                    emoji = '\N{THUMBS UP SIGN}'
                    await message.add_reaction(emoji)
                    bingo_data = ju.read_json("./Bingo/bingo.json")
                    bingo_data.update({ name+"#"+number : { 'rsn' : content.strip().replace(' ','_') } })
                    with open("./Bingo/bingo.json", 'w') as write_file:
                        json.dump(bingo_data, write_file)
                else:
                    emoji = '\N{THUMBS DOWN SIGN}' 
                    await message.add_reaction(emoji)
                    await message.channel.send(f"Invalid RSN, try again {message.author.mention}")
                    
    @commands.command(name='assign_teams')
    @commands.has_permissions(administrator=True)
    async def assign_teams(self, ctx, *, team_string):
        # Parse teams
        teams = [i.strip().replace(' ','_').lower() for i in team_string.split(',')]
        return_string = ""
               
        # Closing sign-ups
        signups_open = False
        for i in ctx.guild.channels:
            if i.name=="bingo-signups":
                signups_open =True
        return_string += "_Checking if sign-ups are still open..._\n"
        if signups_open:
            return_string += "\tClosing sign-ups...\n"
            channel = discord.utils.get(ctx.guild.channels, name="bingo-signups")
            await channel.edit(name="signups-closed")
            return_string += "\tSign-ups closed.\n"
        else:
            return_string+="\tBingo already closed.\n"
        return_string += "\n"
        
        # Check sign-ups list
        return_string += "_Checking sign-ups..._\n"
        bingo_data = ju.read_json("./Bingo/bingo.json")
        signups = []
        for discord_user in bingo_data:
            signups.append(bingo_data[discord_user]['rsn'].lower())
        for team in teams:
            if team not in signups:
                return_string+=f"\tERROR: {team.replace('_',' ')} did not signup\n"
        return_string += "\n"
        
        # Check Team Data
        return_string += "_Checking data for the following teams:_\n"
        for team in teams:
            return_string+=f"\t**Team:** {team}\n"
            text_file = f"team_{team}.txt"
            if os.path.isfile(f"./Bingo/{text_file}"):
                return_string+="\t\tTeam file found\n"
            else:
                return_string+=f"\t\tERROR: Cannot find '{text_file}'\n"
        return_string+="\n"
                
        # Return if error(s) exist
        if "ERROR" in return_string:
            return_string+="**1 or more error(s) exist. Please rework and try again**"
            await ctx.send(return_string)
            return
        
        # Sort team names/players
        print("Sorting team names")
        return_string += "_Sorting Team Data..._\n"
        team_names = {}
        for team in teams:
            team_names.update({ team : [] })
            with open(f"./Bingo/team_{team}.txt",'r') as read_file:
                names = [i.replace('\n','').strip() for i in read_file.readlines()]
                team_names[team] = names
        return_string += "\n"      
        print("\tFinished sorting team names")
        
        
        # Create team roles
        print("Creating roles")
        guild = ctx.guild
        for team in team_names:
            role_name = f"Team_{team}"
            role_name = role_name.replace("_"," ")
            if role_name not in [i.name for i in ctx.guild.roles]:
                R, G, B = random.randint(0,255), random.randint(0,255), random.randint(0,255)
                await guild.create_role(name=role_name, hoist=True, color=discord.Color.from_rgb(R,G,B))

        print("\tFinished creating roles")
        
        # Assign teams
        print("Assigning teams...")
        return_string += "_Assigning Teams..._\n"
        warning_string = ""
        memberList = ctx.guild.members
        names = [member.name for member in memberList]
        print(f"Looping through {str(len(bingo_data))} players")
        for discord_user in bingo_data:
            print(f"Working on user: {discord_user}")
            player_data = bingo_data[discord_user]
            player_rsn = player_data['rsn']
            
            if discord_user.split('#')[0] == "Soft to Hard":
                print(f"Skipping {discord_user}")
                continue
            
            # Check if team data already exists
            if 'team' in player_data.keys():
                print("debug1")
                warning_string+=f"\tWARNING: team data for {player_rsn} already exists. Overriding...\n"
            
            # Check if team leader
            if player_rsn.lower() in teams:
                print(f"{player_rsn} = team {player_rsn}")
                player_data.update({ 'team' : player_rsn.lower() })
                player_data.update({ 'leader' : True })
            else:
                found_team = False
                for team in teams:
                    if player_rsn in team_names[team]:
                        print(f"{player_rsn} = team {team}")
                        player_data.update({ 'team' : team })
                        found_team = True
                if not found_team:
                    print(f"Team not found for {player_rsn}")
                    return_string += f"ERROR: {player_rsn} not drafted"
                    continue
                player_data.update({ 'leader' : False })
                
            # Give player the team role in discord
            user_name = discord_user.split("#")[0]
            user_num  = discord_user.split("#")[1]
            user_team = player_data["team"]
            for member in memberList:
                if member.name == user_name and member.discriminator == user_num:
                    role_name = f"Team_{user_team}"
                    role_name = role_name.replace("_"," ")
                    role = discord.utils.get(ctx.guild.roles, name=role_name)
                    try:
                        await member.add_roles(role)
                        time.sleep(0.5)
                        print(" ")
                    except:
                        print(f"Assigning failed for {user_name}\n")
                    
        print("\tFinished assigning teams")
        
        print("Updating bingo data")
        with open("./Bingo/bingo.json",'w') as write_file:
            json.dump(bingo_data,write_file)
        print("\tFinished updating bingo data")
            
        return_string+="\n"  
         
        # Return
        await ctx.send(return_string)
        
    @commands.command(name='team')
    async def check_team(self, ctx):
        name = ctx.author.name
        number = ctx.author.discriminator
        
        bingo_data = ju.read_json("./Bingo/bingo.json")
        player_data = bingo_data[f"{name}#{number}"]
        if 'team' in player_data.keys():
            await ctx.send(f"You are on team {player_data['team']}.")
        else:
            await ctx.send("You have not been assigned a team yet.")
            
    @commands.command(name='updatebingo')
    @commands.has_permissions(administrator=True)
    async def update_bingo_stats(self, ctx, all_string="user"):
        
        # Check channel
        message_channel = ctx.message.channel
        if str(message_channel) in blacklist_channels:
            print("Command received in unapproved channel")
            approved_channel = discord.utils.get(ctx.guild.channels, name=bot_channel)
            await approved_channel.send(f"{ctx.author.mention} Please use this channel for the bot.")
            return
        
        if not os.path.isfile("./Bingo/bingo.json"):
            await ctx.send("No player data found")
            return
        
        # Get username
        name = ctx.author.name
        number = ctx.author.discriminator
        is_admin = ctx.author.guild_permissions.administrator
        username = f"{name}#{str(number)}"
        
        # Check if updating all
        update_all = False
        if all_string.lower() == "all":
            if is_admin:
                update_all = True
            else:
                await ctx.send("You don't have permission to update everyone")
                return
        
        print("Reading current bingo data")
        bingo_data = ju.read_json("./Bingo/bingo.json")
        current_time = datetime.now()
        for discord_user in bingo_data:
            
            if (not discord_user == username) and (not update_all):
                continue
            
            # Get player data
            player_data = bingo_data[discord_user]
            player_rsn = player_data["rsn"]
            
            # Quit if no assigned team
            if "team" not in player_data.keys():
                await ctx.send("Bingo hasn't started yet, you silly goose")
                return
            
            print(f"\tLooking up hiscores data for: {player_rsn}")
            player_html = rh.read_hiscores(player_rsn, False)
            player_stats = rh.format_hiscores_text(player_html.text)
            if player_stats == "FAIL":
                await ctx.send(f"Cannot find {player_rsn} on hiscores, skipping.")
                continue
            
            # Check if first data point
            if "start_time" not in player_data.keys():
                player_datapoint  = (0,player_stats)
                player_data.update({ "start_time" : current_time.strftime("%m/%d/%Y, %H:%M:%S") })
                player_data.update({ "data" : [] })
            else:
                start_time = datetime.strptime(player_data["start_time"],"%m/%d/%Y, %H:%M:%S")
                dif_time = current_time-start_time
                player_datapoint = (dif_time.total_seconds(),player_stats)
                
            print(f"\tCompiling stats for player: {player_rsn}")    
            player_data["data"].append(player_datapoint)
            
        print("\nUpdating bingo data")
        with open("./Bingo/bingo.json", "w") as write_file:
            json.dump(bingo_data, write_file)
        print("\tUpdate complete.")
        
        if all_string != 'all':
            await ctx.send(f"Update of {player_rsn.replace('_',' ')} complete.")
        else:
            await ctx.send("Update of everyone complete.")
            
    @commands.command(name='export')
    async def export_names(self, ctx):
        
        if not os.path.isfile("./Bingo/bingo.json"):
            await ctx.send("ERROR: No bingo data found.")
            return
        
        bingo_data = ju.read_json("./Bingo/bingo.json")
        with open("./Bingo/bingo_names.txt", "w") as write_file:
            for user in bingo_data:
                write_file.write(bingo_data[user]["rsn"]+"\n")
                
        await ctx.send(file=discord.File("./Bingo/bingo_names.txt"))
                
    @commands.command(name='progress')
    async def plot_activity(self, ctx, *argv):
        
        # Check channel
        message_channel = ctx.message.channel
        if str(message_channel) in blacklist_channels:
            print("Command received in unapproved channel")
            approved_channel = discord.utils.get(ctx.guild.channels, name=bot_channel)
            await approved_channel.send(f"{ctx.author.mention} Please use this channel for the bot.")
            return
        
        # Check for arguments
        print("Progress command received.\n")
        print("Checking arguments (part 1)...")
        if len(argv) < 2:
            return_string = "Invalid command use. Use:\n"
            return_string+= "\t*!progress <skill/boss> <player_name>*\n"
            return_string+= "\t*!progress <skill/boss> team <team_name>*\n"
            print("\tInvalid args")
            await ctx.send(return_string)
            return
        print("\tPASS")
           
        # Check 1st argument is skill/boss
        print("Checking arguments (part 2)...")
        stat = argv[0]
        if not (hf.find_boss(stat) in pvm_list or hf.find_skill(stat) in skill_list):
            return_string = "Invalid command use. Use:\n"
            return_string+= "\t*!progress <skill/boss> <player_name>*\n"
            return_string+= "\t*!progress <skill/boss> team <team_name>*\n"
            print("\tInvalid args")
            await ctx.send(return_string)
            return
        print("\tPASS")
        
        # Check mode
        print("Checking team mode...")
        if argv[1] == "team":
            team_mode = True
            arg_list = argv[2:]
        else:
            team_mode = False
            arg_list = argv[1:]
        print("\tPASS")
        
        # Load bingo data
        print("Loading bingo data...")
        bingo_data = ju.read_json('./Bingo/bingo.json')
        print("\tPASS")
        
        # Check player name
        name = ""
        for arg in arg_list:
            name+=arg+"_"
        name = name[:-1]
        print(f"Checking player {name}...")
        player_existence = bh.check_player(bingo_data, name)
        if not player_existence:
            return_string = f"Player {name.replace('_',' ')} not found."
            print("\tInvalid player name")
            await ctx.send(return_string)
            return
        print(f"\tPASS: {name}")
        
        # Make the image
        print("Making image...\n")
        if team_mode:
            return_string = bh.plot_team_activity(bingo_data, stat, name)
            await ctx.send(return_string)
        else:
            bh.plot_player_activity(bingo_data, stat, name)
            await ctx.send(file=discord.File('player_activity.png'))
            
    @commands.command(name='bingo_remove')
    @commands.has_permissions(administrator=True)
    async def remove_player(self, ctx, *, name):
        name = name.replace(' ','_')
        bingo_data = ju.read_json("./Bingo/bingo.json")
        return_string = ""
        print(name)
        for user in bingo_data:
            if bingo_data[user]['rsn'].lower() == name.lower():
                bingo_data = {key:val for key, val in bingo_data.items() if key != user}
                print("debug2")
                return_string += f"Deleting user {name} from bingo"
                with open("./Bingo/bingo.json", "w") as write_file:
                    json.dump(bingo_data, write_file)
                await ctx.send(return_string)
                
                return                        
        
        if return_string == "":
            await ctx.send("Could not find user in bingo data")
            
    @commands.command(name='bingo_add')
    @commands.has_permissions(administrator=True)
    async def add_late(self, ctx, discord_name, *, name):
        await ctx.send("Im trusting the info above is right... If u see u made a mistake then fix manually ASAP")
        
        name = name.replace(' ','_')
        bingo_data = ju.read_json("./Bingo/bingo.json")
        bingo_data.update({ discord_name : { 'rsn' : name }})
        
        with open("./Bingo/bingo.json", "w") as write_file:
            json.dump(bingo_data, write_file)
            
        await ctx.send("Done. Check json file manually for verification of format")
        
    @commands.command(name='name_change')
    @commands.has_permissions(administrator=True)  
    async def name_change(self, ctx, old_name, new_name):
        # Arguments require _'s
        bingo_data = ju.read_json("./Bingo/bingo.json")
        for user in bingo_data:
            if bingo_data[user]['rsn'].lower() == old_name.lower():
                bingo_data[user]['rsn'] = new_name
                with open("./Bingo/bingo.json", "w") as write_file:
                    json.dump(bingo_data, write_file)
                await ctx.send(f"Name change from {old_name.replace('_',' ')} to {new_name.replace('_',' ')} successful.")
                return
        await ctx.send(f"Player {old_name.replace('_',' ')} not found")
        
    @commands.command(name='remove_fails')
    @commands.has_permissions(administrator=True)
    async def remove_fails(self, ctx, *, name):
        print(f"Attempting to remove fails from {name}")
        name = name.replace(' ','_')
        bingo_data = ju.read_json("./Bingo/bingo.json")
    
        fail_count = 0
        for discord_user in bingo_data:
            player_data = bingo_data[discord_user]
            if player_data["rsn"].lower() == name.lower():
                data = player_data["data"]
                for i in data:
                    if i[1] == "FAIL":
                        print("FAILURE FOUND! Removing...")
                        data.remove(i)
                        fail_count += 1
        
        with open("./Bingo/bingo.json", "w") as write_file:
            json.dump(bingo_data, write_file)
                        
        await ctx.send(f"Removed {str(fail_count)} errored data points.")                            
        
        
def setup(bot):
    bot.add_cog(Bingo(bot))