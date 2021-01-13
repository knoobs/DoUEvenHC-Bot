# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 00:24:30 2021

@author: kneub
"""

import json
import os
import read_hiscores

def update_player(name):
    name = name.lower()
    filename = "clan.json"
    
    # Read existing data
    clan_data = read_json(filename)
            
    # Modify existing data
    player_hiscores = read_hiscores.read_hiscores(name)
    player_dict = read_hiscores.format_hiscores_text(player_hiscores.text)
    if player_dict == "FAIL":
        return "Player update NOT successful"
    clan_data[name] = player_dict
    
    # Write new data
    with open(filename, "w") as write_file:
        json.dump(clan_data, write_file)
    
    return "Player update successful"

def read_json(filename):
    data = {}
    if os.path.exists(filename):
        with open(filename, "r") as read_file:
            data = json.load(read_file)
    
    return data

def remove_player(name):
    name = name.lower()
    filename = "clan.json"
    
    # Read existing data
    clan_data = read_json(filename)
            
    # Modify existing data
    return_string = ""
    if name in clan_data:
        del clan_data[name]
        # Write new data
        with open(filename, "w") as write_file:
            json.dump(clan_data, write_file)
        return_string = "Player removed successfully"
    else:
        return_string = "Player not found in clan database"
    
    return return_string 

    
