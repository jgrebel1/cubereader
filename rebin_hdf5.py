# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 15:08:15 2013

@author: JG
"""
import shutil
import numpy as np
import os
from PySide import QtCore
from PySide import QtGui
import h5py

#project specific items

import analysis


class RebinHDF5(QtGui.QMainWindow):
    """
    Rebins HDF5 file from CubeReader or hyperspy.
    
    The program prompts the user for input file, new dimensions and output file
    and then starts the rebinning in a new thread
    """
    def __init__(self, parent=None):
        super(RebinHDF5, self).__init__(parent)
        self.stop_rebin = False
        self.rebin_mutex = QtCore.QMutex()
        self.threadPool = []
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        dialog.setNameFilter('HDF5 (*.hdf5);; All Files (*.*)')
        self.filefilter = 'HDF5 (*.hdf5)'
        dialog.filterSelected.connect(self.filterSelected)
        if dialog.exec_():
            filenames = dialog.selectedFiles()
        for filename in filenames:
            self.rebin_hdf5_process(filename)
            
    def filterSelected(self, filter):
        self.filefilter = filter
        
    def get_dimensions(self, input_file):
        input_hdf5 = h5py.File(input_file, 'r')
        ycube = input_hdf5["Experiments/__unnamed__/data"]
        (input_rows, input_columns, input_slices) = np.shape(ycube[...])
        dimensions = RebinWindow(input_rows, input_columns, input_slices)
        dimensions.exec_()
        if dimensions.result():
            new_rows = int(dimensions.textbox_rows.text())
            new_columns = int(dimensions.textbox_columns.text())
        else:
            new_rows = input_rows
            new_columns = input_columns
        return (new_rows, new_columns, input_slices)
        
    def get_output_filename(self, input_file):
        hdf5_directory = QtGui.QFileDialog.getExistingDirectory()
        file_exists = True
        count = 0
        while file_exists == True:
            basename = analysis.get_file_basename(input_file)
            full_basename = 'Rebinned%02d'%count + '-' + basename
            output_filename = os.path.join(hdf5_directory, full_basename) +'.hdf5'
            try:
                with open(output_filename): pass
                count += 1
            except IOError:
                file_exists = False
        return output_filename
        
    def rebin_hdf5(self, input_file, output_file, new_rows, new_columns):
        """
        makes a temporary hdf5 file, rebins image slices into the file and
        then uses the temp file as data for the final output.
        """
        self.input_hdf5 = h5py.File(input_file, 'r')
        ycube = self.input_hdf5["Experiments/__unnamed__/data"]
        (input_rows, input_columns, input_slices) = np.shape(ycube[...])
        self.temp_hdf5 = h5py.File(output_file +'temporary','w')
        self.read_into_temp_hdf5(self.temp_hdf5,
                                 ycube,
                                 new_rows,
                                 new_columns,
                                 input_slices)
        if not self.stop_rebin:
            self.generate_output(input_file, output_file, self.temp_hdf5)
            self.temp_hdf5.close()
            os.remove(output_file +'temporary')
            self.input_hdf5.close()       
        
    def rebin_hdf5_process(self, input_file):
        """
        gets rows, columns, progress bar and starts the rebinning in a 
        new thread
        """
        print 'Reading file %s'%input_file
        new_rows, new_columns, slices = self.get_dimensions(input_file)
        output_filename = self.get_output_filename(input_file)
        self.progress_bar = self.rebin_progress_bar(slices)
        print 'Saving file %s'%output_filename
        self.threadPool.append(GenericThread(self.rebin_hdf5,input_file, 
                                             output_filename, new_rows,
                                             new_columns))
        self.threadPool[len(self.threadPool)-1].start()           
        
    def rebin(self, a, *args):
        '''
        from scipy.org cookbook
        
        rebin ndarray data into a smaller ndarray of the same rank whose dimensions
        are factors of the original dimensions. eg. An array with 6 columns and 4 rows
        can be reduced to have 6,3,2 or 1 columns and 4,2 or 1 rows.
        example usages:
        >>> a=rand(6,4); b=rebin(a,3,2)
        >>> a=rand(6); b=rebin(a,2)
        '''
        shape = a.shape
        lenShape = len(shape)
        assert len(shape) == len(args)
        factor = np.asarray(shape)/np.asarray(args)
        evList = ['a.reshape('] + \
                ['args[%d],factor[%d],'%(i,i) for i in range(lenShape)] + \
                [')'] + ['.sum(%d)'%(i+1) for i in range(lenShape)] + \
                ['/factor[%d]'%i for i in range(lenShape)]
        #print ''.join(evList)
        return eval(''.join(evList))
        
    def rebin_progress_bar(self, maximum):
        """
        progress bar window with stop button
        """
        self.progress_window = QtGui.QWidget()
        self.progress_window.setWindowTitle("Rebin Progress")
        progress_bar = QtGui.QProgressBar()
        progress_bar.setMaximum(maximum)
        button_stop_rebin = QtGui.QPushButton("&Stop Rebin")
        button_stop_rebin.clicked.connect(self.stop_rebin_now)
        
        box = QtGui.QVBoxLayout()
        box.addWidget(progress_bar)
        box.addWidget(button_stop_rebin)
        self.progress_window.setLayout(box)
        self.progress_window.show()
        return progress_bar
        
        
    def read_into_temp_hdf5(self, temp_hdf5, ycube, rows, columns, slices):
        locker = QtCore.QMutexLocker(self.rebin_mutex)
        temp_cube = temp_hdf5.create_dataset('cube', (rows, columns, slices))
        for input_slice in np.arange(slices):
            if self.stop_rebin:
                return
            image = ycube[:,:,input_slice]
            rebinned_image = self.rebin(image, rows, columns)
            temp_cube[:,:,input_slice] = rebinned_image
            self.update_progress(input_slice)  
        self.progress_window.close()
        
    def generate_output(self,input_file, output_file, temp_hdf5):
        locker = QtCore.QMutexLocker(self.rebin_mutex)
        shutil.copy(input_file, output_file)
        output_hdf5 = h5py.File(output_file, 'r+')   
        del output_hdf5["Experiments/__unnamed__/data"]
        new_ycube = output_hdf5.create_dataset("Experiments/__unnamed__/data",
                                               data = temp_hdf5['cube'])
        output_hdf5.close()
        
    def stop_rebin_now(self):
        self.stop_rebin = True
        locker = QtCore.QMutexLocker(self.rebin_mutex)
        self.input_hdf5.close()
        self.temp_hdf5.close()
        self.progress_window.close()
        
    def update_progress(self, value):
        #update less freqently if it slows down process
        #if value%10 == 0:
        self.progress_bar.setValue(value)         
        
class RebinWindow(QtGui.QDialog):
    
    def __init__(self, input_rows, input_columns, input_slices):
        self.input_rows = input_rows
        self.input_columns = input_columns
        self.input_slices = input_slices
        super(RebinWindow, self).__init__()
        self.setWindowTitle('Rebin Dimensions')
        self.inputs()
        
    def inputs(self):
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
          

class GenericThread(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        self.function(*self.args,**self.kwargs)
        return        
            
        
