# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 13:23:38 2013

@author: JG
"""
import os
import numpy as np
import h5py
import shutil


class Mf1Converter():
    """
    Reads the Mf1 File and builds a Data Cube from the intensities,
    xdata (wavelengths) for graph and optionally info for comments.
    """
    
    def __init__(self, input_filename, output_filename, dimension1, dimension2, 
                 global_bool, progress_bar):
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.dimension1 = dimension1
        self.dimension2 = dimension2
        self.global_bool = global_bool
        self.progress_bar = progress_bar
        #read the file
        self.datasize = self.datasize_finder()
        self.output_file = h5py.File(self.output_filename,'w')
        experiments = self.output_file.create_group("Experiments") 
        self.data_holder = experiments.create_group("__unnamed__")
        with open(self.input_filename,'rb') as fid:
            self.text_header=fid.read(2048)
            self.temporary = h5py.File(self.output_filename+'temporary',
                                       'w')
            self.read_into_cube(fid)
        #if not self.check_dimensions():
            #self.fix_dimensions()
        
        self.build_xdata()
        #self.info = self.build_info()
        self.build_ycube()
        self.write_header()            
        self.output_file.close()
        self.temporary.close()
        os.remove(self.output_filename+'temporary')
   
        
    def datasize_finder(self):
        'finds the data size in the mf1 file'
        fileinfo=os.stat(self.input_filename)
        #subtract header size from total data size and divide by size of 
        #spectrum and comments
        if self.global_bool:
            datasize = (fileinfo.st_size-2048-4*1600)/(4*3200+256)
        else:
            datasize = (fileinfo.st_size-2048)/(4*3200+256)

        return datasize
      
    def check_dimensions(self):
        'checks if we can make a cube from the data'
        if self.dimension1*self.dimension2 != self.datasize:
            return False
        else:
            return True
        
    def build_xdata(self):
        """
        builds the wavelength data (x data for graph). 
        """
        if self.global_bool:
            self.xdata = self.data_holder.create_dataset('xdata', data=self.xdata ) 
        else:
            self.xdata = self.data_holder.create_dataset('xdata',
                                                  data=self.temporary["cube"][0,0,0:1600])
        
    def build_ycube(self):
        """
        builds a 3 dimensional array with intensity data
        """

        if self.global_bool:
            self.ycube = self.data_holder.create_dataset('data',
                                                  data=self.temporary["cube"][:,:,0:1600])
        else:
            self.ycube = self.data_holder.create_dataset('data', 
                                                  data=self.temporary["cube"][:,:,1600:3200])

        
    def build_info(self):
        """
        optional info for each graph. not utilized yet. This may also
        be outdated for displaying the info.
        """
        if self.global_bool:
            info = self.graph_array[:,1600:1664]
        else:
            info = self.graph_array[:,3200:3264]
        info = info.transpose()
        return info
        
    def read_into_cube(self,fid):
        

        
        if self.global_bool:
            cube = self.temporary.create_dataset('cube',
                                                 (self.dimension1,
                                                  self.dimension2, 1664))

            self.xdata = np.fromfile(file=fid, dtype='>f', count=1600)
            
            for i in np.arange(self.dimension1):
                for j in np.arange(self.dimension2):
                    try:
                        cube[i,j,:] = np.fromfile(file=fid, dtype='>f', count=1664)
                    except:
                        return
                    current_spectrum = i*self.dimension2 + j
                    self.progress_bar.setValue(current_spectrum)
        else:
            cube = self.temporary.create_dataset('cube',(self.dimension1,self.dimension2, 3264))  
            for i in np.arange(self.dimension1):
                for j in np.arange(self.dimension2):
                    try:
                        cube[i,j,:] = np.fromfile(file=fid, dtype='>f', count=3264)
                    except:
                        return
                    current_spectrum = i*self.dimension2 + j
                    self.progress_bar.setValue(current_spectrum)
    def write_header(self):
        self.data_holder.attrs['header'] = self.text_header
        