# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 19:48:40 2013

@author: JG
"""

class DataView():
    """
    Holds the current views of the tab
    """
    def __init__(self, maxval):
        self.display_ev = False
        self.xcoordinate = 0
        self.ycoordinate = 0
        self.currentmaxvalcolor = maxval
        self.currentminvalcolor = 0
        self.slider_val = 800