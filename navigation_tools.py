# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 12:45:36 2013

@author: JG
"""
import numpy as np

def move_down(data_view, dimension1):
    if not data_view.ycoordinate == dimension1 - 1:
        data_view.ycoordinate = data_view.ycoordinate+1
    

def move_left(data_view):
    if not data_view.xcoordinate == 0:
        data_view.xcoordinate = data_view.xcoordinate-1


def move_right(data_view, dimension2):
    if not data_view.xcoordinate == dimension2 - 1:
        data_view.xcoordinate = data_view.xcoordinate+1
  
def move_up(data_view):
    if not data_view.ycoordinate == 0:
        data_view.ycoordinate = data_view.ycoordinate-1
  
def change_coordinates(event, data_view):      
    data_view.xcoordinate = np.floor(event.xdata + .5)
    data_view.ycoordinate = np.floor(event.ydata + .5)
