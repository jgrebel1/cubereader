# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 19:44:34 2013

@author: JG
"""
import matplotlib
from matplotlib import pyplot as plt
import analysis


def change_display(axes, data, data_view):
    """
    changes the view between ev and wavelength for ev and wavelength data
    """
    axes.cla()
    xdata = analysis.xdata_calc(data, data_view)
    ydata = analysis.ydata_calc(data, data_view)
    img2, = axes.plot(xdata,ydata,'.')      
    if data_view.display_ev:
        axes.set_xlabel('ev')        
    else:
        axes.set_xlabel('$\lambda$ [nm]')
    
    return img2

def initialize_graph(axes, data, data_view, maxval):
    """
    initializes the graph on screen
    xcoordinates and ycoordinates start from 0        
    """
    axes.cla()
    xdata = analysis.xdata_calc(data, data_view)
    ydata = analysis.ydata_calc(data, data_view)
    
    #scale maxval so data fits on screen. 600 is arbitrary
    scale_factor = 600
    if data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        maxval = maxval
    if data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        maxval = maxval*scale_factor
    if not data_view.display_ev and data.xdata_info['data_type'] == 'ev':
        maxval = maxval/scale_factor
    if not data_view.display_ev and data.xdata_info['data_type'] == 'wavelength':
        maxval = maxval
        
    axes.set_ylim((-maxval/10,maxval))    
    img2, = axes.plot(xdata, ydata,'.')

    if data_view.display_ev:
        plt.xlabel('ev')
    else:
        plt.xlabel('$\lambda$ [nm]')       
    return img2

def initialize_image(axes, data, data_view, slice1, maxval):
    'Initializes the image from the datacube'
   
    slicedata = data.ycube[:,:,slice1]
    img = axes.imshow(slicedata, interpolation='nearest',
                          clim = (0,maxval))
    
    xdata = analysis.xdata_calc(data, data_view)
    if data_view.display_ev:
        axes.set_title('Current Slice ev:%0.2f'%float(xdata[slice1]))
    else:
        axes.set_title('Current Slice Wavelength:%0.2f'%float(xdata[slice1]))
    plt.yticks([])
    plt.xticks([]) 
    return img
    
def plot_graph(img, axes, data, data_view):
    """updates the graph on screen with the given x and y coordinates"""
    ydata = analysis.ydata_calc(data, data_view)    
    img.set_ydata(ydata)
    img.figure.canvas.draw()
    
def plot_image(img, axes, data, data_view):
    """updates the image on screen with a new cube slice from slider"""
    slice1 = data_view.slider_val
    slicedata = data.ycube[:,:,slice1]
    img.set_array(slicedata)
    img.set_clim(vmax=data_view.currentmaxvalcolor,
                 vmin=data_view.currentminvalcolor)
    xdata = analysis.xdata_calc(data, data_view)    
    if data_view.display_ev:
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
    

