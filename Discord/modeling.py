# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 16:42:48 2021

@author: kneub
"""

from matplotlib import pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import numpy as np
import math
import os

from PIL import Image, ImageFont, ImageDraw

import json_updater
from constants import *

#Equation modelling
pvm_points_base = np.arange(1,50000)/10

def calc_pvm(pvm_dict):
    
    eff_ehb = 0    
    # Get BASE ehb*danger
    for boss in ehb_dict:
        eff_ehb += 2*danger_dict[boss]*pvm_dict[boss]['value']/ehb_dict[boss]
    
    if eff_ehb > 5000:
        #print(eff_ehb)
        eff_ehb = 5000
    return eff_ehb

def plot_ranks(player,show_plot=True):
    
    data = json_updater.read_json('clan.json')
    fig = plt.figure()
    for name in data.keys():
        player_rank = data[name]['skills']['Overall']['rank']
        player_pvm = calc_pvm(data[name]['pvm'])
        if name == player.lower():
            plt.plot(player_pvm,player_rank,color='yellow',marker='.',markersize=10)
        else:
            plt.plot(player_pvm,player_rank,color='yellow',marker='.',markersize=1)  
        
    # Base Rank Plotting
    for rank in line_dict:
        rank_dict = line_dict[rank]
        
        log_base   = rank_dict['base']
        offset     = rank_dict['offset']
        color_code = rank_dict['color']
        
        pvm_points = np.array([i for i in pvm_points_base if i-offset > 0])
        rank_line = 10**np.array([math.log(i-offset,log_base) for i in pvm_points])
        
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
    plt.xlim((0,5000))
    plt.gca().yaxis.set_major_formatter(StrMethodFormatter('{x:.0f}'))
    plt.xlabel("Pvm Points")
    plt.ylabel("HC Rank")
    plt.gca().set_title("Do U Even HC Rank Plot",color='white')

    if show_plot:
        plt.show()
        
    plt.savefig(fname='rank_plot',transparent=False, bbox_inches='tight',facecolor='#121111')
    plt.close()
        
    return fig

def generate_background(width=0, height=0):
    
    im = Image.open("Images/background.jpg")
    
    if width == 0:
        width = im.width
    if height == 0:
        height = im.height
    
    new_size = (width,height)
    if im.size != new_size:   
        im = im.resize(new_size)
        
    return im
    
def generate_font(size=12):
    
    return ImageFont.truetype("Fonts/runescape_uf.ttf",size)

def plot_point_table(name=''):
    
    # Create starting image
    if name == '':
        height = 1000
    else:
        height = 1050
    image = generate_background(0,height)
    image_edit = ImageDraw.Draw(image)
    
    # Place title on image
    title_font = generate_font(36)
    if name == '':
        title_text = "Kills for 1 Pvm Point"
    else:
        title_text = f"Pvm Points for {name}"
    w, h = image_edit.textsize(title_text, font=title_font)
    image_edit.text((int((image.width-w)/2),12),title_text,(255,255,0),font=title_font)
    
    # Get Player info
    if name != '':
        data = json_updater.read_json('clan.json')
        pvm_dict = data[name.lower()]['pvm']
    
    # Loop through bosses
    boss_table = []
    text_font = generate_font
    x_pos = 75
    y_pos = 50
    for boss in ehb_dict:
        # Calcs
        kc_multiplier = 1
        if name != '':
            kc_multiplier = pvm_dict[boss]['value']
        boss_points = 2*danger_dict[boss]*kc_multiplier/ehb_dict[boss]
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
        text_font = generate_font(20)
        text_boss = boss.replace(':',' -')+":"
        if name == '':
            text_points = str(round(1/boss_points,2))
        else:
            text_points = str(round(boss_points,2))
        image_edit.text((x_pos + 50 ,y_pos + 12),text_boss,  (255,255,0),font=text_font)
        image_edit.text((x_pos + 335,y_pos + 12),text_points,(255,255,0),font=text_font)
        
        # Move Position
        y_pos += 45
        if y_pos > 980:
            y_pos = 50
            x_pos += 390
            
    # Add total if player request
    if name != '':
        footer_text = "Total: "+str(round(calc_pvm(pvm_dict),2))
        w, h = image_edit.textsize(footer_text, font=title_font)
        image_edit.text((int((image.width-w)/2),1012),footer_text,(255,255,0),font=title_font)
        
    image.save("pvm_points.jpg")
        
    return boss_table


