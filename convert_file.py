# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 19:08:08 2013

@author: JG
"""
import os
from PySide import QtCore
from PySide import QtGui

#project specific items

import default
import cube_loader
import analysis
import init_settings

def convert_mf1():
    
    dialog = QtGui.QFileDialog()
    dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
    dialog.setNameFilter('MF1 (*.mf1)')
    if dialog.exec_():
        filenames = dialog.selectedFiles()
    for filename in filenames:
        if filename:    
            print('Reading file: %s'%filename)
            print 'Pick a folder to save the hdf5 file'
            with open(filename,'rb') as fid:
                text_header=fid.read(2048)
                print text_header
            hdf5_directory = QtGui.QFileDialog.getExistingDirectory()
            default_values = default.DefaultValues(filename)
            basename = analysis.get_file_basename(filename)
            hdf5_file = os.path.join(hdf5_directory, basename) +'.hdf5'
            
            
            dimension1, dimension2, global_bool = get_initial_settings(default_values)
            print('Saving file: %s'%basename)        
            cube_loader.Mf1File(filename,hdf5_file,
                                dimension1, dimension2,
                                global_bool)

            print 'Conversion Complete'
        else:
            print 'No file selected'
    
def get_initial_settings(default_values):
    """
    calls the Initial Settings window and returns the default values.
    """
    dimension1, dimension2 = default_values.default_dimensions() 
    global_bool = default_values.default_global()
    initialsettings = init_settings.InitialSettingsWindow(dimension1,
                                                          dimension2,
                                                          global_bool) 
    initialsettings.exec_()
    
    if initialsettings.result() and initialsettings.dimension1Edit.text()!='':
        print 'Dimension 1 is now ', initialsettings.dimension1Edit.text()
        dimension1 = int(initialsettings.dimension1Edit.text())
    if initialsettings.result() and initialsettings.dimension2Edit.text()!='':   
        print 'Dimension 2 is now ', initialsettings.dimension2Edit.text()
        dimension2 = int(initialsettings.dimension2Edit.text())
    if initialsettings.result():
        global_bool = initialsettings.globalwavelength.isChecked()
        print 'global_bool is', global_bool
    return (dimension1, dimension2, global_bool)
        