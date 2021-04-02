# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 13:28:20 2021

@author: kneub
"""

import discord
from discord.ext import commands

import read_hiscores as rh
import json_updater as ju

import json
import os
import shutil
from datetime import date
from datetime import datetime
import random
import json

class Bingo(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='bingo')
    async def bingo(self, ctx):
        print([i.name for i in ctx.guild.roles])
        #await ctx.send(f"Bingo Bango Bongo! LIVE from {os.getcwd()}")
        
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
        for discord_user in bingo_data:
            player_data = bingo_data[discord_user]
            player_rsn = player_data['rsn']
            
            # Check if team data already exists
            if 'team' in player_data.keys():
                warning_string+=f"\tWARNING: team data for {player_rsn} already exists. Overriding...\n"
            
            # Check if team leader
            if player_rsn.lower() in teams:
                player_data.update({ 'team' : player_rsn.lower() })
                player_data.update({ 'leader' : True })
            else:
                found_team = False
                for team in teams:
                    if player_rsn in team_names[team]:
                        player_data.update({ 'team' : team })
                        found_team = True
                if not found_team:
                    return_string += f"ERROR: {player_rsn} not drafted"
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
                    await member.add_roles(role)
                    break
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
            
    @commands.command(name='bingo_update')
    @commands.has_permissions(administrator=True)
    async def update_bingo_stats(self, ctx):
        if not os.path.isfile("./Bingo/bingo.json"):
            await ctx.send("No player data found")
            return
        
        print("Reading current bingo data")
        bingo_data = ju.read_json("./Bingo/bingo.json")
        current_time = datetime.now()
        for discord_user in bingo_data:
            
            # Get player data
            player_data = bingo_data[discord_user]
            player_rsn = player_data["rsn"]
            print(f"\tLooking up hiscores data for: {player_rsn}")
            player_html = rh.read_hiscores(player_rsn, False)
            player_stats = rh.format_hiscores_text(player_html.text)
            
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
        
        await ctx.send("Update complete.")
            
    @commands.command(name='export')
    @commands.has_permissions(administrator=True)
    async def export_names(self, ctx):
        
        if not os.path.isfile("./Bingo/bingo.json"):
            await ctx.send("ERROR: No bingo data found.")
            return
        
        bingo_data = ju.read_json("./Bingo/bingo.json")
        with open("./Bingo/bingo_names.txt", "w") as write_file:
            for user in bingo_data:
                write_file.write(bingo_data[user]["rsn"]+"\n")
        
def setup(bot):
    bot.add_cog(Bingo(bot))