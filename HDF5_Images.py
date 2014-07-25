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
except:
    pass
import h5py

#project specific items

import analysis
import generic_thread


class HDF5Images(object):
    """
    Applies action to HDF5 file images from CubeReader or hyperspy.
    
    The program starts the action in a new thread
    """
    def __call__(self, filename, output_filename, action, axis = 0):
        print 'Reading file %s'%filename
        self.progress_bar = self.initialize_progress_bar(filename)
        print 'Saving file %s'%output_filename
        self.start_in_new_thread(self.hdf5_images, filename, output_filename, action)
        

    def find_title(self, hdf5):
        g = lambda x: x
        title = str(hdf5['Experiments'].visit(g))
        return title
    
    def get_ycube(self,filename):
        self.input_hdf5 = h5py.File(filename, 'r')
        title = self.find_title(filename)
        ycube = self.input_hdf5["Experiments/%s/data"%title]
        return ycube
    
    def get_dimensions(self, filename):
        ycube = self.get_ycube(filename)
        (input_rows, input_columns, input_slices) = np.shape(ycube[...])
        return (input_rows, input_columns, input_slices)
    
    def hdf5_images(self, filename, output_filename, action):
        """
        makes a temporary hdf5 file, performs action on image slices into the file and
        then uses the temp file as data for the final output.
        """
        ycube = self.get_ycube(filename)
        self.temp_hdf5 = h5py.File(output_filename +'temporary','w')
        self.read_into_temp_hdf5(self.temp_hdf5,
                                 ycube)
        if not self.stop:
            self.generate_output(filename, output_filename, self.temp_hdf5)
            self.temp_hdf5.close()
            os.remove(output_filename +'temporary')
            self.input_hdf5.close()       
    
    def initialize_progress_bar(self, filename):
        try:
            rows, columns, slices = self.get_dimensions(filename)
            progress_bar = self._progress_bar(slices)
        except:
            pass
        return progress_bar
    
    def progress_bar(self, maximum):
        """
        progress bar window with stop button
        """
        self.progress_window = QtGui.QWidget()
        self.progress_window.setWindowTitle("Progress")
        progress_bar = QtGui.QProgressBar()
        progress_bar.setMaximum(maximum)
        button_stop= QtGui.QPushButton("&Stop")
        button_stop.clicked.connect(self.stop_now)
        
        box = QtGui.QVBoxLayout()
        box.addWidget(progress_bar)
        box.addWidget(button_stop)
        self.progress_window.setLayout(box)
        self.progress_window.show()
        return progress_bar
        
        
    def read_into_temp_hdf5(self, temp_hdf5, ycube, action, images = True):
        shape = np.shape(ycube[...])
        temp_cube = temp_hdf5.create_dataset('cube', shape)
        if images:
            self.iterate_images(ycube)
        else:
            self.iterate_spectrums(ycube)
        try:
            self.progress_window.close()
        except:
            pass
        
    def iterate_images(self,ycube, temp_cube):
        slices = np.shape(ycube)[2]
        for input_slice in np.arange(slices):
            if self.stop:
                return
            image = ycube[:,:,input_slice]
            new_image = self.action(image)
            temp_cube[:,:,input_slice] = new_image
            try:
                self.update_progress(input_slice)  
            except:
                pass
            
    def iterate_spectrums(self, ycube, temp_cube):
        raise NotImplementedError()
        
    def generate_output(self,filename, output_file, temp_hdf5):
        shutil.copy(filename, output_file)
        output_hdf5 = h5py.File(output_file, 'r+')
        title = self.get_title(filename)   
        del output_hdf5["Experiments/%s/data"%title]
        new_ycube = output_hdf5.create_dataset("Experiments/%s/data"%title,
                                               data = temp_hdf5['cube'])
        output_hdf5.close()
        
    def start_in_new_thread(self, function, *args):
        self.threadPool = []
        self.threadPool.append(generic_thread.GenericThread(function,args))
        self.threadPool[len(self.threadPool)-1].start()      
        return self.threadPool
    def stop_now(self):
        self.stop = True
        self.input_hdf5.close()
        self.temp_hdf5.close()
        self.progress_window.close()
        
    def update_progress(self, value):
        #update less freqently if it slows down process
        #if value%10 == 0:
        self.progress_bar.setValue(value)         
 
 
#main function to start up program
def main(filename=None):
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
        form = HDF5Images(filename)
        app.exec_()
        return form
    else:
        form = HDF5Images(filename)
        app.exec_()
        return form            