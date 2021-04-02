# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 16:42:48 2021

@author: kneub
"""

from constants import ehb_dict, danger_dict, line_dict
import math

def calc_pvm(pvm_dict):
    
    # Returns updated player pvm dictionary with point data
    total_points = 0    
    for boss in ehb_dict:
        boss_points = 2*danger_dict[boss]*pvm_dict[boss]['value']/ehb_dict[boss]
        total_points += boss_points
        pvm_dict[boss].update({ 'points' : boss_points })
    pvm_dict.update({ 'points' : total_points })

    return pvm_dict

def calc_points_per_kill(boss):
    
    # Returns number of points per kill for a given boss
    boss_points = 2*danger_dict[boss]/ehb_dict[boss]
    
    return boss_points

def get_rank(hc_rank,points):
    
    cc_rank = 'potato'
    
    for rank in line_dict:
        offset = line_dict[rank]['offset']
        log_base = line_dict[rank]['base']
        k = line_dict[rank]['k']
        if float(points) <= 0:
            break
        rank_line = 10**(math.log(float(points),log_base))*(float(points)/offset)**k
        
        if int(hc_rank) < rank_line:
            cc_rank = rank
        else:
            break
    
    return cc_rank
    



