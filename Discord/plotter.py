# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 01:57:44 2021

@author: kneub
"""

from matplotlib import pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import numpy as np
import math
import os

from PIL import Image, ImageDraw

import json_updater
import modeling
import helper_functions as hf
from constants import skill_list, line_dict, pvm_points_base, ehb_dict, danger_dict, odd_pvm_list

def plot_xp(player_name,skill="Overall",gamemode='hardcore'):
    
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
        xp = np.append(xp,data[name][gamemode]['skills'][skill]['xp'])
        if name == player:
            xp_player = data[name][gamemode]['skills'][skill]['xp']

    return_string += player_name+" "+skill+" xp:\t "+format(xp_player,",")+"\n"
    return_string += "Clan average "+skill+" xp:\t "+format(int(round(np.mean(xp))),",")+"\n"
    return_string += "Clan median "+skill+" xp:\t "+format(int(round(np.median(xp))),",")
    return return_string

def plot_ranks(player,show_plot=True,zoom='none',gamemode='hardcore'):
    
    data = json_updater.read_json('clan.json')
    fig = plt.figure()
    cc_rank = ''
    for name in data.keys():
        player_rank = data[name][gamemode]['skills']['Overall']['rank']
        player_pvm = data[name][gamemode]['pvm']['points']
        if player_pvm > 5000:
            player_pvm = 5000
        if name == player.lower():
            plt.plot(player_pvm,player_rank,color='magenta',marker='.',markersize=10)
            cc_rank = modeling.get_rank(player_rank,player_pvm)
        else:
            plt.plot(player_pvm,player_rank,color='yellow',marker='.',markersize=1)  
        
    # Base Rank Plotting
    for rank in line_dict:
        rank_dict = line_dict[rank]
        
        log_base   = rank_dict['base']
        offset     = rank_dict['offset']
        k          = rank_dict['k']
        color_code = rank_dict['color']
        
        pvm_points = np.array([i for i in pvm_points_base if i > 0])
        rank_line = 10**np.array([math.log(i,log_base) for i in pvm_points])*(pvm_points/offset)**k
        
        plt.plot(pvm_points,rank_line,color_code)
    
    # Coloring
    #plt.style.use('dark_background')
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
    
    # Styling  
    plt.yscale("log")
    plt.gca().invert_yaxis()
    plt.yticks([100000,10000,1000,100,10,1])
    plt.ylim((100000,1))
    if zoom.isdigit():
        plt.xlim((0,int(5000/2**int(zoom))))
    else:
        plt.xlim((0,5000))
    plt.gca().yaxis.set_major_formatter(StrMethodFormatter('{x:.0f}'))
    plt.xlabel("Pvm Points")
    plt.ylabel("HC Rank")
    plt.gca().set_title("Do U Even HC Rank Plot",color='white')

    if show_plot:
        plt.show()
        
    plt.savefig(fname='rank_plot',transparent=False, bbox_inches='tight',facecolor='#121111')
    plt.close()
    
    # Put player info on image
    image = Image.open('rank_plot.png')
    image_edit = ImageDraw.Draw(image)
    player_font = hf.generate_font(20)
    cc_rank = cc_rank.title()
    player_text = player+': '+cc_rank
    w, h = image_edit.textsize(player_text, font=player_font)
    image_edit.text((image.width-w-45,image.height-60),player_text,(255,255,0),font=player_font)
    
    rank_image = Image.open(f'Images/{cc_rank}.png')
    rank_image = rank_image.resize((20,20))
    rank_image = rank_image.convert("RGBA")
    image.paste(rank_image,(image.width-40,image.height-60),mask=rank_image)
    
    image.save('rank_plot.png')
    
        
    return fig

def plot_point_table(name='',gamemode='hardcore'):
    
    # Create starting image
    if name == '':
        height = 1000
    else:
        height = 1050
    image = hf.generate_background(0,height)
    image_edit = ImageDraw.Draw(image)
    
    # Place title on image
    title_font = hf.generate_font(36)
    if name == '':
        title_text = "Kills for 1 Pvm Point"
    else:
        title_text = f"Pvm Points for {name}"
    w, h = image_edit.textsize(title_text, font=title_font)
    image_edit.text((int((image.width-w)/2),12),title_text,(255,255,0),font=title_font)
    
    # Get Player info
    status = True
    if name != '':
        data = json_updater.read_json('clan.json')
        pvm_dict = data[name.lower()][gamemode]['pvm']
        status = data[name.lower()]['status']
    
    # Loop through bosses
    boss_table = []
    x_pos = 75
    y_pos = 50
    for boss in ehb_dict:
        # Calcs
        if name != '':
            boss_points = pvm_dict[boss]['points']
        else:
            boss_points = modeling.calc_points_per_kill(boss)
        boss_table.append((boss,boss_points))
        
        # Image Pasting
        boss_name = boss.replace(':','')
        boss_name = boss_name.replace(' ','_')
        if os.path.exists(f"Images/{boss_name}.png"):
            boss_image = Image.open(f"Images/{boss_name}.png")
            boss_image = boss_image.resize((40,40))
            image.paste(boss_image, (x_pos, y_pos), mask = boss_image)
        else:
            boss_image = Image.open("Images/blank.png")
            boss_image = boss_image.resize((40,40))
            image.paste(boss_image, (x_pos, y_pos))  
        
        
        # Text Pasting
        text_font = hf.generate_font(20)
        text_boss = boss.replace(':',' -')+":"
        text_color = (255,255,0)
        if name == '':
            text_points = str(round(1/boss_points,2))
        else:
            if boss_points == 0:
                text_points = "--"
                text_color = (255,255,255)
            else:
                text_points = str(round(boss_points,2))
        image_edit.text((x_pos + 50 ,y_pos + 12),text_boss,  (255,255,0),font=text_font)
        image_edit.text((x_pos + 335,y_pos + 12),text_points,text_color,font=text_font)
        
        # Move Position
        y_pos += 45
        if y_pos > 980:
            y_pos = 50
            x_pos += 390
            
    # Add total if player request
    if name != '':
        total_points = pvm_dict['points']
        footer_text = "Total: "+str(round(total_points,2))
        w, h = image_edit.textsize(footer_text, font=title_font)
        image_edit.text((int((image.width-w)/2),1012),footer_text,(255,255,0),font=title_font)
        
        if not status:
            death_image = Image.open("Images/hcim_skull.png")
            death_image = death_image.resize((30,30))
            death_image = death_image.convert('RGBA')
            image.paste(death_image, (int((image.width+w)/2)+10,1012), mask = death_image)  
        
    image.save("pvm_points.jpg")
        
    return boss_table

def plot_top_boss(boss,num=10,mode='value',gamemode='hardcore'):
    
    # Load Data
    data = json_updater.read_json('clan.json')
    
    # Edge Case: num cannot exceed number of players
    if num > len(data):
        num = len(data)
       
    # Get player data for boss
    name_list = np.array([])
    kc_list = np.array([])
    status_list = np.array([])
    for name in data:
        kc_list = np.append(kc_list,data[name][gamemode]['pvm'][boss][mode])
        name_list = np.append(name_list, name)
        status_list = np.append(status_list, data[name]['status'])
        
    # If in rank modem remove "0" ranks
    if mode == 'rank':
        zero_logical = kc_list == 0
        name_list = name_list[~zero_logical]
        kc_list = kc_list[~zero_logical]
        status_list = status_list[~zero_logical]
    
    # Sort player data for boss
    top_list = []
    while num > 0:
        # If in rank mode, sort in reverse
        if mode == 'rank':
            index_logical = kc_list == np.min(kc_list)
        else:
            index_logical = kc_list == np.max(kc_list)
        names = name_list[index_logical]
        kcs = kc_list[index_logical]
        statuses = status_list[index_logical]
        
        tie_count = len(names)
        num -= tie_count
        
        for i in range(tie_count):
            if int(kcs[i]) == 0:
                break
            top_list.append((names[i],int(kcs[i]),statuses[i]))
        
        # Remove already sorted names
        name_list = name_list[~index_logical]
        kc_list = kc_list[~index_logical]
        status_list = status_list[~index_logical]
        
    # Generate Image
    user_pixels = 40
    num = len(top_list)
    height = num*user_pixels+150
    if mode == 'rank':
        height += 45
    image = hf.generate_background(0,height)
    image = image.convert('RGBA')
        
    # Place overlay image
    boss_name = boss.replace(':','')
    boss_name = boss_name.replace(' ','_')
    if os.path.exists(f"Images/{boss_name}.png"):
        boss_image = Image.open(f"Images/{boss_name}.png")
        boss_image = boss_image.resize(image.size)
        if boss_image.mode != "RGBA":
            boss_image = boss_image.convert("RGBA")
        image = Image.blend(image, boss_image, alpha=0.3)
    
    # Create edittable
    image_edit = ImageDraw.Draw(image)
    
    # Place title on image
    font_size = 60
    title_font = hf.generate_font(font_size)
    title_text = "Top "+str(num)+" Clan HC "+boss
    if boss not in odd_pvm_list:
        title_text += " Killers"
    w, h = image_edit.textsize(title_text, font=title_font)
    while w > image.width:
        font_size -= 1
        title_font = hf.generate_font(font_size)
        w, h = image_edit.textsize(title_text, font=title_font)
    image_edit.text((int((image.width-w)/2),12),title_text,(255,255,0),font=title_font)
    if mode == 'rank':
        mode_font = hf.generate_font(40)
        w, h = image_edit.textsize("(HC Hiscores Rank)", font=mode_font)
        image_edit.text((int((image.width-w)/2),12+60),"(HC Hiscores Rank)",(255,255,0),font=mode_font)
    
    # Place names on image
    y_pos = 100
    if mode == 'rank':
        y_pos += 45
    x_pos = 250
    for i in range(num):
        
        place = str(i+1)+". "
        name = top_list[i][0]
        kc = str(top_list[i][1])
        status = top_list[i][2]
        
        # Text Pasting
        text_font = hf.generate_font(35)
        image_edit.text((x_pos,y_pos),place+name,(255,255,0),font=text_font)
        image_edit.text((x_pos + 350,y_pos),kc,(255,255,0),font=text_font)
        
        # Place death symbol
        if not status:
            w, h = image_edit.textsize(place+name, font=text_font)
            death_image = Image.open("Images/hcim_skull.png")
            death_image = death_image.resize((25,25))
            death_image = death_image.convert('RGBA')
            image.paste(death_image, (x_pos+w+5,y_pos+5), mask = death_image) 
        
        # Move Position
        y_pos += user_pixels
        
    # Save image
    image.save("top_boss.png")
    
    return top_list
