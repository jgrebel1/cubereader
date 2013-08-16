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
    
def ev_to_index(ev, data):
    if data.xdata_info['reversed']:
        ordered_xdata = data.xdata[::-1]
    else:
        ordered_xdata = data.xdata
    if data.xdata_info['data_type'] == 'ev':
        value = ev
    elif data.xdata_info['data_type'] == 'wavelength':
        value = 1240/ev
    index = index_from_ordered_list(value, ordered_xdata)
    if data.xdata_info['reversed']:
        length, = np.shape(data.xdata)
        index = length -1 - index
    return index
    
def index_from_ordered_list(value, ordered_list):
    """
    input an ordered list.
    returns the index of the number closest to value
    """
    maxdata = ordered_list[-1]
    mindata = ordered_list[0]
    length, = np.shape(ordered_list)
    f = interpolate.interp1d(ordered_list, np.arange(length)) 
    if value > maxdata:
        index = length - 1
    elif value < mindata:
        index = 0
    else:
        for number in np.arange(length):
            if number > f(value):
                index = number
                break
    return index
    
def wavelength_to_index(wavelength, data):
    """
    converts an input wavelength into the nearest xdata index using interpolation
    """
    if wavelength == 0:
        wavelength = .000001
    ev = 1240/wavelength
    index = ev_to_index(ev, data)
    return index
    
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
    
def xdata_calc(data, data_view):
    """
    returns xdata based on data type and current display mode
    """
    if data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        xdata = data.xdata
    elif data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        xdata = 1240/data.xdata
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        xdata = 1240/data.xdata
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        xdata = data.xdata
    return xdata
    
def xdata_calc2(input_xdata, dtype, display_ev):
    if display_ev and dtype == 'ev':
        xdata = input_xdata
    elif display_ev and dtype == 'wavelength':
        xdata = 1240/input_xdata
    elif not display_ev and dtype == 'ev':
        xdata = 1240/input_xdata
    elif not display_ev and dtype == 'wavelength':
        xdata = input_xdata
    return xdata
    
def ydata_calc(data, data_view):
    """
    returns ydata based on data type and current display mode.
    """    
    if data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        ydata = data.ycube[data_view.ycoordinate, data_view.xcoordinate,:]        
    elif data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        wavelength_data = data.ycube[data_view.ycoordinate, data_view.xcoordinate,:]
        ydata = []
        for index, lambda_photon_count in enumerate(wavelength_data):
            ev_photon_count = (lambda_photon_count)*(data.xdata[index]**2/1240)
            ydata.append(ev_photon_count)
        ydata = np.array(ydata)
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        ev_data = data.ycube[data_view.ycoordinate, data_view.xcoordinate,:]
        ydata = []
        for index,ev_photon_count in enumerate(ev_data):
            wavelength_photon_count = (ev_photon_count)*(1240/data.xdata[index])
            ydata.append(wavelength_photon_count)
        ydata = np.array(ydata)
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        ydata = data.ycube[data_view.ycoordinate, data_view.xcoordinate,:]        
    return ydata
    
def ydata_calc2(input_ydata, input_xdata, dtype, display_ev):
    """
    returns ydata based on data type and current display mode from input.
    """
    if display_ev and dtype == 'ev':
        ydata = input_ydata       
    elif display_ev and dtype == 'wavelength':
        wavelength_data = input_ydata
        ydata = []
        for index, lambda_photon_count in enumerate(wavelength_data):
            ev_photon_count = (lambda_photon_count)*(input_xdata[index]**2/1240)
            ydata.append(ev_photon_count)
        ydata = np.array(ydata)
    elif not display_ev and dtype == 'ev':
        ev_data = input_ydata
        ydata = []
        for index,ev_photon_count in enumerate(ev_data):
            wavelength_photon_count = (ev_photon_count)*(input_xdata[index])
            ydata.append(wavelength_photon_count)
        ydata = np.array(ydata)
    elif not display_ev and dtype == 'wavelength':
        ydata = input_ydata        
    return ydata

def yimage_calc(data, data_view):
    slice1 = data_view.slider_val
    
    if data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        yimage = data.ycube[:,:,slice1]
    elif data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        yimage = (data.ycube[:,:,slice1])*(data.xdata[slice1]**2/1240)
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'ev':   
        yimage = (data.ycube[:,:,slice1])*(data.xdata[slice1])
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        yimage = data.ycube[:,:,slice1]
    
    return yimage
    
def colors_calc(data, data_view):
    """
    returns min and max colors for display based on data type
    and current display mode.
    
    scale_factor so data scales correctly for both wavelength and ev.
    600 is arbitrary   
    """
    scale_factor = 600
    if data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        max_color = data_view.currentmaxvalcolor
        min_color = data_view.currentminvalcolor
    elif data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        max_color = data_view.currentmaxvalcolor*scale_factor
        min_color = data_view.currentminvalcolor*scale_factor
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'ev':   
        max_color = data_view.currentmaxvalcolor/scale_factor
        min_color = data_view.currentminvalcolor/scale_factor
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        max_color = data_view.currentmaxvalcolor
        min_color = data_view.currentminvalcolor

    return max_color, min_color
    
def colors_calc_max(input_max_color, data, data_view):   
    """
    returns max color for display based on data type
    and current display mode from user input values.
    
    scale_factor so data scales correctly for both wavelength and ev.
    600 is arbitrary   
    """
    scale_factor = 600
    if data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        max_color = input_max_color
    elif data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        max_color = input_max_color*scale_factor
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'ev':   
        max_color = input_max_color/scale_factor
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        max_color = input_max_color

    return max_color
    
def colors_calc_min(input_min_color,data, data_view):   
    """
    returns min and color for display based on data type
    and current display mode from user input values.
    
    scale_factor so data scales correctly for both wavelength and ev.
    600 is arbitrary   
    """
    scale_factor = 600
    if data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        min_color = input_min_color
    elif data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        min_color = input_min_color*scale_factor
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'ev':   
        min_color = input_min_color/scale_factor
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        min_color = input_min_color

    return min_color


def maxval_calc(data, data_view):
    """
    returns maxval for display based on data type and current display mode.
    
    scale_factor so data scales correctly for both wavelength and ev.
    600 is arbitrary    
    """

    scale_factor = 600
    
    if data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        maxval = data_view.maxval
    elif data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        maxval = data_view.maxval*scale_factor
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'ev':   
        maxval = data_view.maxval/scale_factor
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        maxval = data_view.maxval
        
    return maxval
    