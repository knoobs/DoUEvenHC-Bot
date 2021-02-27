# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 16:42:48 2021

@author: kneub
"""

from matplotlib import pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import numpy as np
import math

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
        print(eff_ehb)
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
    plt.gca().set_title("Hardcore Clan Rank Plot",color='white')

    if show_plot:
        plt.show()
        
    plt.savefig(fname='rank_plot',transparent=False, bbox_inches='tight',facecolor='#121111')
    plt.close()
        
    return fig



