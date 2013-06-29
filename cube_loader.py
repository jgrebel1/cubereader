# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 13:23:38 2013

@author: JG
"""
import os
import numpy as np

class Mf1File:
    """
    Reads the Mf1 File and builds a Data Cube from the intensities,
    xdata (wavelengths) for graph and optionally info for comments.
    """
    
    def __init__(self, filename, dimension1, dimension2, global_bool):
        self.filename = filename
        self.dimension1 = dimension1
        self.dimension2 = dimension2
        self.global_bool = global_bool

        #read the file
        self.datasize = self.datasize_finder()
        
        with open(self.filename,'rb') as fid:
            self.text_header=fid.read(2048)
            self.read_into_graph(fid)
        if not self.check_dimensions():
            self.fix_dimensions()

        self.xcube = self.build_xcube()
        self.info = self.build_info()
        self.ycube = self.build_ycube()        
        self.maxval = self.find_maxval()
     
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

    def read_into_graph(self,fid):
        """
        Reads the Binary data into an array. This does not work for large files.
        """
        if self.global_bool:
            self.xdata = np.fromfile(file=fid, dtype='>f', count=1600)
            self.graph_array = np.empty((self.dimension1*self.dimension2,1664))
            for i in np.arange(self.dimension1*self.dimension2):
                self.graph_array[i] = np.fromfile(file=fid, dtype='>f', count=1664)
        else:
            self.graph_array = np.empty((self.dimension1*self.dimension2,3264))
            for i in np.arange(self.dimension1*self.dimension2):
                self.graph_array[i] = np.fromfile(file=fid, dtype='>f', count=3264)
      
    def check_dimensions(self):
        'checks if we can make a cube from the data'
        if self.dimension1*self.dimension2 != self.datasize:
            return False
        else:
            return True
            
    def fix_dimensions(self):
        """
        fills in zeros for the missing spectra to make the dimensions 
        correspond to the data size
        """
        missingspectra = self.dimension1*self.dimension2-self.datasize
        if self.global_bool:
            for i in np.arange(self.datasize,self.dimension1*self.dimension2):
                self.graph_array[i] = np.repeat(0,1664)
        else:
            for i in np.arange(self.datasize,self.dimension1*self.dimension2):
                self.graph_array[i] = np.repeat(0,3264)
        print 'filled in', missingspectra, 'missing spectra as zeros'
        
    def find_maxval(self):
        maxval = np.amax(self.ycube)
        return maxval
        
    def build_xcube(self):
        """
        builds the wavelength data (x data for graph). 
        """
        if self.global_bool:
            xarray = np.empty((self.dimension1*self.dimension2,1600))
            for i in np.arange(self.dimension1*self.dimension2):
                xarray[i] = self.xdata
        else:
            xarray = self.graph_array[:,0:1600]
        xarray = xarray.transpose()
        xarray = xarray.reshape((1600,self.dimension1,self.dimension2))
        return xarray
        
    def build_ycube(self):
        """
        builds a 3 dimensional array with intensity data
        """
        if self.global_bool:
            ydata = self.graph_array[:,0:1600]
        else:
            ydata = self.graph_array[:,1600:3200]
        ydata = ydata.transpose()
        ycube = ydata.reshape((1600,self.dimension1,self.dimension2))
        return ycube
        
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
  