# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 14:55:22 2021

@author: kneub
"""

import numpy as np
from matplotlib import pyplot as plt

import helper_functions as hf
from constants import pvm_list, skill_list

def check_player(bingo_data, player):
    
    for user in bingo_data.keys():
        if player.lower() == bingo_data[user]['rsn'].lower():
            return True
        
    return False

def get_skill_activity(bingo_data, skill, player):
    
    # Initialize
    skill = hf.find_skill(skill)
    day = np.array([])
    xp  = np.array([])

    for discord_user in bingo_data:
        player_data = bingo_data[discord_user]
        if player_data["rsn"].lower() == player.lower():
            data = player_data["data"]
            for i in data:
                cur_day = i[0]/(24*60*60)
                cur_xp  = i[1]["skills"][skill]["xp"]
                
                # Monochromatic check
                if len(xp) != 0:
                    if cur_xp < xp[-1]:
                        continue
                
                # Append list
                day = np.append(day, cur_day)
                xp  = np.append(xp,  cur_xp)
    
    # Take difference                            
    xp = xp-xp[0]
    xp_delta = xp[-1]
    
    return (xp_delta, day, xp)

def get_boss_activity(bingo_data, boss, player):
    
    # Initialize
    boss = hf.find_boss(boss)
    day = np.array([])
    kc  = np.array([])

    for discord_user in bingo_data:
        player_data = bingo_data[discord_user]
        if player_data["rsn"].lower() == player.lower():
            data = player_data["data"]
            for i in data:
                cur_day = i[0]/(24*60*60)
                cur_kc  = i[1]["pvm"][boss]["value"]
                
                # Monochromatic check
                if len(kc) != 0:
                    if cur_kc < kc[-1]:
                        continue
                
                # Append list
                day = np.append(day, cur_day)
                kc  = np.append(kc,  cur_kc)
                                
    kc = kc-kc[0]
    kc_delta = kc[-1]
    
    return (kc_delta, day, kc)

def get_team_skill_activity(bingo_data, skill, team, top=3):
    
    team_xp = 0
    xp_list = np.array([])
    name_list = np.array([])
    top_players = np.array([])
    
    # Get team xp
    for discord_user in bingo_data:
        player_data = bingo_data[discord_user]
        if player_data["team"].lower() == team.lower():
            xp_delta, day, xp = get_skill_activity(bingo_data, skill, player_data["rsn"])
            
            xp_list = np.append(xp_list, xp_delta)
            name_list = np.append(name_list, player_data["rsn"])
            team_xp+=xp_delta
    
    # Find top players on team
    zero_log = xp_list != 0
    xp_list = xp_list[zero_log]
    name_list = name_list[zero_log]
    while len(top_players) < top:
        
        if len(xp_list) == 0:
            break
        
        max_xp = max(xp_list)
        max_xp_log = max_xp == xp_list
        max_xp_name = name_list[max_xp_log]
        
        xp_list = xp_list[~max_xp_log]
        name_list = name_list[~max_xp_log]
        
        top_players = np.append(top_players, { 'name' : max_xp_name, 'value' : max_xp })
        
    return (team_xp, top_players)

def get_team_boss_activity(bingo_data, boss, team, top=3):
    
    team_kc = 0
    kc_list = np.array([])
    name_list = np.array([])
    top_players = np.array([])
    
    # Get team xp
    for discord_user in bingo_data:
        player_data = bingo_data[discord_user]
        if player_data["team"].lower() == team.lower():
            kc_delta, day, kc = get_boss_activity(bingo_data, boss, player_data["rsn"])
            
            kc_list = np.append(kc_list, kc_delta)
            name_list = np.append(name_list, player_data["rsn"])
            team_kc+=kc_delta
    
    # Find top players on team
    zero_log = kc_list != 0
    kc_list = kc_list[zero_log]
    name_list = name_list[zero_log]
    while len(top_players) < top:
        
        if len(kc_list) == 0:
            break
        
        max_kc = max(kc_list)
        max_kc_log = max_kc == kc_list
        max_kc_name = name_list[max_kc_log]
        
        kc_list = kc_list[~max_kc_log]
        name_list = name_list[~max_kc_log]
        
        if len(max_kc_name) == 1:
            top_players = np.append(top_players, { 'name' : max_kc_name, 'value' : max_kc })
        else:
            for name in max_kc_name:
                top_players = np.append(top_players, { 'name' : [name], 'value' : max_kc })
        
    return (team_kc, top_players)
            
def plot_player_activity(bingo_data, stat, player):
    
    # Check if stat is boss or skill
    label = ""
    if hf.find_boss(stat) in pvm_list:
        stat = hf.find_boss(stat)
        data = get_boss_activity(bingo_data, stat, player)
        label = "Kc"
    elif hf.find_skill(stat) in skill_list:
        stat = hf.find_skill(stat)
        data = get_skill_activity(bingo_data, stat, player)
        label = "Xp"
    else:
        return "ERROR: Invalid stat"
    
    # Instantiate data
    total_value = data[0]
    day         = data[1]
    values      = data[2]
    
    # Create Figure
    fig = plt.figure()
    plt.plot(day,values)
    
    # Coloring
    color = "#121111"
    plt.gca().set_facecolor(color)
    plt.gca().spines['top'].set_color('white')
    plt.gca().spines['right'].set_color('white')
    plt.gca().spines['bottom'].set_color('white')
    plt.gca().spines['left'].set_color('white')
    plt.gca().xaxis.label.set_color('white')
    plt.gca().tick_params(axis='x', colors='white')
    plt.gca().yaxis.label.set_color('white')
    plt.gca().tick_params(axis='y', colors='white')
    
    # Labels
    plt.xlabel("Days")
    plt.ylabel(label)
    plt.gca().set_ylim(bottom=0, top=None)
    plt.gca().set_title(f"{player.replace('_',' ')}'s Bingo Plot - {stat}",color='white')
    
    # Annotations
    note = f"Total {label}: {int(total_value):,}"
    plt.text(0,0.88*plt.gca().get_ylim()[1], note, size=15, color='white') 

    # Save and close
    plt.savefig(fname='player_activity',transparent=False, bbox_inches='tight',facecolor='#121111')
    plt.close()
    
    return fig

def plot_team_activity(bingo_data, stat, team):
    
    # Check if stat is boss or skill
    label = ""
    return_string = "FAIL"
    if hf.find_boss(stat) in pvm_list:
        stat = hf.find_boss(stat)
        data = get_team_boss_activity(bingo_data, stat, team, 10)
        label = "Kc"
    elif hf.find_skill(stat) in skill_list:
        stat = hf.find_skill(stat)
        data = get_team_skill_activity(bingo_data, stat, team, 10)
        label = "Xp"
    else:
        return "ERROR: Invalid stat"

    # Instantiate data
    total_value = data[0]
    top_players = data[1]
    
    return_string = f"**Team {team.replace('_',' ')} - {stat} {label}: {int(total_value):,}**\n"
    count = 1
    for tup in top_players:
        name = str(tup['name'][0])
        value = tup['value']
        return_string+=f"{str(count)}. {name.replace('_',' ')}: {int(value):,} {label.lower()}\n"
        count+=1
        
    return return_string