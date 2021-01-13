# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 00:10:14 2021

@author: kneub
"""

from lxml import html
import requests
from bs4 import BeautifulSoup
import xlwt
from xlwt import Workbook
import time
import math
import random
        

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
URL_short = "https://secure.runescape.com/m=hiscore_oldschool_ironman/hiscorepersonal?user1="
headers = { "user-agent" : USER_AGENT }

skill_list = ['Overall','Attack','Defence','Strength','Hitpoints','Ranged','Prayer','Magic','Cooking',
              'Woodcutting','Fletching','Fishing','Firemaking','Crafting','Smithing',
              'Mining','Herblore','Agility','Thieving','Slayer','Farming','Runecraft',
              'Hunter','Construction']

pvm_list = ['Bounty Hunter - Hunter','Clue Scrolls (all)','Clue Scrolls (beginner)',
            'Clue Scrolls (easy)','Clue Scrolls (medium)','Clue Scrolls (hard)',
            'Clue Scrolls (elite)','Clue Scrolls (master)','LMS - Rank','Soul Wars Zeal',
            'Abyssal Sire','Alchemical Hydra','Barrows Chests','Byrophyta','Callisto',
            'Cerberus','Chambers of Xeric','Chambers of Xeric: Challenge Mode',
            'Chaos Elemental','Chaos Fanatic','Commander Zilyana','Corporeal Beast',
            'Crazy Archaeologist','Dagannoth Prime','Dagannoth Rex','Dagannoth Supreme',
            'Deranged Archaeologist','General Graardor','Giant Mole','Grotesque Guardians',
            'Hespori','Kalphite Queen','King Black Dragon','Kraken',"Kree'Arra",
            "K'ril Tsutsaroth",'Mimic','Nightmare','Obor','Sarachnis','Scorpia','Skotizo',
            'The Gauntlet','The Corrupted Gauntlet','Theatre of Blood','Thermonuclear Smoke Devil',
            'TzTok-Jad','TzKal-Zuk','Venenatis',"Vet'ion",'Vorkath','Wintertodt','Zalcano','Zulrah']

def read_hiscores(name, hardcore=False):
    # Read the ironman hiscores for the name above
    if hardcore:
        URL_short = "https://secure.runescape.com/m=hiscore_oldschool_hardcore_ironman/hiscorepersonal?user1="
    else:
        URL_short = "https://secure.runescape.com/m=hiscore_oldschool_ironman/hiscorepersonal?user1="
    
    URL = URL_short + name.replace(" ", "%A0")
    page = requests.get(URL, headers=headers)

    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
    else:
        raise NameError("Unable to load webpage")
        
    return soup

def format_hiscores_text(text):
    # Format text output
    text = [i for i in text.split('\n') if i != '']
    
    # Check if player exists
    fail_string = 'No player'
    if fail_string in text:
        return 'FAIL'
    
    # Create nice dictionaries
    skills_dict = {}
    for skill in skill_list:
        skills_dict.update({skill : {}})
        index = [i for i in range(len(text)) if skill in text[i]]
        if len(index) == 0:
            skills_dict[skill].update({ 'rank'  : 0 })
            skills_dict[skill].update({ 'level' : 0 })
            skills_dict[skill].update({ 'xp'    : 0 })
        else:
            skills_dict[skill].update({ 'rank'  : convert_to_int(text[index[0]+1]) })
            skills_dict[skill].update({ 'level' : convert_to_int(text[index[0]+2]) })
            skills_dict[skill].update({ 'xp'    : convert_to_int(text[index[0]+3]) })
            
    pvm_dict = {}
    for boss in pvm_list:
        pvm_dict.update({boss : {}})
        index = [i for i in range(len(text)) if boss in text[i]]
        if len(index) == 0:
            pvm_dict[boss].update({ 'rank'  : 0 })
            pvm_dict[boss].update({ 'value' : 0 })
        else:
            pvm_dict[boss].update({ 'rank'  : convert_to_int(text[index[0]+1]) })
            pvm_dict[boss].update({ 'value' : convert_to_int(text[index[0]+2]) })
            
    player_dict = { "skills" : skills_dict, "pvm" : pvm_dict }
    
    return player_dict

def convert_to_int(num):
    return int(num.replace(",",""))




