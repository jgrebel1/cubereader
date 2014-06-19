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
    def __init__(self, maxval, dimensions):
        self.maxval = maxval
        self.display_ev = True
        self.xcoordinate = 0
        self.ycoordinate = 0
        self.maxcolor = maxval
        self.mincolor = 0
        self.dimension1 = dimensions[0]
        self.dimension2 = dimensions[1]
        self.number_of_slices = dimensions[2]
        self.slider_val = 1
        self.vmin_wavelength = 300
        self.vmax_wavelength = 800
        
        
class FitDataView():
    """
    Holds the current views of the Fit tab
    """
    def __init__(self):
        self.current_peak = 'Peak0'
        self.current_variable = 'A'
        self.xcoordinate = 0
        self.ycoordinate = 0
        self.maxcolor = 100
        self.mincolor = 0
        self.min_filter = -1
        self.max_filter = 1