# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 15:08:15 2013

@author: JG
"""
import shutil
import numpy as np
import os
import sys
try:
    from PySide import QtCore
    from PySide import QtGui
except Exception as e:
    print "failed to import PySide"
import h5py

#project specific items

import analysis
import generic_thread
import hdf5_action
import actions

class Transform(QtGui.QMainWindow):
    """
    Wrapper for HDF5Action.
    Transforms HDF5 file from CubeReader or hyperspy.
    """
    def __init__(self, filename=None, output_filename=None,action=None, images=True, parent=None):
        super(Transform, self).__init__(parent)
        #self.stop_normalize = False
        #self.normalize_mutex = QtCore.QMutex()
        #self.threadPool = []
        filenames = self.get_filenames(filename)
        for filename in filenames:
            if not output_filename:
                output_filename = self.get_output_filename(filename)
            hdf5_action.HDF5Action(filename, output_filename,action, images )
            
    def filterSelected(self, filter_):
        self.filefilter = filter_
        
    def get_filenames(self, filename):
        print 'filename is', filename
        if filename==None:
            print 'test'
            dialog = QtGui.QFileDialog()
            dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
            dialog.setNameFilter('HDF5 (*.hdf5);; All Files (*.*)')
            self.filefilter = 'HDF5 (*.hdf5)'
            dialog.filterSelected.connect(self.filterSelected)
            if dialog.exec_():
                filenames = dialog.selectedFiles()
        else:
            filenames = []
            filenames.append(filename)
        return filenames
        
    def get_output_filename(self, input_file):
        hdf5_directory = QtGui.QFileDialog.getExistingDirectory()
        file_exists = True
        count = 0
        while file_exists == True:
            basename = analysis.get_file_basename(input_file)
            full_basename = 'new%02d'%count + '-' + basename
            output_filename = os.path.join(hdf5_directory, full_basename) +'.hdf5'
            try:
                with open(output_filename): pass
                count += 1
            except IOError:
                file_exists = False
        return output_filename          

        
#main function to start up program
def main(filename=None, output_filename=None, action=None, Images=True):
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
        form = Transform(filename,output_filename, action, Images)
        app.exec_()
        return form
    else:
        form = Transform(filename,output_filename, action, Images)
        app.exec_()
        return form  
if __name__ == "__main__":
     main('C:/Users/jg/Documents/Summer 2014/Shaul/notebooks/spectrum image zlp cor2.hdf5',
     'C:/Users/jg/Documents/Summer 2014/Shaul/New folder/newier01-spectrum image zlp cor2.hdf5'    )          