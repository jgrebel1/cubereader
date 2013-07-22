# -*- coding: utf-8 -*-
"""
Created on Mon Jul 01 13:57:51 2013

@author: JG
"""
import os
import numpy as np
from scipy import interpolate


def find_maxval(dataset):
    maxval = 0
    for i in dataset:
        if np.amax(i) > maxval:
            maxval = np.amax(i)
    return maxval
    
def get_file_basename(path_name):
    filename, extension = os.path.splitext(path_name)
    basename = os.path.basename(filename)
    return basename

def wavelength_to_slice(wavelength, xdata):
    """
    converts an input wavelength into the nearest xdata index using interpolation
    """
    xdata = np.array(xdata[...])
    f = interpolate.interp1d(xdata[::-1], np.arange(1600)) 
    if wavelength > xdata[0]:
        imageval = 1599
    elif wavelength < xdata[-1]:
        imageval = 0
    else:
        for number in np.arange(1600):
            if number > f(wavelength):
                imageval = number
                break    
    return imageval
    
def ev_to_slice(ev, xdata):
    """
    converts an input ev into the nearest xdata index using interpolation
    """
    if ev == 0:
        imageval = 0
    else:
        wavelength = 1240/ev
    xdata = np.array(xdata[...])
    f = interpolate.interp1d(xdata[::-1], np.arange(1600)) 
    if wavelength > xdata[0]:
        imageval = 1599
    elif wavelength < xdata[-1]:
        imageval = 0
    else:
        for number in np.arange(1600):
            if number > f(wavelength):
                imageval = number
                break    
    return imageval