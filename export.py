# -*- coding: utf-8 -*-
"""
Created on Mon Jul 08 17:44:52 2013

@author: JG
"""
import os
import analysis
import numpy as np
import copy

def export_spectrum(filename, data, data_view):
    """
    export the current spectrum to an excel file in the original file's folder
    """
    location = 'x' + str(data_view.xcoordinate) + 'y' + str(data_view.ycoordinate)
    no_ext_filename, ext = os.path.splitext(filename)
    out_filename = no_ext_filename + location + '.csv'
    xdata = analysis.xdata_calc(data,data_view)
    ydata = analysis.ydata_calc(data,data_view)
    out = np.c_[xdata,ydata]
    np.savetxt(str(out_filename), out, delimiter=",", fmt="%10.5f")
    
def export_cube(filename, data, data_view):
    """
    export the entire cube to an excel file in the original file's
    folder.
    
    format is xdata, spectrum etc.
    """
    display_ev = copy.copy(data_view.display_ev)
    no_ext_filename, ext = os.path.splitext(filename)
    out_filename = no_ext_filename + '.csv'
    rows, columns, slices = np.shape(data.ycube[...])
    spectra_count = 0
    for i in np.arange(rows):
        for j in np.arange(columns):
            xdata = analysis.xdata_calc2(data.xdata,
                                         data.xdata_info['data_type'],
                                         display_ev)
            ydata = analysis.ydata_calc2(data.ycube[i,j,:],
                                         data.xdata,
                                         data.xdata_info['data_type'],
                                         display_ev)
            if spectra_count == 0:
                out = np.c_[xdata, ydata]
                spectra_count = 1
            else:
                out = np.c_[out, xdata, ydata]
            print np.shape(out)
    np.savetxt(str(out_filename), out, delimiter=",", fmt="%10.5f")