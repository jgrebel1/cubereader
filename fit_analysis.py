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

#this module contains functions used both by the peak_fit reader and spectrum
#holder box. I need to separate these functions into two separate modules


def filter_current_image_from_residuals(min_filter, max_filter,
                                        data, data_view):
    """returns image with 0's in places failing residual calculation"""
    image = get_image_from_data(data, data_view)
    integrated_residuals = data.integrated_residuals
    filtered_image = filter_from_residuals(min_filter, max_filter,
                                           image, integrated_residuals)
    return filtered_image

def filter_from_residuals(min_filter, max_filter, image, image_residuals):
    """returns image with 0's in places failing residual calculation"""
    image_current = np.copy(image)
    (rows, columns) = np.shape(image)
    for row in np.arange(rows):
        for column in np.arange(columns):
            if image_residuals[row, column] > max_filter:
                image_current[row, column] = 0
            elif image_residuals[row, column] < min_filter:
                image_current[row, column] = 0
    return image_current
            
def get_cube_filename(fit_filename):
    """input peak_fit filename, return original data filename"""
    dirname = os.path.dirname(fit_filename)
    basename = os.path.basename(fit_filename)
    cube_basename = basename[11:]
    cube_filename = os.path.join(dirname, cube_basename)
    return cube_filename    

def get_image_from_cube(image_cube, peak_number):
    image = image_cube[:,:,peak_number]
    return image
    
def get_image_from_data(data, data_view):
    peak = data.peaks[data_view.current_peak]
    image = peak[data_view.current_variable]
    return image
    
def get_output_filename(input_filename):
    """
    generate filenames for peak_fit. if filename exists in directory
    increment name
    """
    hdf5_directory = QtGui.QFileDialog.getExistingDirectory()
    basename = analysis.get_file_basename(input_filename)
    file_exists = True
    count = 0
    while file_exists == True:
        basename = analysis.get_file_basename(input_filename)
        full_basename = 'Peak_Fit%02d'%count + '-' + basename
        output_filename = os.path.join(hdf5_directory, full_basename) +'.hdf5'
        try:
            with open(output_filename): pass
            count += 1
        except IOError:
            file_exists = False            
    return output_filename

def get_peak_function(cube_peaks, peak_number):
    """peak function from cube_peaks holder"""
    spectrum = cube_peaks[0]
    peak = spectrum[peak_number]
    peak_function = peak['function']
    return peak_function
    

def get_peak_name(cube_peaks, peak_number):
    """peak name from cube_peaks holder"""
    spectrum = cube_peaks[0]
    peak = spectrum[peak_number]
    peak_name = peak['name']
    return peak_name

def get_peak_penalty_function(cube_peaks, peak_number):
    """peak penalty function from cube_peaks holder"""
    spectrum = cube_peaks[0]
    peak = spectrum[peak_number]
    peak_penalty_function = peak['penalty_function']
    return peak_penalty_function  
    
def get_peak_ranges(cube_peaks, peak_number):
    """peak ranges from cube_peaks holder"""
    spectrum = cube_peaks[0]
    peak = spectrum[peak_number]
    peak_ranges = peak['ranges']
    return peak_ranges
                             
def get_peak_variables(cube_peaks, peak_number):
    """peak variables from cube_peaks holder"""
    spectrum = cube_peaks[0]
    peak = spectrum[peak_number]
    peak_variables = peak['variables']
    return peak_variables
    
def spectrum_from_data(peak_list, fit_data, cube_data_view):
    """
    generate list of peaks from fit data.
    """
    x = cube_data_view.xcoordinate
    y = cube_data_view.ycoordinate
    spectrum = []
    for peak in peak_list:
        peak_holder = fit_data.peaks[peak]
        function = peak_holder.attrs['function']
        name = peak_holder.attrs['name']
        penalty_function = peak_holder.attrs['penalty_function']
        ranges = peak_holder.attrs['ranges']
        variables = peak_holder.attrs['variables']
        values = []
        for variable in variables:
            image = peak_holder[variable]
            value = image[y, x]
            values.append(value)
        values = np.array(values)
        peak_dict = {}
        peak_dict['function'] = function
        peak_dict['name'] = name
        peak_dict['penalty_function'] = penalty_function
        peak_dict['ranges'] = ranges
        peak_dict['values'] = values
        peak_dict['variables'] = variables
        spectrum.append(peak_dict)
    return spectrum
        