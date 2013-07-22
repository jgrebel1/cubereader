# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 13:23:38 2013

@author: JG
"""
import os
import numpy as np
import h5py


class Mf1File():
    """
    Reads the Mf1 File and builds a Data Cube from the intensities,
    xdata (wavelengths) for graph and optionally info for comments.
    """
    
    def __init__(self, filename, hdf5_filename, dimension1, dimension2, 
                 global_bool):
        self.filename = filename
        self.hdf5_filename = hdf5_filename
        self.dimension1 = dimension1
        self.dimension2 = dimension2
        self.global_bool = global_bool

        #read the file
        self.datasize = self.datasize_finder()
        
        with open(self.filename,'rb') as fid:
            self.text_header=fid.read(2048)
            self.data = h5py.File(self.hdf5_filename,'w', userblock_size=2048)
            self.read_into_cube(fid)
        #if not self.check_dimensions():
            #self.fix_dimensions()
        
        self.build_xdata()
        #self.info = self.build_info()
        self.build_ycube()
        
        self.data.close()
        self.write_header()        
        
    def datasize_finder(self):
        'finds the data size in the mf1 file'
        fileinfo=os.stat(self.filename)
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
            self.xdata = self.data.create_dataset('xdata', data=self.xdata ) 
        else:
            self.xdata = self.data.create_dataset('xdata',
                                                  data=self.data["cube"][0,0,0:1600])
        
    def build_ycube(self):
        """
        builds a 3 dimensional array with intensity data
        """

        if self.global_bool:
            self.ycube = self.data.create_dataset('ycube',
                                                  data=self.data["cube"][:,:,0:1600])
        else:
            self.ycube = self.data.create_dataset('ycube', 
                                                  data=self.data["cube"][:,:,1600:3200])

        
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
            cube = self.data.create_dataset('cube',
                                            (self.dimension1,
                                             self.dimension2, 1664))

            self.xdata = np.fromfile(file=fid, dtype='>f', count=1600)
            
            for i in np.arange(self.dimension1):
                for j in np.arange(self.dimension2):
                    try:
                        cube[i,j,:] = np.fromfile(file=fid, dtype='>f', count=1664)
                    except:
                        return
        else:
            cube = self.data.create_dataset('cube',(self.dimension1,self.dimension2, 3264))  
            for i in np.arange(self.dimension1):
                for j in np.arange(self.dimension2):
                    try:
                        cube[i,j,:] = np.fromfile(file=fid, dtype='>f', count=3264)
                    except:
                        return
    def write_header(self):
        """
        HDF5 only supports writing the userblock after you close a file.
        this writes in the header from the mf1 file to the new HDF5 file.
        """
        f = file(self.hdf5_filename, 'r+b')
        f.seek(0,0)
        f.write(self.text_header)
        f.close()