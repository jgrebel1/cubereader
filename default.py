# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 16:52:51 2013

@author: JG
"""
import re

class DefaultValues():
    """
    takes file input and returns information found
    in header
    """
    def __init__(self, filename):
        self.filename = filename
        with open(filename,'rb') as fid:
            self.text_header=fid.read(2048)
            
    def default_dimensions(self):
        """
        Look for picture dimensions in file. If not found return 0 for 
        each dimension.
        """
        try:
            dimension1, dimension2 = self.dimension_finder(self.text_header)
        except:
            dimension1, dimension2 = 0,0
        return (dimension1, dimension2)
    
    def default_global(self):
        """
        look for words global wavelength in file. If not found, return False
        """
        try:
            re.search('global wavelength',self.text_header).group()
            global_wavelength = True
        except:
            global_wavelength = False
        return global_wavelength
                
    def dimension_finder(self, text_header):
        """finds the picture dimension in a text header"""
        dimension = re.search('\d+x\d+',text_header).group()
        dimension1 = re.findall('\d+',dimension)[0]
        dimension1 = float(dimension1)
        dimension2 = re.findall('\d+',dimension)[1]
        dimension2 = float(dimension2)
        return (dimension1,dimension2)
