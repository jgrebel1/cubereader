# -*- coding: utf-8 -*-
"""
Created on Mon Jul 01 13:57:51 2013

@author: JG
"""
import os
import numpy as np
from scipy import interpolate

def colors_calc(data, data_view):
    """
    returns min and max colors for display based on data type
    and current display mode.
    
    scale_factor so data scales correctly for both wavelength and ev.
    600 is arbitrary   
    """
    scale_factor = 600
    if data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        max_color = data_view.maxcolor
        min_color = data_view.mincolor
    elif data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        max_color = data_view.maxcolor*scale_factor
        min_color = data_view.mincolor*scale_factor
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'ev':   
        max_color = data_view.maxcolor/scale_factor
        min_color = data_view.mincolor/scale_factor
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        max_color = data_view.maxcolor
        min_color = data_view.mincolor

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
    
def ev_to_index(ev, data):
    """
    converts an input ev value to an index in the default cube
    """
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

def ev_to_index2(ev, data):
    """
    converts an input ev to an index in the extra ev cube
    """
    value = ev
    ordered_xdata = data.ev_xdata
    index = index_from_ordered_list(value, ordered_xdata)
    return index
    
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

def mayavi_cube(data, data_view):
    """
    chooses correct cube to use for mayavi based on data type and data_view.
    Choice is between default and ev_cube.
    """
    if data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        ycube = data.ycube
    elif data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        ycube = data.ev_ycube
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'ev':   
        ycube = data.ycube
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        ycube = data.ycube
    return ycube
    
def mayavi_slices(data, data_view):
    """
    returns min and max slices based on data type and data view.
    The only difference occurs for wavelength data and ev display. Then the 
    slices are from the ev_cube.
    """
    if data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        min_slice = wavelength_to_index(data_view.vmin_wavelength, data)
        max_slice = wavelength_to_index(data_view.vmax_wavelength, data)
    elif data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        max_slice = wavelength_to_index2(data_view.vmin_wavelength, data)
        min_slice = wavelength_to_index2(data_view.vmax_wavelength, data)
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'ev':   
        min_slice = wavelength_to_index(data_view.vmin_wavelength, data)
        max_slice = wavelength_to_index(data_view.vmax_wavelength, data)
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        min_slice = wavelength_to_index(data_view.vmin_wavelength, data)
        max_slice = wavelength_to_index(data_view.vmax_wavelength, data)
        
    return min_slice, max_slice
    
def v_labels(data_view):
    """
    returns labels for visualization input based on current
    data_view
    """
    if data_view.display_ev:
        min_label = 'Min ev:'
        max_label = 'Max ev:'
    else:
        min_label = 'Min wavelength:'
        max_label = 'Max wavelength:'
    return (min_label, max_label)
    
def v_text(data_view):
    """
    returns text for visualization input based on current
    data_view
    """
    if data_view.display_ev:
        min_text = 1240/data_view.vmin_wavelength
        max_text = 1240/data_view.vmax_wavelength
    else:
        min_text = data_view.vmin_wavelength
        max_text = data_view.vmax_wavelength
    return (str(min_text), str(max_text))    
    
def wavelength_to_index(wavelength, data):
    """
    converts an input wavelength to the nearest xdata index using 
    interpolation. For default data_cube.
    """
    if wavelength == 0:
        wavelength = .000001
    ev = 1240/wavelength
    index = ev_to_index(ev, data)
    return index
    
def wavelength_to_index2(wavelength, data):
    """
    converts an input wavelength to the nearest xdata index using
    interpolation. For ev_cube.
    """
    if wavelength == 0:
        wavelength = .000001
    ev = 1240/wavelength
    index = ev_to_index2(ev, data)
    return index
    

    
def xdata_calc(data, data_view):
    """
    returns xdata based on data type and current display mode from wavelength
    cube
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
    """
    returns xdata based on data type and current display mode from wavelength
    cube
    """
    if display_ev and dtype == 'ev':
        xdata = input_xdata
    elif display_ev and dtype == 'wavelength':
        xdata = 1240/input_xdata
    elif not display_ev and dtype == 'ev':
        xdata = 1240/input_xdata
    elif not display_ev and dtype == 'wavelength':
        xdata = input_xdata
    return xdata
    
def xdata_calc_cubes(data, data_view):
    """
    chooses which data_cube to take xdata from based on data type and
    current display mode. data.xdata is the default xdata, data.ev_xdata
    occurs only when converting from mf1 files which has two separate data
    cubes with wavelength and ev data.
    
    The data with data type ev we are reading currently
    does not have meaning in wavelength, so its result is a placeholder.
    """
    if data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        xdata = data.xdata
    elif data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        xdata = data.ev_xdata
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        xdata = 1240/data.xdata
    elif not data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        xdata = data.xdata
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
