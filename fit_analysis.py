# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 18:08:16 2013

@author: JG
"""
import os
from PySide import QtGui
from PySide import QtCore
import numpy as np

#project specific items

import analysis

def filter_current_image_from_residuals(min_filter, max_filter,
                                        data, data_view):
    image = get_image_from_data(data, data_view)
    integrated_residuals = data.integrated_residuals
    filtered_image = filter_from_residuals(min_filter, max_filter,
                                           image, integrated_residuals)
    return filtered_image

def filter_from_residuals(min_filter, max_filter, image, image_residuals):
    image_current = np.copy(image)
    (rows, columns) = np.shape(image)
    for row in np.arange(rows):
        for column in np.arange(columns):
            if image_residuals[row, column] > max_filter:
                image_current[row, column] = 0
            elif image_residuals[row, column] < min_filter:
                image_current[row, column] = 0
    return image_current
            
    

def get_image_from_cube(image_cube, peak_number):
    image = image_cube[:,:,peak_number]
    return image
    
def get_image_from_data(data, data_view):
    peak = data.peaks[data_view.current_peak]
    image = peak[data_view.current_variable]
    return image
    
def get_output_filename(input_filename):
    hdf5_directory = QtGui.QFileDialog.getExistingDirectory()
    basename = analysis.get_file_basename(input_filename)
    full_basename = 'Peak_Fit-' + basename
    output_filename = os.path.join(hdf5_directory, full_basename) +'.hdf5'
    return output_filename

def get_peak_function(cube_peaks, peak_number):
    spectrum = cube_peaks[0]
    peak = spectrum[peak_number]
    peak_function = peak['function']
    return peak_function
    

def get_peak_name(cube_peaks, peak_number):
    spectrum = cube_peaks[0]
    peak = spectrum[peak_number]
    peak_name = peak['name']
    return peak_name

def get_peak_penalty_function(cube_peaks, peak_number):
    spectrum = cube_peaks[0]
    peak = spectrum[peak_number]
    peak_penalty_function = peak['penalty_function']
    return peak_penalty_function  
    
def get_peak_ranges(cube_peaks, peak_number):
    spectrum = cube_peaks[0]
    peak = spectrum[peak_number]
    peak_ranges = peak['ranges']
    return peak_ranges
                             
def get_peak_variables(cube_peaks, peak_number):
    spectrum = cube_peaks[0]
    peak = spectrum[peak_number]
    peak_variables = peak['variables']
    return peak_variables