# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 19:08:08 2013

@author: JG
"""
import os
from PySide import QtCore
from PySide import QtGui
import h5py
import shutil
import numpy as np

#project specific items

import default
import cube_loader
import analysis
import init_settings
import generic_thread



class ConvertToCubeReader():
    def __init__(self):
        self.convert_mutex = QtCore.QMutex()
        self.progress_mutex = QtCore.QMutex()
        self.threadPool = []
        self.convert_mutex = QtCore.QMutex()
        self.stop_convert = False
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
                
                self.threadPool.append(generic_thread.GenericThread(self.convert_mf1,
                                                     filename, 
                                                     output_filename,
                                                     dimension1, 
                                                     dimension2,
                                                     global_bool))
                
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
    
    def stop_conversion_now(self):
        self.stop_convert = True
        locker = QtCore.QMutexLocker(self.convert_mutex)
        self.temp_hdf5.close()
        os.remove(self.output_filename+'temporary')
        self.progress_window.close()        
        
    def update_progress(self, value):
        #update progress bar less freqently if it slows down process
        if value%10 == 0:
            self.progress_bar.setValue(value)   
        
    def convert_mf1(self, input_filename, output_filename, dimension1, dimension2,
                    global_bool):
        """
        Reads the Mf1 File and builds a Data Cube from the intensities,
        xdata (wavelengths) for graph and optionally info for comments.
        """
        #read the file
        self.output_filename = output_filename
        datasize = self.datasize_finder(input_filename, global_bool)
    
        with open(input_filename,'rb') as fid:
            header=fid.read(2048)
            self.temp_hdf5 = h5py.File(output_filename+'temporary','w')
            list_xdata = self.read_into_cube(fid, self.temp_hdf5, global_bool,
                                             dimension1,dimension2)

        if not self.stop_convert:
            self.generate_output(output_filename, self.temp_hdf5, global_bool,
                                 header,list_xdata, dimension1, dimension2)
            self.temp_hdf5.close()
            os.remove(output_filename+'temporary')
        self.progress_window.close()            
       
    def build_xdata(self, data_holder, temp_hdf5, list_xdata):
        """
        builds the wavelength data (x data for graph). 
        """
        data_holder.create_dataset('xdata', data=list_xdata )
        
    def build_ycube(self, data_holder, temp_hdf5, global_bool):
        """
        builds two 3 dimensional arrays with intensity data in wavelength
        and ev
        """
        if global_bool:
            ydata = temp_hdf5["cube"][:,:,0:1600]
        else:
            ydata = temp_hdf5["cube"][:,:,1600:3200]
        data_holder.create_dataset('data', data=ydata)
        
    def build_info(self):
        """
        optional info for each graph. not utilized yet. This may also
        be an outdated function for displaying the info.
        """
        if global_bool:
            info = graph_array[:,1600:1664]
        else:
            info = graph_array[:,3200:3264]
        info = info.transpose()
        return info
       
    def datasize_finder(self, input_filename, global_bool):
        'finds the data size in the mf1 file'
        fileinfo=os.stat(input_filename)
        #subtract header size from total data size and divide by size of 
        #spectrum and comments
        if global_bool:
            datasize = (fileinfo.st_size-2048-4*1600)/(4*3200+256)
        else:
            datasize = (fileinfo.st_size-2048)/(4*3200+256)
        return datasize
        
    def generate_output(self, output_filename, temp_hdf5, global_bool, header,
                        list_xdata, dimension1, dimension2):
        locker = QtCore.QMutexLocker(self.convert_mutex)
        output_file = h5py.File(output_filename,'w')
        data_holder = output_file.create_group("Experiments/__unnamed__")       
        self.build_xdata(data_holder, temp_hdf5, list_xdata)
        #self.info = self.build_info()
        self.build_ycube(data_holder, temp_hdf5, global_bool)
        self.write_header(data_holder, header)
        self.add_formatting(output_file, data_holder, list_xdata,
                            dimension1, dimension2)            
        output_file.close()
              
    def read_into_cube(self, fid, temp_hdf5, global_bool,
                       dimension1, dimension2):
        """read from mf1 file into temporary hdf5 file"""
        locker = QtCore.QMutexLocker(self.convert_mutex)
        if global_bool:
            cube = temp_hdf5.create_dataset('cube',
                                                 (dimension1,
                                                  dimension2, 1664))
    
            list_xdata = np.fromfile(file=fid, dtype='>f', count=1600)
            
            for i in np.arange(dimension1):
                for j in np.arange(dimension2):
                    if self.stop_convert:
                        return
                    try:
                        cube[i,j,:] = np.fromfile(file=fid,
                                                  dtype='>f', count=1664)
                    except:
                        return list_xdata
                    current_spectrum = i*dimension2 + j
                    self.update_progress(current_spectrum)
        else:
            
            cube = temp_hdf5.create_dataset('cube',(dimension1,
                                                    dimension2,
                                                    3264))  
            for i in np.arange(dimension1):
                for j in np.arange(dimension2):
                    if self.stop_convert:
                        return
                    try:
                        cube[i,j,:] = np.fromfile(file=fid, dtype='>f',
                                                  count=3264)
                    except:
                        list_xdata = cube[0,0,0:1600]
                        return 
                    current_spectrum = i*dimension2 + j
                    self.update_progress(current_spectrum)
            list_xdata = cube[0,0,0:1600]
        return list_xdata
                            
    def write_header(self, data_holder, header):
        data_holder.attrs['header'] = header      
        
    def add_formatting(self, output_file, data_holder, list_xdata,
                            dimension1, dimension2):
        output_file.attrs['file_format'] = 'mf1 compatible with Hyperspy'
        output_file.attrs['file_format_version'] = 1.2
        data_holder.create_group('axis-0')
        data_holder['axis-0'].attrs['size'] = dimension1 
        data_holder.create_group('axis-1')
        data_holder['axis-1'].attrs['size'] = dimension2 
        data_holder.create_group('axis-2')
        data_holder['axis-2'].attrs['size'] = np.shape(list_xdata)
        data_holder.create_group('metadata')
        data_holder.create_group('original_metadata')
        data_holder.create_group('axes')
        data_holder.create_group('attributes')
