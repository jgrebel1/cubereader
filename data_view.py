# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 19:48:40 2013

@author: JG
"""

class DataView():
    """
    Holds the current views of the tab
    """
    def __init__(self, maxval, number_of_slices):
        self.display_ev = False
        self.xcoordinate = 0
        self.ycoordinate = 0
        self.currentmaxvalcolor = maxval
        self.currentminvalcolor = 0
        self.slider_val = 1
        self.visualization_min_color = 0
        self.visualization_max_color = maxval
        self.visualization_min_slice = 0
        self.visualization_max_slice = number_of_slices - 1
        self.reversed_data = False