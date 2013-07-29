# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 10:56:25 2013

@author: JG
"""

import h5py
import numpy as np
import analysis
    
class Data():
    
    def __init__(self, hdf5_file):
        self.xdata = []
        self.ycube = []
        self.xdata_info = {}
        self.load_data(hdf5_file)        
    
    def load_data(self, hdf5_file):
        self.hdf5 = h5py.File(hdf5_file,'r')
        self.ycube = self.hdf5["Experiments/__unnamed__/data"]       
        try:
            self.xdata = self.hdf5["Experiments/__unnamed__/xdata"][...]
            self.xdata_info['wavelength_ordered'] = True
            self.xdata_info['reversed'] = True
        except:
            self.xdata = np.array(1240/analysis.get_xdata(self.hdf5["Experiments/__unnamed__/axis-2"]))
            self.xdata_info['wavelength_ordered'] = False
            self.xdata_info['reversed'] = False
