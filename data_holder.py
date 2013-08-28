# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 10:56:25 2013

@author: JG
"""

import h5py
import numpy as np
import analysis
    
class Data():
    """holds cube data"""
    def __init__(self, hdf5_file):
        self.xdata = []
        self.ycube = []
        self.ev_xdata = []
        self.ev_ycube = []
        self.xdata_info = {}
        self.hdf5 = self.load_data(hdf5_file)
        self.assign_shortcuts(self.hdf5)
        self.check_for_ev_cube(self.hdf5)
    
    def load_data(self, hdf5_file):
        hdf5 = h5py.File(hdf5_file,'r+')
        return hdf5
        
    def assign_shortcuts(self, hdf5):
        self.ycube = hdf5["Experiments/__unnamed__/data"]       
        try:
            self.xdata = hdf5["Experiments/__unnamed__/xdata"][...]
            self.xdata_info['data_type'] = 'wavelength'
            self.xdata_info['reversed'] = True
            self.header = hdf5['Experiments']['__unnamed__'].attrs['header']
        except:
            self.xdata = analysis.get_xdata(hdf5["Experiments/__unnamed__/axis-2"])
            self.xdata_info['data_type'] = 'ev'
            self.xdata_info['reversed'] = False
            
    def check_for_ev_cube(self, hdf5):
        try:
            self.ev_xdata = hdf5["Experiments/__unnamed__/ev_xdata"][...]
            self.ev_ycube = hdf5["Experiments/__unnamed__/ev_data"]
        except:
            pass
            
class FitData():
    """holds peak_fit data"""
    def __init__(self, hdf5_file):
        self.peaks = []        
        self.load_data(hdf5_file)

        
    def load_data(self, hdf5_file):
        self.hdf5 = h5py.File(hdf5_file, 'r')   
        self.peaks = self.hdf5['peaks']
        self.integrated_residuals = self.hdf5['integrated_residuals']
