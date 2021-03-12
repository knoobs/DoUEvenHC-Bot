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
    # Get HC Data
    player_hiscores = read_hiscores.read_hiscores(name)
    player_dict_hc = read_hiscores.format_hiscores_text(player_hiscores.text)
    if player_dict_hc == "FAIL":
        return "Player update of '"+name+"' NOT successful"
    
    #Get Iron data
    player_hiscores = read_hiscores.read_hiscores(name,False)
    player_dict_iron = read_hiscores.format_hiscores_text(player_hiscores.text)
    if player_dict_iron == "FAIL":
        return "Player update of '"+name+"' NOT successful"
    
    status = True
    xp_hc = player_dict_hc['skills']['Overall']['xp']
    xp_iron = player_dict_iron['skills']['Overall']['xp']
    if xp_hc != xp_iron:
        status = False
    player_dict = {
            'hardcore' : player_dict_hc,
            'ironman'  : player_dict_iron,
            'status'   : status
            }
    
    clan_data[name] = player_dict
    
    # Write new data
    with open(filename, "w") as write_file:
        json.dump(clan_data, write_file)
    
    return "Player update of '"+name+"' successful"

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
        return_string = name+" removed successfully"
    else:
        return_string = name+" not found in clan database"
    
    return return_string

def mass_update(textfile):
    
    # Read textfile
    with open(textfile, "r") as read_file:
        for line in read_file:
            name = line.split('\n')[0]
            if name != '':
                return_string = update_player(name)
                print(return_string)
                
    return

def update_all():
    
    data = read_json('clan.json')
    return_string = ""
    for name in data.keys():
        output = update_player(name)
        print(output)
        if "NOT successful" in output:
            return_string += output + "...\n"
            return_string += "\tRemoving "+name+" from clan database...\n"
            remove_output = remove_player(name)
            if "successfully" not in remove_output:
                return_string += "\tRemove unsuccessful." 
                return_string += " Crazy you got here tbh, this is an odd edge case. Gz I guess?"
        
    if return_string == "":
        return "All player updated successfully"
    else:
        return return_string
    

