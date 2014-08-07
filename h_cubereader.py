# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 11:27:41 2014

@author: jg
"""
import sys
from PySide import QtGui
import matplotlib
matplotlib.rcParams['backend.qt4']='PySide'

#project specific items

import analysis
import data_view
import data_holder
import spectrum_holder
import view_windows
import wraith_for_cubereader
import convert_file
import rebin_hdf5
import visualization
import file_tools
import spectrum_viewer
import transform_wrapper

def convert_to_Cubereader(filename=None):
    return convert_file.main(filename)
    
def load_data(filename=None):
    """Loads Cubereader HDF5 file"""
    if filename==None:
        filename = file_tools.file_dialog()
    data = data_holder.Data(filename)
    maxval = analysis.find_maxval(data.ycube[...])
    dimensions = analysis.get_dimensions(data.ycube)
    dataview = data_view.DataView(maxval, dimensions)
    return data, dataview
    
def load_fit(filename=None):
    """Unimplemented"""
    if filename==None:
        filename = file_tools.file_dialog()
    fit_data = data_holder.FitData(filename)
    fit_dataview = data_view.FitDataView()
    return fit_data, fit_dataview

def spec_holder(cube):
    data = cube[0]
    dataview = cube[1]
    holder = spectrum_holder.SpectrumHolder(data.filename, dataview.dimension1,
                                  dataview.dimension2)
    return holder

def transform(filename, output_filename=None, action=None,images=True):
    return transform_wrapper.main(filename,output_filename, action, images)

def show_3d(cube, vmin=None,vmax=None):
    """opens mayavi window"""
    data = cube[0]
    dataview = cube[1]
    
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
        
    data.check_for_ev_cube(data.hdf5)
    ycube = analysis.mayavi_cube(data, dataview)
    if ycube == []:
        print "No ev cube in file. Press Make ev Cube"
        return
    if dataview.display_ev:
        if vmax is not None:
            dataview.vmin_wavelength = 1240/vmax
        if vmin is not None:
            dataview.vmax_wavelength = 1240/vmin
    else:
        if vmin is not None:
            dataview.vmin_wavelength = vmin
        if vmax is not None:
            dataview.vmax_wavelength = vmax

    min_slice, max_slice = analysis.mayavi_slices(data, dataview)
    
    #order min and max correctly
    try:
        ycube_slice = ycube[:,:,min_slice:max_slice]
    except ValueError:
        ycube_slice = ycube[:,:,max_slice:min_slice]
    visualization_window = visualization.MayaviQWidget(ycube_slice)
    app.exec_()
    return visualization_window
       
def rebin_HDF5(filename=None):
    return rebin_hdf5.main(filename)

def wraith(cube, spectrum_holder):
    """opens wraith window"""
    data = cube[0]
    dataview = cube[1]
    return wraith_for_cubereader.main(data, dataview, spectrum_holder)

def view_data(cube):
    return view_windows.data(cube)

def view_fit(fit, cube):
    return view_windows.fit(fit, cube)

def view_spec_holder(spectrum_holder):
    return spectrum_viewer.main(spectrum_holder)