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
    def __init__(self, hdf5_filename):
        self.filename = hdf5_filename
        self.xdata = []
        self.ycube = []
        self.ev_xdata = []
        self.ev_ycube = []
        self.xdata_info = {}
        self.hdf5 = self.load_data(self.filename)
        self.title = self.find_title(self.hdf5)
        self.assign_shortcuts(self.hdf5)
        self.check_for_ev_cube(self.hdf5)
    
    def load_data(self, filename):
        hdf5 = h5py.File(filename,'r+')
        return hdf5
        
    def assign_shortcuts(self, hdf5):
        self.ycube = hdf5["Experiments/%s/data"%self.title]       
        try:
            self.xdata = hdf5["Experiments/%s/xdata"%self.title][...]
            self.xdata_info['data_type'] = 'wavelength'
            self.xdata_info['reversed'] = True
            self.header = hdf5['Experiments']['%s'%self.title].attrs['header']
        except:
            self.xdata = analysis.get_xdata(hdf5["Experiments/%s/axis-2"%self.title])
            self.xdata_info['data_type'] = 'ev'
            self.xdata_info['reversed'] = False
            
    def check_for_ev_cube(self, hdf5):
        try:
            self.ev_xdata = hdf5["Experiments/%s/ev_xdata"%self.title][...]
            self.ev_ycube = hdf5["Experiments/%s/ev_data"%self.title]
        except:
            pass
        
    def find_title(self, hdf5):
        g = lambda x: x
        title = str(hdf5['Experiments'].visit(g))
        return title
        

            
class FitData():
    """holds peak_fit data"""
    def __init__(self, hdf5_filename):
        self.peaks = []        
        self.load_data(hdf5_filename)

        
    def load_data(self, hdf5_filename):
        self.hdf5 = h5py.File(hdf5_filename, 'r')   
        self.peaks = self.hdf5['peaks']
        self.integrated_residuals = self.hdf5['integrated_residuals']
