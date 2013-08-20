# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 19:48:40 2013

@author: JG
"""
import analysis

class DataView():
    """
    Holds the current views of the tab
    """
    def __init__(self, maxval, number_of_slices):
        self.maxval = maxval
        self.display_ev = True
        self.xcoordinate = 0
        self.ycoordinate = 0
        self.maxcolor = maxval
        self.mincolor = 0
        self.slider_val = 1
        self.vmin_slice = 0
        self.vmax_slice = number_of_slices - 1
        
class FitDataView():
    """
    Holds the current views of the Fit tab
    """
    def __init__(self):
        self.current_peak = 'Peak0'
        self.current_variable = 'A'
        self.maxcolor = 100
        self.mincolor = 0