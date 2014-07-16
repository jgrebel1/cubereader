# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 17:28:09 2013

@author: JG
"""
import sys
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import h5py

from PySide import QtCore
from PySide import QtGui
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar


#project specific items

import analysis
import fit_analysis

class SpectrumHolder():
    """
    Holds peaks, peak_fit, and generates peak_fit images
    """
    def __init__(self, filename, dimension1, dimension2):
        self.filename = filename
        self.data = {}
        self.dimension1 = dimension1
        self.dimension2 = dimension2
        self.spectrum_box = ''
        self.cube_peaks = []
        self.amplitudes = []
        self.mu = []
        self.sigma = []
        self.m = []
        self.widths = []
        self.cube_residuals = []
        self.cube_fitted = False
        self.cube_fitting = False
        self.cube_mutex = QtCore.QMutex()

    def count_peaks(self, cube_peaks):
        """count peaks in cube_peaks"""
        spectrum = cube_peaks[0]
        peak_count = 0            
        for peak in spectrum:
            peak_count += 1
        return peak_count
    
    def empty_cube_box(self):
        self.cube_fitted = False
        self.cube_peaks = []
        self.cube_residuals = []
        self.amplitudes = []
        self.mu = []
        self.sigma = []
        self.m = []
    
    def empty_spectrum_box(self):
        self.spectrum_box = ''
        
    def generate_amplitudes_picture(self, cube_peaks):  
        for spectrum in cube_peaks:
            for peak in spectrum:
                self.amplitudes.append(peak['values'][0])
        self.amplitudes = np.reshape(self.amplitudes,
                                     (self.dimension1,
                                      self.dimension2,
                                      self.peak_count))
                                      
    def generate_m_picture(self, cube_peaks):
        for spectrum in cube_peaks:
            for peak in spectrum:
                self.m.append(peak['values'][3])
            
        self.m = np.reshape(self.m,
                            (self.dimension1,
                             self.dimension2,
                             self.peak_count))
                                      
    def generate_mu_picture(self, cube_peaks):
        for spectrum in cube_peaks:
            for peak in spectrum:
                self.mu.append(peak['values'][1])
            
        self.mu = np.reshape(self.mu,
                             (self.dimension1,
                              self.dimension2,
                              self.peak_count))
                                     
    def generate_residuals_picture(self):
        self.cube_residuals = np.reshape(self.cube_residuals,
                                         (self.dimension1,
                                          self.dimension2))
    
    def generate_sigma_picture(self, cube_peaks):
        for spectrum in cube_peaks:
            for peak in spectrum:
                self.sigma.append(peak['values'][2])
            
        self.sigma = np.reshape(self.sigma,
                                (self.dimension1,
                                 self.dimension2,
                                 self.peak_count))
    
    def get_image_cube(self, variable):
        """choose image cube based on variable"""
        if variable == 'A':
            image_cube = self.amplitudes
        elif variable == '\\mu':
            image_cube = self.mu
        elif variable == '\\sigma':
            image_cube = self.sigma
        elif variable == 'm':
            image_cube = self.m
        return image_cube

    def notify_cube_fitted(self):
        self.sort_peaks(self.cube_peaks)
        self.peak_count = self.count_peaks(self.cube_peaks)
        self.generate_amplitudes_picture(self.cube_peaks)
        self.generate_mu_picture(self.cube_peaks)
        self.generate_sigma_picture(self.cube_peaks) 
        self.generate_m_picture(self.cube_peaks)
        self.generate_residuals_picture()
        self.cube_fitted = True
        self.cube_fitting = False

    
    def notify_cube_fitting(self):
        self.empty_cube_box()
        self.cube_fitting = True
        
    def save_cube(self):
        if not self.cube_fitted:
            self.cube_warning()
            return
        output_filename = fit_analysis.get_output_filename(self.filename)
        self.save_cube_process(output_filename, self.cube_peaks, self.peak_count)

    def save_cube_process(self, output_filename, cube_peaks, peak_count):
        """
        Saves the cube_fit as an hdf5 file
        """           

            
        output_file = h5py.File(output_filename,'w')
        output_file.attrs['peak_count'] = peak_count
        peaks = output_file.create_group("peaks")
        for peak in np.arange(peak_count):
            peak_holder = peaks.create_group("Peak%d"%peak)
            
            peak_function = fit_analysis.get_peak_function(cube_peaks, peak)
            peak_name = fit_analysis.get_peak_name(cube_peaks, peak)
            peak_penalty_function = fit_analysis.get_peak_penalty_function(cube_peaks,peak)
            peak_ranges = fit_analysis.get_peak_ranges(cube_peaks, peak)
            peak_variables = fit_analysis.get_peak_variables(cube_peaks, peak)
            peak_holder.attrs['function'] = peak_function
            peak_holder.attrs['name'] = peak_name
            peak_holder.attrs['penalty_function'] = peak_penalty_function
            peak_holder.attrs['ranges'] = peak_ranges
            peak_holder.attrs['variables'] = peak_variables
            
            for variable in peak_variables:
                image_cube = self.get_image_cube(variable)
                image = fit_analysis.get_image_from_cube(image_cube, peak)
                peak_holder.create_dataset(variable, data=image)
                
        output_file.create_dataset("integrated_residuals",
                                    data=self.cube_residuals)
        output_file.close()
        
    def sort_peaks(self, cube_peaks):
        """
        sorts peaks in spectra by energy or wavelength
        """
        for spectrum in cube_peaks:
            spectrum.sort(key=lambda x: x['values'][1])
                
    def stop_fit(self):
        self.cube_fitted = False
        self.cube_fitting = False


