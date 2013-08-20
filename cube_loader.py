# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 13:23:38 2013

@author: JG

This file is not in use anymore by CubeReader. I integrated its contents
with convert_file so that the progress bar works.
"""
import os
import numpy as np
import h5py
import shutil


def convert_mf1(input_filename, output_filename, dimension1, dimension2,
                global_bool, progress_bar):
    """
    Reads the Mf1 File and builds a Data Cube from the intensities,
    xdata (wavelengths) for graph and optionally info for comments.
    """
    #read the file
    datasize = datasize_finder(input_filename, global_bool)

    with open(input_filename,'rb') as fid:
        header=fid.read(2048)
        temp_hdf5 = h5py.File(output_filename+'temporary','w')
        list_xdata = read_into_cube(fid, temp_hdf5, global_bool, dimension1,
                                    dimension2, progress_bar)
    generate_output(output_filename, temp_hdf5, global_bool, header,
                    list_xdata)
    temp_hdf5.close()
    os.remove(output_filename+'temporary')
   
def build_xdata(data_holder, temp_hdf5, global_bool, list_xdata):
    """
    builds the wavelength data (x data for graph). 
    """
    if global_bool:
        data_holder.create_dataset('xdata', data=self.list_xdata ) 
    else:
        data_holder.create_dataset('xdata',
                                   data=temp_hdf5["cube"][0,0,0:1600])
    
def build_ycube(data_holder, temp_hdf5, global_bool):
    """
    builds a 3 dimensional array with intensity data
    """

    if global_bool:
        data_holder.create_dataset('data',
                                   data=temp_hdf5["cube"][:,:,0:1600])
    else:
        data_holder.create_dataset('data', 
                                   data=temp_hdf5["cube"][:,:,1600:3200])
    
def build_info():
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
    
def datasize_finder(input_filename, global_bool):
    'finds the data size in the mf1 file'
    fileinfo=os.stat(input_filename)
    #subtract header size from total data size and divide by size of 
    #spectrum and comments
    if global_bool:
        datasize = (fileinfo.st_size-2048-4*1600)/(4*3200+256)
    else:
        datasize = (fileinfo.st_size-2048)/(4*3200+256)
    return datasize
    
def generate_output(output_filename, temp_hdf5, global_bool, header,
                    list_xdata):
    output_file = h5py.File(output_filename,'w')
    data_holder = output_file.create_group("Experiments/__unnamed__")         
    build_xdata(data_holder, temp_hdf5, global_bool, list_xdata)
    #self.info = self.build_info()
    build_ycube(data_holder, temp_hdf5, global_bool)
    write_header(data_holder, header)            
    output_file.close()
          
def read_into_cube(fid, temp_hdf5, global_bool,
                   dimension1, dimension2, progress_bar):         
    if global_bool:
        cube = temp_hdf5.create_dataset('cube',
                                             (dimension1,
                                              dimension2, 1664))

        list_xdata = np.fromfile(file=fid, dtype='>f', count=1600)
        
        for i in np.arange(dimension1):
            for j in np.arange(dimension2):
                try:
                    cube[i,j,:] = np.fromfile(file=fid,
                                              dtype='>f', count=1664)
                except:
                    return
                current_spectrum = i*dimension2 + j
                progress_bar.setValue(current_spectrum)
    else:
        cube = temp_hdf5.create_dataset('cube',(dimension1,
                                                dimension2,
                                                3264))  
        for i in np.arange(dimension1):
            for j in np.arange(dimension2):
                try:
                    cube[i,j,:] = np.fromfile(file=fid, dtype='>f',
                                              count=3264)
                except:
                    return
                current_spectrum = i*dimension2 + j
                progress_bar.setValue(current_spectrum)
    return list_xdata
                
def write_header(data_holder, header):
    data_holder.attrs['header'] = header
    