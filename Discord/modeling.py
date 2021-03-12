# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 16:42:48 2021

@author: kneub
"""

from constants import ehb_dict, danger_dict

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



