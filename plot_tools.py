# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 19:44:34 2013

@author: JG
"""
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import analysis

def plot_pyqt(imv, data, dataview):
    yimage = analysis.yimage_calc(data, dataview)
    yimage = np.rot90(yimage, 1)
    imv.setImage(yimage)
    
def graph_pyqt(curve1, curve2, data, dataview):
    xdata = analysis.xdata_calc(data, dataview)
    ydata = analysis.ydata_calc(data, dataview)    
    curve1.setData(ydata, pen="w")
    curve2.setData(ydata, pen="w")
    
def change_display(axes, data, dataview):
    """
    changes the view between ev and wavelength for ev and wavelength data
    """
    axes.cla()
    xdata = analysis.xdata_calc(data, dataview)
    ydata = analysis.ydata_calc(data, dataview)
    img2, = axes.plot(xdata,ydata,'.')      
    if dataview.display_ev:
        axes.set_xlabel('ev')        
    else:
        axes.set_xlabel('$\lambda$ [nm]')
    
    return img2

def initialize_graph(axes, data, dataview):
    """
    initializes the graph on screen
    xs and ys start from 0        
    """
    axes.cla()
    xdata = analysis.xdata_calc(data, dataview)
    ydata = analysis.ydata_calc(data, dataview)    
    maxval = analysis.maxval_calc(data, dataview)
        
    axes.set_ylim((-maxval/10,maxval))    
    img2, = axes.plot(xdata, ydata,'.')

    if dataview.display_ev:
        plt.xlabel('ev')
    else:
        plt.xlabel('$\lambda$ [nm]')  
        
    return img2

def initialize_image(axes, data, dataview):
    'Initializes the image from the datacube'
   
    yimage = analysis.yimage_calc(data, dataview)
    maxval = analysis.maxval_calc(data, dataview)
    
    img = axes.imshow(yimage, interpolation='nearest', clim = (0,maxval),
                      cmap='spectral')
    
    xdata = analysis.xdata_calc(data, dataview)
    slice1 = dataview.slider_val
    if dataview.display_ev:
        axes.set_title('Current Slice ev:%0.2f'%float(xdata[slice1]))
    else:
        axes.set_title('Current Slice Wavelength:%0.2f'%float(xdata[slice1]))
        
    plt.yticks([])
    plt.xticks([]) 
    
    return img
    
def plot_graph(img, axes, data, dataview):
    """updates the graph on screen with the given x and y coordinates"""
    ydata = analysis.ydata_calc(data, dataview)    
    img.set_ydata(ydata)
    img.figure.canvas.draw()
    
def plot_image(img, axes, data, dataview):
    """updates the image on screen with a new cube slice from slider"""
    yimage = analysis.yimage_calc(data, dataview)
    img.set_array(yimage)
    max_color, min_color = analysis.colors_calc(data, dataview)
    if dataview.auto_color:
        img.autoscale()
        vmin, vmax = img.get_clim()
        dataview.mincolor = vmin
        dataview.maxcolor = vmax
    else:
        img.set_clim(vmax=max_color, vmin=min_color)                
    xdata = analysis.xdata_calc(data, dataview)    
    slice1 = dataview.slider_val
    if dataview.display_ev:
        axes.set_title('Current Slice ev:%0.2f'%float(xdata[slice1]))
    else:
        axes.set_title('Current Slice Wavelength:%0.0f '%float(xdata[slice1]))
        
    img.figure.canvas.draw()
     
        
def show_slices(self,N=100,axis=0):
    """
    Remnant of Aaron's original code. I need to update this for the
    new version.
    show N slices out of a data cube. N square root must be an integer
    """      
    
    self.slices = QtGui.QWidget()
    
    self.slices.fig = plt.figure(figsize=(8.0, 6.0))
    self.slices.canvas = FigureCanvas(self.slices.fig)
    self.slices.canvas.setParent(self.slices) 
    
    dE = 1600/N
    inds = np.r_[0:dE]
    m = self.maxval*(N/16)
    NN = np.floor(np.sqrt(N))
    for i in np.arange(0,N):
        plt.subplot(NN,NN,i+1)
        plt.imshow(np.sum(self.ycube[i*dE + inds,:],axis=0),
                   interpolation='nearest'  )
        #plt.title('%0.0f to %0.0f nm'%tuple(self.mf1.xdata[np.r_[i*dE + inds][[0,-1]],1,1].tolist()))
        #plt.colorbar()
        plt.yticks([])
        plt.xticks([])
        plt.clim(0,m)

    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(self.slices.canvas)
    self.slices.setLayout(vbox)

    self.slices.show()
    

