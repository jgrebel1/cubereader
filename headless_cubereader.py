# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 11:27:41 2014

@author: jg
"""
#from PySide import QtCore
#from PySide import QtGui
from PyQt4 import QtCore
from PyQt4 import QtGui
#import matplotlib
from matplotlib import pyplot as plt
#matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

#project specific items

import analysis
import color
import data_view
import plot_tools
import data_holder
import navigation_tools
import spectrum_holder
import view_data
import wraith_for_cubereader_2

def load_data(filename=None):
    if filename==None:
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        dialog.setNameFilter('HDF5 (*.hdf5)')
        if dialog.exec_():
            filenames = dialog.selectedFiles()
        for name in filenames:
            if name:
                filename = name
            else:
                print 'No file selected'
    data = data_holder.Data(filename)
    maxval = analysis.find_maxval(data.ycube[...])
    dimension1, dimension2, number_of_slices = analysis.get_dimensions(data.ycube) 
    dimensions = analysis.get_dimensions(data.ycube)
    dataview = data_view.DataView(maxval, dimensions)
    #convert_mutex = QtCore.QMutex()
    #bool_press = False
    return data, dataview
    
def load_fit(filename):
    pass

def make_spectrum_holder(cube):
    data = cube[0]
    dataview = cube[1]
    holder = spectrum_holder.main(data.filename, dataview.dimension1,
                                  dataview.dimension2)
    #holder = spectrum_holder.SpectrumHolder(data.filename, dataview.dimension1,
    #                                        dataview.dimension2)  
    return holder
    
def open_wraith(cube, spectrum_holder):
    """opens wraith window"""
    data = cube[0]
    dataview = cube[1]
    wraith_window = wraith_for_cubereader_2.Form(data, dataview, spectrum_holder)
    wraith_window.show()  
    return wraith_window

def view(cube=None):

    return view_data.main(cube)
    

    
def view_fit():
    pass
