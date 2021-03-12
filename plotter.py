# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 01:57:44 2021

@author: kneub
"""

import json_updater
from matplotlib import pyplot as plt
import numpy as np
from constants import *

def xp(player_name,skill="Overall"):
    
    data = json_updater.read_json('clan.json')
    player = player_name.lower()
    return_string = ''
    
    if skill not in skill_list:
        return_string += "Skill not found in skill list, defaulting to 'Overall'\n"
        return_string += "Type skill with a capital first letter.\n\n"
        skill = "Overall"
    
    if player not in data.keys():
        return_string += player_name+" not in clan database.\n"
        return_string += "If this is your name, please type !update "+player_name+"\n"
        return return_string
    
    xp = np.array([])
    for name in data.keys():
        xp = np.append(xp,data[name]['skills'][skill]['xp'])
        if name == player:
            xp_player = data[name]['skills'][skill]['xp']

    return_string += player_name+" "+skill+" xp:\t "+format(xp_player,",")+"\n"
    return_string += "Clan average "+skill+" xp:\t "+format(int(round(np.mean(xp))),",")+"\n"
    return_string += "Clan median "+skill+" xp:\t "+format(int(round(np.median(xp))),",")
    return return_string

def plot_level(skill="Overall"):
    
    return

def plot_pvm(boss="Nightmare"):
    
    return