# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 16:42:14 2013

@author: JG
"""
import numpy as np
from PySide import QtCore
from PySide import QtGui
import h5py
from scipy import interpolate

#project specific items
import analysis
import generic_thread

class ConvertEvCube():
    """
    Makes an equally spaced ev cube from an equally 
    spaced wavelength cube
    """
    def __init__(self, hdf5_file, wavelength_xdata, dimension1, dimension2,
                 convert_mutex):
        self.convert_mutex = convert_mutex
        self.progress_mutex = QtCore.QMutex()
        self.threadPool = []
        self.convert_mutex = QtCore.QMutex()
        self.stop_convert = False
        self.hdf5_file = hdf5_file
        self.progress_bar = self.convert_progress_bar(dimension1*dimension2) 
                
        self.threadPool.append(generic_thread.GenericThread(self.convert_ev_cube_process,
                                             self.hdf5_file,
                                             wavelength_xdata,
                                             dimension1, dimension2))               
        self.threadPool[len(self.threadPool)-1].start() 

    def convert_ev_cube_process(self, hdf5_file, wavelength_xdata, dimension1,
                      dimension2):
        """
        makes an ev cube from wavelength cube and puts it into original file
        """
        locker = QtCore.QMutexLocker(self.convert_mutex)
        ev_xdata = 1240/wavelength_xdata        
 
        ev_step = ev_xdata[1]-ev_xdata[0]
        rebinned_ev_xdata =  np.arange(start=ev_xdata[0], stop=ev_xdata[-1],
                                       step=ev_step)     
        ev_list_size, = np.shape(rebinned_ev_xdata)                                     
        ev_cube = hdf5_file.create_dataset('Experiments/__unnamed__/ev_data',
                                                 (dimension1,
                                                  dimension2, ev_list_size))
        hdf5_file.create_dataset('Experiments/__unnamed__/ev_xdata', 
                                 data=rebinned_ev_xdata)

        for i in np.arange(dimension1):
            for j in np.arange(dimension2):
                if self.stop_convert:
                    return
                ydata = hdf5_file["Experiments/__unnamed__/data"][i,j,:]
                ev_ydata = analysis.ydata_calc2(input_ydata=ydata,
                                                input_xdata=wavelength_xdata,
                                                dtype='wavelength',
                                                display_ev=True)
                rebinned_ev_ydata = self.rebin_ev_ydata(ev_ydata,ev_xdata,
                                                        rebinned_ev_xdata)
                ev_cube[i,j,:] = rebinned_ev_ydata
                current_spectrum = i*dimension2 + j
                self.update_progress(current_spectrum)
        self.progress_window.close()  
        
    def convert_progress_bar(self, maximum):
        """
        progress bar window with stop button
        """
        locker = QtCore.QMutexLocker(self.progress_mutex)
        self.progress_window = QtGui.QWidget()
        self.progress_window.setWindowTitle("Conversion Progress")
        progress_bar = QtGui.QProgressBar()
        button_stop_conversion = QtGui.QPushButton("&Stop Conversion")
        button_stop_conversion.clicked.connect(self.stop_conversion_now)
        progress_bar.setMaximum(maximum)
        box = QtGui.QVBoxLayout()
        box.addWidget(progress_bar)
        box.addWidget(button_stop_conversion)
        self.progress_window.setLayout(box)
        self.progress_window.show()
        return progress_bar
        
    def rebin_ev_ydata(self, ev_ydata, ev_xdata, rebinned_ev_xdata):
        """
        Takes unequally spaced ev data and rebins it to make
        equally spaced ev data
        """
        
        f = interpolate.interp1d(ev_xdata, ev_ydata)
        rebinned_ev_ydata = []
        count = 0
        for xdatum in rebinned_ev_xdata:
            ydatum = f(xdatum)
            if count == 0:
                rebinned_ev_ydata = ydatum
                count = 1
            else:
                rebinned_ev_ydata = np.c_[rebinned_ev_ydata, ydatum]
        return rebinned_ev_ydata
        
    def stop_conversion_now(self):
        self.stop_convert = True
        locker = QtCore.QMutexLocker(self.convert_mutex)
        del self.hdf5_file['Experiments/__unnamed__/ev_data']
        del self.hdf5_file['Experiments/__unnamed__/ev_xdata']
        self.progress_window.close()
        
    def update_progress(self, value):
        #update progress bar less freqently if it slows down process
        if value%1 == 0:
            self.progress_bar.setValue(value)  