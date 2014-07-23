# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 15:08:15 2013

@author: JG
"""
import shutil
import numpy as np
import os
import sys
from PySide import QtCore
from PySide import QtGui
import h5py

#project specific items

import analysis
import generic_thread


class NormalizeHDF5(QtGui.QMainWindow):
    """
    Normalizes HDF5 file from CubeReader or hyperspy.
    
    The program prompts the user for input file, new dimensions and output file
    and then starts the normalizening in a new thread
    """
    def __init__(self, filename=None, parent=None):
        super(NormalizeHDF5, self).__init__(parent)
        self.stop_normalize = False
        self.normalize_mutex = QtCore.QMutex()
        self.threadPool = []
        if filename==None:
            dialog = QtGui.QFileDialog()
            dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
            dialog.setNameFilter('HDF5 (*.hdf5);; All Files (*.*)')
            self.filefilter = 'HDF5 (*.hdf5)'
            dialog.filterSelected.connect(self.filterSelected)
            if dialog.exec_():
                filenames = dialog.selectedFiles()
            for filename in filenames:
                self.normalize_hdf5_process(filename)
        else:
            self.normalize_hdf5_process(filename) 
            
    def filterSelected(self, filter_):
        self.filefilter = filter_
    def get_dimensions(self, input_file):
        input_hdf5 = h5py.File(input_file, 'r')
        ycube = input_hdf5["Experiments/__unnamed__/data"]
        (input_rows, input_columns, input_slices) = np.shape(ycube[...])
        #dimensions = normalizeWindow(input_rows, input_columns, input_slices)
        #dimensions.exec_()
        #if dimensions.result():
        #    new_rows = int(dimensions.textbox_rows.text())
        #    new_columns = int(dimensions.textbox_columns.text())
        #else:
        #    new_rows = input_rows
        #    new_columns = input_columns
        return (input_rows, input_columns, input_slices)
        
    def get_output_filename(self, input_file):
        hdf5_directory = QtGui.QFileDialog.getExistingDirectory()
        file_exists = True
        count = 0
        while file_exists == True:
            basename = analysis.get_file_basename(input_file)
            full_basename = 'normalizened%02d'%count + '-' + basename
            output_filename = os.path.join(hdf5_directory, full_basename) +'.hdf5'
            try:
                with open(output_filename): pass
                count += 1
            except IOError:
                file_exists = False
        return output_filename
        
    def normalize_hdf5(self, input_file, output_file):
        """
        makes a temporary hdf5 file, normalizes image slices into the file and
        then uses the temp file as data for the final output.
        """
        self.input_hdf5 = h5py.File(input_file, 'r')
        ycube = self.input_hdf5["Experiments/__unnamed__/data"]
        (input_rows, input_columns, input_slices) = np.shape(ycube[...])
        self.temp_hdf5 = h5py.File(output_file +'temporary','w')
        self.read_into_temp_hdf5(self.temp_hdf5,
                                 ycube, input_slices, input_rows, input_columns)
        if not self.stop_normalize:
            self.generate_output(input_file, output_file, self.temp_hdf5)
            self.temp_hdf5.close()
            os.remove(output_file +'temporary')
            self.input_hdf5.close()       
        
    def normalize_hdf5_process(self, input_file):
        """
        gets rows, columns, progress bar and starts the normalizening in a 
        new thread
        """
        print 'Reading file %s'%input_file
        input_rows, input_columns, slices = self.get_dimensions(input_file)
        output_filename = self.get_output_filename(input_file)
        self.progress_bar = self.normalize_progress_bar(slices)
        print 'Saving file %s'%output_filename
        self.threadPool.append(generic_thread.GenericThread(self.normalize_hdf5,input_file, 
                                             output_filename))
        self.threadPool[len(self.threadPool)-1].start()           
        
    def normalize(self, a):
        amax = np.amax(a)
        new_a = a/float(amax)
        return new_a
        
    def normalize_progress_bar(self, maximum):
        """
        progress bar window with stop button
        """
        self.progress_window = QtGui.QWidget()
        self.progress_window.setWindowTitle("normalize Progress")
        progress_bar = QtGui.QProgressBar()
        progress_bar.setMaximum(maximum)
        button_stop_normalize = QtGui.QPushButton("&Stop normalize")
        button_stop_normalize.clicked.connect(self.stop_normalize_now)
        
        box = QtGui.QVBoxLayout()
        box.addWidget(progress_bar)
        box.addWidget(button_stop_normalize)
        self.progress_window.setLayout(box)
        self.progress_window.show()
        return progress_bar
        
        
    def read_into_temp_hdf5(self, temp_hdf5, ycube, slices, rows, columns):
        locker = QtCore.QMutexLocker(self.normalize_mutex)
        temp_cube = temp_hdf5.create_dataset('cube', (rows, columns, slices))
        for input_slice in np.arange(slices):
            if self.stop_normalize:
                return
            image = ycube[:,:,input_slice]
            normalizened_image = self.normalize(image)
            temp_cube[:,:,input_slice] = normalizened_image
            self.update_progress(input_slice)  
        self.progress_window.close()
        
    def generate_output(self,input_file, output_file, temp_hdf5):
        locker = QtCore.QMutexLocker(self.normalize_mutex)
        shutil.copy(input_file, output_file)
        output_hdf5 = h5py.File(output_file, 'r+')   
        del output_hdf5["Experiments/__unnamed__/data"]
        new_ycube = output_hdf5.create_dataset("Experiments/__unnamed__/data",
                                               data = temp_hdf5['cube'])
        output_hdf5.close()
        
    def stop_normalize_now(self):
        self.stop_normalize = True
        locker = QtCore.QMutexLocker(self.normalize_mutex)
        self.input_hdf5.close()
        self.temp_hdf5.close()
        self.progress_window.close()
        
    def update_progress(self, value):
        #update less freqently if it slows down process
        #if value%10 == 0:
        self.progress_bar.setValue(value)         
        
class normalizeWindow(QtGui.QDialog):
    
    def __init__(self, input_rows, input_columns, input_slices):
        self.input_rows = input_rows
        self.input_columns = input_columns
        self.input_slices = input_slices
        super(normalizeWindow, self).__init__()
        self.setWindowTitle('normalize Dimensions')
        self.inputs()
        
    def inputs(self):
        """populate screen"""
        label_current_dimensions = QtGui.QLabel("Current Dimensions are rows:%s, columns:%s, %s,"%(str(self.input_rows),
                                                                                                   str(self.input_columns),
                                                                                                   str(self.input_slices)))
        label_warning = QtGui.QLabel("New dimensions must be a factor of current dimensions")
        self.textbox_rows = QtGui.QLineEdit(str(self.input_rows))
        self.textbox_columns = QtGui.QLineEdit(str(self.input_columns))
        
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.textbox_rows)
        hbox1.addWidget(self.textbox_columns)
        
        self.okButton = QtGui.QPushButton("OK")
        self.cancelButton = QtGui.QPushButton("Cancel")
        
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)
        
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(label_current_dimensions)
        vbox.addWidget(label_warning)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)
        self.connect_events()
        self.show()
        
    def connect_events(self):
        self.connect(self.okButton, QtCore.SIGNAL('clicked()'),self.accept)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.reject) 
 
 
#main function to start up program
def main(filename=None):
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
        form = NormalizeHDF5(filename)
        app.exec_()
        return form
    else:
        form = NormalizeHDF5(filename)
        app.exec_()
        return form            