# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 17:58:36 2013

@author: JG
"""
import matplotlib
from matplotlib import pyplot as plt
import analysis
import fit_analysis
import numpy as np

def initialize_image(axes, data, data_view):
    image = fit_analysis.get_image_from_data(data, data_view)
    data_view.mincolor = np.amin(image)
    data_view.maxcolor = np.amax(image)
    img = axes.imshow(image, interpolation='nearest')
    plt.yticks([])
    plt.xticks([]) 
    
    return img
    
def plot_image(img, axes, data, data_view):
    image = fit_analysis.get_image_from_data(data, data_view)
    img.set_array(image)
    data_view.mincolor = np.amin(image)
    data_view.maxcolor = np.amax(image)
    img.set_clim(data_view.mincolor, data_view.maxcolor)
    img.figure.canvas.draw()
    
def plot_residuals(img, axes, data, data_view):
    image = data.integrated_residuals
    img.set_array(image)
    data_view.mincolor = np.amin(image)
    data_view.maxcolor = np.amax(image)
    img.set_clim(data_view.mincolor, data_view.maxcolor)
    img.figure.canvas.draw()
    
