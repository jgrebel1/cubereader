# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 13:23:38 2013

@author: JG
"""
import os
import numpy as np
import re

class Mf1File:
    """
    Reads the Mf1 File and builds a Data Cube from the intensities,
    xdata (wavelengths) for graph and optionally info for comments.
    
    This is for non-global wavelength files
    """
    
    def __init__(self, filename, dimension1 = 0, dimension2 = 0):
        self.filename = filename
        print('Reading file: %s'%self.filename)
        #read the file
        self.datasize = self.datasize_finder()
        with open(self.filename,'rb') as fid:
            self.text_header=fid.read(2048)
            print self.text_header
            if dimension1==0 and dimension2==0:
                self.dimension1, self.dimension2 = self.dimension_finder()
            else:
                self.dimension1, self.dimension2 = dimension1, dimension2
            self.read_into_graphs(fid)
        if not self.check_dimensions():
            self.fix_dimensions()

        self.xcube = self.build_xcube()
        self.info = self.build_info()
        self.maxval = self.find_maxval()
        self.ycube = self.build_ycube()
        #self.xdata_ev = 1240/self.xdata
        
        #I think this following code block is for testing, but I'll keep it here 
        #just in case it's important
        
        #plt.figure()
        #if np.shape(mf1.xdata)[0]>10:
            #plt.plot(mf1.xdata[:,0:10],mf1.ydata[:,0:10]+np.cumsum(np.r_[0,np.repeat(np.amax(mf1.ydata[:,0:10]),np.shape(mf1.ydata[:,0:10])[1]-1)]),'.')
        #else:
            #plt.plot(mf1.xdata,mf1.ydata+np.cumsum(np.r_[0,np.repeat(np.amax(mf1.ydata),np.shape(mf1.ydata)[1]-1)]),'.')

        #plt.yticks([])
        #plt.xlabel('$\lambda$ [nm]')
        #plt.title(mf1.fname)
        #plt.close()
        
    def datasize_finder(self):
        'finds the data size in the mf1 file'
        fileinfo=os.stat(self.filename)
        #subtract header size from total data size and divide by size of 
        #spectrum and comments
        datasize = (fileinfo.st_size-2048)/(4*3200+256)
        return datasize
  
    def dimension_finder(self):
        """finds the picture dimension"""
        dimension = re.search('\d+x\d+',self.text_header).group()
        dimension1 = re.findall('\d+',dimension)[0]
        dimension1 = float(dimension1)
        dimension2 = re.findall('\d+',dimension)[1]
        dimension2 = float(dimension2)
        return (dimension1,dimension2)
        
    def read_into_graphs(self,fid):
        """
        Reads the Binary data into an array. This does not work for large files.
        """
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

        for i in np.arange(self.datasize,self.dimension1*self.dimension2):
             self.graph_array[i] = np.repeat(0,3264)
        print 'filled in', missingspectra, 'missing spectra as zeros'
        
    def find_maxval(self):
        maxval = np.amax(self.ydata)
        return maxval
        
    def build_xcube(self):
        """
        builds the wavelength data (x data for graph). 
        """
        xdata = self.graph_array[:,0:1600]
        xdata = xdata.transpose()
        xdata = xdata.reshape((1600,self.dimension1,self.dimension2))
        return xdata
        
    def build_ycube(self):
        """
        builds a 3 dimensional array with intensity data
        """

        ydata = self.graph_array[:,1600:3200]
        ydata = ydata.transpose()
        ycube = self.ydata.reshape((1600,self.dimension1,self.dimension2))
        return ycube
        
    def build_info(self):
        """
        optional info for each graph. not utilized yet. This may also
        be outdated for displaying the info.
        """
        info = self.graph_array[:,3200:3264]
        info = info.transpose()
        return info
  