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



class ConvertToCubeReader():
    def __init__(self):
        self.convert_mutex = QtCore.QMutex()
        self.threadPool = []
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        dialog.setNameFilter('MF1 (*.mf1);; All Files (*.*)')
        self.filefilter = 'MF1 (*.mf1)'
        dialog.filterSelected.connect(self.filterSelected)
        if dialog.exec_():
            filenames = dialog.selectedFiles()
        if self.filefilter == 'MF1 (*.mf1)':
            self.convert_mf1_to_cubereader(filenames)         
                
    def convert_mf1_to_cubereader(self, filenames):
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
                full_basename = 'CubeReader-' + basename
                output_filename = os.path.join(hdf5_directory, full_basename) +'.hdf5'
                
                
                dimension1, dimension2, global_bool = self.get_initial_settings_for_mf1(default_values)
                print('Saving file: %s'%output_filename)
                self.progress_bar = self.convert_progress_bar(dimension1*dimension2) 
                
                self.threadPool.append(GenericThread(cube_loader.Mf1Converter,
                                                     filename, 
                                                     output_filename,
                                                     dimension1, 
                                                     dimension2,
                                                     global_bool,
                                                     self.progress_bar))
                
                self.threadPool[len(self.threadPool)-1].start() 
                
                
                #cube_loader.Mf1Converter(filename, 
                                         #output_filename,
                                         #dimension1, 
                                         #dimension2,
                                         #global_bool,
                                         #self.progress_bar)
                
                #print 'Conversion Completed'
            else:
                print 'No file selected'
                
    
        
    def get_initial_settings_for_mf1(self, default_values):
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

    def filterSelected(self, filter):
        self.filefilter = filter
        
    def convert_progress_bar(self, maximum):
        """
        progress bar window with stop button
        """
        self.progress_window = QtGui.QWidget()
        self.progress_window.setWindowTitle("Conversion Progress")
        progress_bar = QtGui.QProgressBar()
        button_stop_rebin = QtGui.QPushButton("&Stop Conversion")
        #button_stop_rebin.clicked.connect(self.stop_conversion_now)
        progress_bar.setMaximum(maximum)
        box = QtGui.QVBoxLayout()
        box.addWidget(progress_bar)
        box.addWidget(button_stop_rebin)
        self.progress_window.setLayout(box)
        self.progress_window.show()
        return progress_bar
    
    def stop_conversion_now(self):
        pass
        
    def update_progress(self, value):
        #update less freqently if it slows down process
        #if value%10 == 0:
        self.progress_bar.setValue(value)     
class GenericThread(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    #def __del__(self):
        #self.wait()

    def run(self):
        self.function(*self.args,**self.kwargs)
        return