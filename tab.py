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
import data_view
import plot_tools

            
class Tab(QtGui.QWidget):

    def __init__(self,filename, parent=None):
        super(Tab, self).__init__(parent)      
        self.filename = filename
        self.hdf5 = h5py.File(self.filename,'r')    
        self.cube = self.hdf5["cube"]
        self.ycube = self.hdf5["ycube"]
        self.xdata = self.hdf5["xdata"]
        self.maxval = analysis.find_maxval(self.ycube[...])
        self.press = False
        self.make_frame()
 
    
    def make_frame(self):
        self.fig = plt.figure(figsize=(16.0, 6.0))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)            
        self.img_axes = self.fig.add_subplot(121)
        self.img = plot_tools.initialize_image(self.img_axes, ycube=self.ycube, 
                                               xdata=self.xdata, slice1=1,
                                               maxval=self.maxval)
        self.marker, = self.img_axes.plot(0,0,'wo')
        self.cbar = plt.colorbar(self.img)
        self.set_color_bar_settings()
        self.graph_axes = self.fig.add_subplot(122)        
        self.img2 = plot_tools.initialize_graph(self.graph_axes, self.ycube,
                                                self.xdata, self.maxval)

        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        #
        # Layout with box sizers
        left_spacer = QtGui.QWidget()
        left_spacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                  QtGui.QSizePolicy.Expanding)      
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.set_slider_settings()
        
        self.export_graph_button = QtGui.QPushButton('Export Graph')
        self.export_graph_button.setSizePolicy(QtGui.QSizePolicy.Fixed, 
                                               QtGui.QSizePolicy.Fixed)
        
        
        
        
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
        self.data_view = data_view.DataView(maxval=self.maxval)


    def change_display(self):
        self.graph_axes.cla()
        if self.data_view.display_ev:
            self.img2, = self.graph_axes.plot(1240/self.xdata[...],
                                      self.ycube[self.data_view.ycoordinate,
                                                 self.data_view.xcoordinate,:],
                                      '.')
            self.graph_axes.set_xlabel('ev')
            
        else:
            self.img2, = self.graph_axes.plot(self.xdata[...],
                                      self.ycube[self.data_view.ycoordinate,
                                                 self.data_view.xcoordinate,:],
                                      '.')       
            self.graph_axes.set_xlabel('$\lambda$ [nm]')
            
    def connect_events(self):
        """connect to all the events we need"""
        self.cidpress = self.img.figure.canvas.mpl_connect(
            'button_press_event', self.on_press_image)
        self.cidpress2 = self.img.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)
        self.cidpress3 = self.img.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'),
                     self.update_image_from_slider)
        self.cidpick = self.canvas.mpl_connect('pick_event',
                                               self.on_pick_color)
        self.connect(self.export_graph_button, QtCore.SIGNAL('clicked()'),
                     self.export_graph)
                     
    def export_graph(self):
        folder, _ = QtGui.QFileDialog.getExistingDirectory()
        filename = os.path.join(folder,)
        print 'saving graph at:', folder
        export.export_graph(self.filename,filename, self.xcoordinate,
                            self.ycoordinate)
        print 'Graph saved'  
        
    def on_motion(self, event):        
        """
        dragging the marker will change the graph.
        """
        if self.press is False: return
        if event.inaxes != self.img.axes: return  
        
        self.data_view.xcoordinate = np.floor(event.xdata + .5)
        self.data_view.ycoordinate = np.floor(event.ydata + .5)
        self.update_graph()

        
    def on_pick_color(self, event):
        """
        Clicking on the color bar will generate three different actions 
        depending on location. The upper third sets the max color value,
        the lower third sets min color value, and the middle pops up a
        window asking for custom values.
        """
        self.val = event.mouseevent.ydata
        self.clicked_number = (self.val*(self.currentmaxvalcolor
                                         -self.currentminvalcolor)
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
        self.data_view.xcoordinate = np.floor(event.xdata + .5)
        self.data_view.ycoordinate = np.floor(event.ydata + .5)
        self.marker.set_xdata(self.data_view.xcoordinate)
        self.marker.set_ydata(self.data_view.ycoordinate)
        self.press = True 
        self.update_graph()


    def on_release(self, event):
        'on release we reset the press data'
        self.press = False
            
    def reset_colors(self):
        self.img.set_clim(0, self.maxval)
        self.data_view.currentmaxvalcolor = self.maxval
        print 'new max is', self.currentmaxvalcolor
        self.data_view.currentminvalcolor = 0
        print 'new min is', self.currentminvalcolor               
                
    def set_color_bar_settings(self):
        self.currentmaxvalcolor = self.maxval
        self.currentminvalcolor = 0
        self.cbar.ax.set_picker(5) 
        
    def set_slider_settings(self):
        self.slider.setRange(1, 1600)
        self.slider.setValue(800)
        self.slider.setTracking(True)
        
    def show_ev(self):     
        self.data_view.display_ev = True
        self.change_display()
        plot_tools.plot_image(self.img, self.img_axes, self.ycube, self.xdata,
                              self.data_view)
       
    def show_wavelength(self):      
        self.data_view.display_ev = False
        self.change_display()
        plot_tools.plot_image(self.img, self.img_axes, self.ycube, self.xdata,
                              self.data_view)

    def update_graph(self):
        plot_tools.plot_graph(self.img2, self.graph_axes, self.ycube,
                              self.xdata, self.data_view)
        self.marker.set_xdata(self.data_view.xcoordinate)
        self.marker.set_ydata(self.data_view.ycoordinate)
        
    def update_image_from_slider(self, sliderval):
        self.data_view.slider_val = sliderval
        plot_tools.plot_image(self.img, self.img_axes, self.ycube, self.xdata,
                              self.data_view)

    
