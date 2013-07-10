# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 13:14:51 2013

@author: JG
"""

import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from PySide import QtCore
from PySide import QtGui
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import h5py

#project specific items

import analysis
import export 
import color

            
class Tab(QtGui.QWidget):

    def __init__(self,filename, parent=None):
        super(Tab, self).__init__(parent)      
        self.filename = filename
        self.hdf5 = h5py.File(self.filename,'r')    
        self.cube = self.hdf5["cube"]
        self.ycube = self.hdf5["ycube"]
        self.xdata = self.hdf5["xdata"]
        self.make_frame()
 
    
    def make_frame(self):
        self.fig = plt.figure(figsize=(16.0, 6.0))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)            
        self.ax = self.fig.add_subplot(121)
        self.img = self.initialize_image(self.ax, 1)
        self.cbar = plt.colorbar(self.img)
        self.set_color_bar_settings()
        self.ax2 = self.fig.add_subplot(122)        
        self.initialize_graph(self.ax2, 0, 0)

        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        #
        # Layout with box sizers
        left_spacer = QtGui.QWidget()
        left_spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)      
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.set_slider_settings()
        
        self.export_graph_button = QtGui.QPushButton('Export Graph')
        self.export_graph_button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        
        
        
        self.connect_events()
        
        hbox = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)       
        vbox.addWidget(self.canvas)
        hbox.addWidget(left_spacer)
        hbox.addWidget(self.slider)
        vbox.addLayout(hbox)
        vbox.addWidget(self.export_graph_button)

        self.setLayout(vbox)
        #self.setCentralWidget(self.main_frame)

        #self.show_slices()

    def connect_events(self):
        """connect to all the events we need"""
        self.cidpress = self.img.figure.canvas.mpl_connect(
            'button_press_event', self.on_press_image)
        self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'),
                     self.update_image)
        self.cidpick = self.canvas.mpl_connect('pick_event', self.on_pick_color)
        self.connect(self.export_graph_button, QtCore.SIGNAL('clicked()'),
                     self.export_graph)

    def show_ev(self):     
        self.display_ev = True
        self.change_display()
        self.update_image(self.imageval)
        self.canvas.draw()
        
    def show_wavelength(self):      
        self.display_ev = False
        self.change_display()
        self.update_image(self.imageval)
        self.canvas.draw()    
    
    def export_graph(self):
        filename, _ = QtGui.QFileDialog.getSaveFileName()
        print 'saving graph at:', filename
        export.export_graph(self.filename,self.xcoordinate, self.ycoordinate)
        print 'Graph saved'   
        
    def on_press_image(self, event):
        """
        This changes the spec graph to theclicked xy coordinate and moves
        the marker on the image.
        
        The .5 addition in the floor function is there to make xdata print 
        correct coordinates.        
        """
    
        if event.inaxes != self.img.axes: return
    
        contains, attrd = self.img.contains(event)
        if not contains: return

        print 'xcoordinate=%d, ycoordinate=%d'%(event.xdata + .5,
                                                event.ydata + .5)
        self.xcoordinate = np.floor(event.xdata + .5)
        self.ycoordinate = np.floor(event.ydata + .5)
        self.update_graph(self.xcoordinate, self.ycoordinate)
        self.marker.set_xdata(self.xcoordinate)
        self.marker.set_ydata(self.ycoordinate)
        self.img.figure.canvas.draw()
    
    def change_display(self):
        self.ax2.cla()
        if self.display_ev:
            self.img2, = self.ax2.plot(1240/self.xdata[...],
                                      self.ycube[self.ycoordinate,
                                                 self.xcoordinate,:],
                                      '.')
            self.ax2.set_xlabel('ev')
            
        else:
            self.img2, = self.ax2.plot(self.xdata,
                                      self.ycube[self.ycoordinate,
                                                 self.xcoordinate,:],
                                      '.')       
            self.ax2.set_xlabel('$\lambda$ [nm]')
            
    
    
        
    def initialize_graph(self,ax2, xcoordinate, ycoordinate):
        """
        initializes the graph on screen
        xcoordinates and ycoordinates start from 0        
        """
        self.display_ev = False
        self.xcoordinate = xcoordinate
        self.ycoordinate = ycoordinate
        self.currentmaxvalcolor = self.maxval
        self.currentminvalcolor = 0
        self.img2, = ax2.plot(self.xdata,
                                  self.ycube[ycoordinate,xcoordinate,:],'.')
        plt.ylim(ymin=-self.maxval/10, ymax=self.maxval)
        plt.xlabel('$\lambda$ [nm]')
        return ax2        
        
    def initialize_image(self,ax, slice1):
        'Initializes the image from the datacube'
        self.imageval = 800
        self.maxval = analysis.find_maxval(self.ycube[...])
        self.slicedata = self.ycube[:,:,slice1]
        self.img = ax.imshow(self.slicedata, interpolation='nearest',
                              clim = (0,self.maxval))
        self.marker, = ax.plot(0,0,'wo')
        ax.set_title('Current Slice Wavelength:%0.0f '
                           %float(self.xdata[slice1]))
        plt.yticks([])
        plt.xticks([])
        return self.img    
        
    def on_pick_color(self, event):
        """
        Clicking on the color bar will generate three different actions 
        depending on location. The upper third sets the max color value,
        the lower third sets min color value, and the middle pops up a
        window asking for custom values.
        """
        self.val = event.mouseevent.ydata
        self.clicked_number = (self.val*(self.currentmaxvalcolor-self.currentminvalcolor)
                               +self.currentminvalcolor)
        
        if self.val < .33:
            self.currentminvalcolor = self.clicked_number
            self.img.set_clim(vmin=self.clicked_number)
            print 'new min is ', self.currentminvalcolor
    
        elif self.val > .66:
            self.currentmaxvalcolor = self.clicked_number
            self.img.set_clim(vmax=self.clicked_number)
            print 'new max is ', self.currentmaxvalcolor
        else:
            self.colorwindow = color.ColorWindow()
            self.colorwindow.exec_()
            if self.colorwindow.result() and self.colorwindow.maxcolor.text()!='':
                self.currentmaxvalcolor = int(self.colorwindow.maxcolor.text())
                self.img.set_clim(vmax=self.currentmaxvalcolor)
                print 'new max is', self.currentmaxvalcolor
            if self.colorwindow.result() and self.colorwindow.mincolor.text()!='':
                self.currentminvalcolor = int(self.colorwindow.mincolor.text())
                self.img.set_clim(vmin=self.currentminvalcolor)
                print 'new min is', self.currentminvalcolor
            if self.colorwindow.resetvalue:
                self.reset_colors()
        self.canvas.draw()      
        
    
            
    def reset_colors(self):
        self.img.set_clim(0, self.maxval)
        
    
        
    def set_color_bar_settings(self):
        self.currentmaxvalcolor = self.maxval
        self.currentminvalcolor = 0
        self.cbar.ax.set_picker(5) 
        
    def set_slider_settings(self):
        self.slider.setRange(1, 1600)
        self.slider.setValue(800)
        self.slider.setTracking(True)
        
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
        
    
    
    def update_graph(self, xcoordinate, ycoordinate):
        """updates the graph on screen with the given x and y coordinates"""
        self.img2.set_ydata(self.ycube[ycoordinate, xcoordinate,:])
        self.canvas.draw()
    
    def update_image(self, slider_val):
        """updates the image on screen with a new cube slice from slider"""
        self.imageval = slider_val
        if self.display_ev:
            self.slice1 = slider_val
            self.slicedata = self.ycube[:,:,self.slice1]
            self.img.set_array(self.slicedata)
            self.ax.set_title('Current Slice ev:%0.2f'
                                %float(1240/self.xdata[self.slice1]))
        else:
            self.slice1 = 1600-slider_val
            self.slicedata = self.ycube[:,:,self.slice1]
            self.img.set_array(self.slicedata)
            self.ax.set_title('Current Slice Wavelength:%0.0f '
                              %float(self.xdata[self.slice1]))
        self.canvas.draw()     
