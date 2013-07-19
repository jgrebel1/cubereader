# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 19:44:34 2013

@author: JG
"""
import matplotlib
from matplotlib import pyplot as plt


def initialize_graph(axes, ycube, xdata, maxval):
    """
    initializes the graph on screen
    xcoordinates and ycoordinates start from 0        
    """
    img2, = axes.plot(xdata[...], ycube[0,0,:],'.')
    plt.ylim(ymin=-maxval/10, ymax=maxval)
    plt.xlabel('$\lambda$ [nm]')
    return img2

def initialize_image(axes, ycube, xdata, slice1, maxval):
    'Initializes the image from the datacube'
   
    slicedata = ycube[:,:,slice1]
    img = axes.imshow(slicedata, interpolation='nearest',
                          clim = (0,maxval))

    axes.set_title('Current Slice Wavelength:%0.0f '
                       %float(xdata[slice1]))
    plt.yticks([])
    plt.xticks([]) 
    return img
    
   
        
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
    
def plot_graph(img, axes, ycube, xdata, data_view):
    """updates the graph on screen with the given x and y coordinates"""
    img.set_ydata(ycube[data_view.ycoordinate, data_view.xcoordinate,:])
    img.figure.canvas.draw()
    
def plot_image(img, axes, ycube, xdata, data_view):
    """updates the image on screen with a new cube slice from slider"""
    if data_view.display_ev:
        slice1 = data_view.slider_val
        slicedata = ycube[:,:,slice1]
        img.set_array(slicedata)
        axes.set_title('Current Slice ev:%0.2f'
                            %float(1240/xdata[slice1]))
    else:
        slice1 = 1600-data_view.slider_val
        slicedata = ycube[:,:,slice1]
        img.set_array(slicedata)
        axes.set_title('Current Slice Wavelength:%0.0f '
                          %float(xdata[slice1]))
    img.set_clim(vmax=data_view.currentmaxvalcolor,
                 vmin=data_view.currentminvalcolor)
    img.figure.canvas.draw()
  