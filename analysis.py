# -*- coding: utf-8 -*-
"""
Created on Mon Jul 01 13:57:51 2013

@author: JG
"""
import os
import numpy as np

def find_maxval(dataset):
    maxval = 0
    for i in dataset:
        if np.amax(i) > maxval:
            maxval = np.amax(i)
    return maxval
    
def get_file_basename(path_name):
    filename, extension = os.path.splitext(path_name)
    basename = os.path.basename(filename)
    return basename