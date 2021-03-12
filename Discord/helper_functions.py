# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 10:47:39 2021

@author: kneub
"""
from PIL import Image, ImageFont

from constants import pvm_list, pvm_short_dict, skill_list, skill_short_dict

def find_boss(name):
    
    # Check case sensitivity of keys
    for boss in pvm_list:
        if name.lower() == boss.lower():
            return boss
        
    # Check shorthands
    for boss in pvm_short_dict:
        if name.lower() in pvm_short_dict[boss]:
            return boss
        
    # Return Default
    return 'poop'

def find_skill(name):
    
    # Check case sensitivity of keys
    for skill in skill_list:
        if name.lower() == skill.lower():
            return skill
        
    # Check shorthands
    for skill in skill_short_dict:
        if name.lower() in skill_short_dict[skill]:
            return skill
        
    # Return Default
    return 'poop'

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