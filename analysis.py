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
    
def get_dimensions(ycube):
    (rows, columns, slices) = np.shape(ycube[...])
    return (rows, columns, slices)
def ev_to_slice(ev, data):
    """
    converts an input ev into the nearest xdata index using interpolation
    """    
    length, = np.shape(data.xdata)
    if ev == 0:
        ev = 0.000001
    if data.xdata_info['wavelength_ordered']:
        value = 1240/ev
        ordered_xdata = data.xdata
    else:
        value = ev
        ordered_xdata = 1240/data.xdata
    if data.xdata_info['reversed']:
        maxdata = data.xdata[0]
        mindata = data.xdata[-1]
        ordered_xdata = ordered_xdata[::-1]
    else:
        maxdata = data.xdata[-1]
        mindata = data.xdata[0]
        ordered_xdata = ordered_xdata
    f = interpolate.interp1d(ordered_xdata, np.arange(length)) 
    if value > maxdata:
        imageval = length - 1
    elif value < mindata:
        imageval = 0
    else:
        for number in np.arange(length):
            if number > f(value):
                imageval = number
                break
    if not data.xdata_info['reversed']:
        imageval = length -1 - imageval
  
    return imageval
    
def wavelength_to_slice(wavelength, data):
    """
    converts an input wavelength into the nearest xdata index using interpolation
    """
    ev = 1240/wavelength
    ev_to_slice(ev, data)
    
def get_xdata(hdf5_axis):
    scale = hdf5_axis.attrs['scale']
    offset = hdf5_axis.attrs['offset']
    size = hdf5_axis.attrs['size']
    point = offset
    xdata = []
    for points in np.arange(size):
        xdata.append(offset)
        offset += scale
    xdata = np.array(xdata)
    return xdata
    
