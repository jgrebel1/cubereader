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
def ev_to_slice(ev, xdata):
    """
    converts an input ev into the nearest xdata index using interpolation
    """
    maxdata = xdata[0]
    mindata = xdata[-1]      
    length, = np.shape(xdata)
    if ev == 0:
        print 'test1'
        imageval = 0
    else:
        wavelength = 1240/ev
        print 'test2'
    xdata = np.array(xdata)
    f = interpolate.interp1d(xdata[::-1], np.arange(length)) 
    for number in np.arange(length):
        print xdata[number]
    if wavelength > maxdata:
        print 'test3'
        print 'maxdata is', maxdata
        print 'wavelength is', wavelength
        imageval = length - 1
    elif wavelength < mindata:
        print 'test4'
        print 'mindata is', mindata
        print 'wavelength is', wavelength
        imageval = 0
    else:
        print 'test5'
        for number in np.arange(length):
            if number > f(wavelength):
                imageval = number
                break    
    return imageval
    
def wavelength_to_slice(wavelength, xdata):
    """
    converts an input wavelength into the nearest xdata index using interpolation
    """
    maxdata = xdata[0]
    mindata = xdata[-1] 
    length, = np.shape(xdata)
    xdata = np.array(xdata)
    f = interpolate.interp1d(xdata[::-1], np.arange(length)) 
    if wavelength > maxdata:
        imageval = length-1
    elif wavelength < mindata:
        imageval = 0
    else:
        for number in np.arange(length):
            if number > f(wavelength):
                imageval = number
                break    
    return imageval
    
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
    
