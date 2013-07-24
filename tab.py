# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 13:14:51 2013

@author: JG
"""

import os
os.environ['ETS_TOOLKIT'] = 'qt4'
from pyface.qt import QtGui, QtCore
from traits.api import HasTraits, Instance, on_trait_change, \
    Int, Dict
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
        SceneEditor

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
import wraith_for_mf1read
import visualization
import peak_bank

plt.ioff()
            
class Tab(QtGui.QWidget):

    def __init__(self,filename, parent=None):
        super(Tab, self).__init__(parent)      
        self.filename = filename
        print self.filename
        self.hdf5 = h5py.File(self.filename,'r')    
        self.cube = self.hdf5["cube"]
        self.ycube = self.hdf5["ycube"]
        self.xdata = self.hdf5["xdata"]
        self.maxval = analysis.find_maxval(self.ycube[...])
        self.press = False
        self.peak_bank = peak_bank.PeakBank()
        self.make_frame()
 
    
    def make_frame(self):
        
        self.data_view = data_view.DataView(maxval=self.maxval)
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
        
        self.wraith = QtGui.QPushButton('Open Wraith for Current Graph')
        self.wraith.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                  QtGui.QSizePolicy.Fixed)
        
        self.visualization = QtGui.QPushButton('Open Visualization')
        self.visualization.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                         QtGui.QSizePolicy.Fixed)
        self.visualization_min_color_label = QtGui.QLabel('Min Color:')
        self.visualization_min_color_textbox = QtGui.QLineEdit(str(self.data_view.visualization_min_color))
        self.connect(self.visualization_min_color_textbox, 
                     QtCore.SIGNAL('editingFinished ()'), 
                     self.update_visualization_settings)
        self.visualization_max_color_label = QtGui.QLabel('Max Color:')
        self.visualization_max_color_textbox = QtGui.QLineEdit(str(self.data_view.visualization_max_color))
        self.connect(self.visualization_max_color_textbox, 
                     QtCore.SIGNAL('editingFinished ()'), 
                     self.update_visualization_settings)
        self.visualization_min_slice_label = QtGui.QLabel('Min Wavelength:')
        self.visualization_min_slice_textbox = QtGui.QLineEdit(str(self.xdata[-1]))
        self.connect(self.visualization_min_slice_textbox, 
                     QtCore.SIGNAL('editingFinished ()'), 
                     self.update_visualization_settings)
        self.visualization_max_slice_label = QtGui.QLabel('Max Wavelength:')
        self.visualization_max_slice_textbox = QtGui.QLineEdit(str(self.xdata[0]))
        self.connect(self.visualization_max_slice_textbox, 
                     QtCore.SIGNAL('editingFinished ()'), 
                     self.update_visualization_settings)
                             
        self.connect_events()
        
        hbox = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)       
        vbox.addWidget(self.canvas)
        hbox.addWidget(left_spacer)
        hbox.addWidget(self.slider)
        vbox.addLayout(hbox)
        vbox.addWidget(self.export_graph_button)
        vbox.addWidget(self.wraith)
        visualization_hbox = QtGui.QHBoxLayout()
        visualization_hbox.addStretch(1)
        visualization_hbox.setDirection(QtGui.QBoxLayout.LeftToRight)
        visualization_hbox.addWidget(self.visualization)
        visualization_hbox.addWidget(self.visualization_min_color_label)
        visualization_hbox.addWidget(self.visualization_min_color_textbox)
        visualization_hbox.addWidget(self.visualization_max_color_label)
        visualization_hbox.addWidget(self.visualization_max_color_textbox)
        visualization_hbox.addWidget(self.visualization_min_slice_label)
        visualization_hbox.addWidget(self.visualization_min_slice_textbox)
        visualization_hbox.addWidget(self.visualization_max_slice_label)
        visualization_hbox.addWidget(self.visualization_max_slice_textbox)
        vbox.addLayout(visualization_hbox)

        self.setLayout(vbox)
        


    def change_display(self):
        """
        changes the view between ev and wavelength
        """
        self. img2 = plot_tools.change_display(self.graph_axes, self.ycube, self.xdata,
                                  self.data_view)
        if self.data_view.display_ev:
            self.visualization_min_slice_label.setText('Min ev:')
            self.visualization_min_slice_textbox.setText(str(1240/self.xdata[self.data_view.visualization_max_slice]))
            self.visualization_max_slice_label.setText('Max ev:')
            self.visualization_max_slice_textbox.setText(str(1240/self.xdata[self.data_view.visualization_min_slice]))
        else:
            self.visualization_min_slice_label.setText('Min Wavelength:')
            self.visualization_min_slice_textbox.setText(str(self.xdata[self.data_view.visualization_min_slice]))         
            self.visualization_max_slice_label.setText('Max Wavelength:')
            self.visualization_max_slice_textbox.setText(str(self.xdata[self.data_view.visualization_max_slice]))      
    def close_tab(self):
        if self.tab.currentWidget().hdf5:
            self.tab.currentWidget().hdf5.close()
        self.tab.removeTab(self.tab.currentIndex())  
        
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
        self.connect(self.wraith, QtCore.SIGNAL('clicked()'),
                     self.open_wraith)
        self.connect(self.visualization, QtCore.SIGNAL('clicked()'),
                     self.open_visualization)
                     
    def export_graph(self):
        """
        exports the current graph to a two column text file in the 
        original file's folder
        """

        print 'saving graph at:', folder
        if self.data_view.display_ev:
            (output_filename) = (self.filename
                                 + 'x' + self.data_view.xcoordinate
                                 + 'y' + self.data_view.ycoordinate
                                 + 'wavelength'
                                 + '.txt')            
            export.export_graph(self.filename,output_filename,
                                1240/self.data_view.xcoordinate,
                                self.data_view.ycoordinate)
        else:
            (output_filename) = (self.filename
                                 + 'x' + self.data_view.xcoordinate
                                 + 'y' + self.data_view.ycoordinate
                                 + 'wavelength'
                                 + '.txt')
            export.export_graph(self.filename,output_filename,
                                self.data_view.xcoordinate,
                                self.data_view.ycoordinate)
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
        clicked_number = (self.val*(self.data_view.currentmaxvalcolor
                                         -self.data_view.currentminvalcolor)
                               +self.data_view.currentminvalcolor)
        
        if self.val < .33:
            self.data_view.currentminvalcolor = clicked_number
            self.img.set_clim(vmin=clicked_number)
            print 'new min is ', self.data_view.currentminvalcolor
    
        elif self.val > .66:
            self.data_view.currentmaxvalcolor = clicked_number
            self.img.set_clim(vmax=clicked_number)
            print 'new max is ', self.data_view.currentmaxvalcolor
        else:
            self.colorwindow = color.ColorWindow()
            self.colorwindow.exec_()
            if self.colorwindow.result() and self.colorwindow.maxcolor.text()!='':
                self.data_view.currentmaxvalcolor = int(self.colorwindow.maxcolor.text())
                self.img.set_clim(vmax=self.data_view.currentmaxvalcolor)
                print 'new max is', self.data_view.currentmaxvalcolor
            if self.colorwindow.result() and self.colorwindow.mincolor.text()!='':
                self.data_view.currentminvalcolor = int(self.colorwindow.mincolor.text())
                self.img.set_clim(vmin=self.data_view.currentminvalcolor)
                print 'new min is', self.data_view.currentminvalcolor
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
    
    def open_visualization(self):
        self.visualization_window = visualization.MayaviQWidget(self.ycube[:,:,self.data_view.visualization_max_slice:self.data_view.visualization_min_slice],
                                                                self.data_view.visualization_min_color,
                                                                self.data_view.visualization_max_color)
        self.visualization_window.show()
    def open_wraith(self):
        if self.data_view.display_ev:
            self.wraith_window = wraith_for_mf1read.Form(self.filename, 1240/self.xdata[...],
                                                     self.ycube[self.data_view.ycoordinate,
                                                           self.data_view.xcoordinate,:],
                                                     self.data_view.xcoordinate,
                                                     self.data_view.ycoordinate,
                                                     self.peak_bank)
        else:
            self.wraith_window = wraith_for_mf1read.Form(self.filename, self.xdata[...],
                                                     self.ycube[self.data_view.ycoordinate,
                                                           self.data_view.xcoordinate,:],
                                                     self.data_view.xcoordinate,
                                                     self.data_view.ycoordinate,
                                                     self.peak_bank)
        self.wraith_window.show()                                                  
       
    def reset_colors(self):
        self.img.set_clim(0, self.maxval)
        self.data_view.currentmaxvalcolor = self.maxval
        print 'new max is', self.data_view.currentmaxvalcolor
        self.data_view.currentminvalcolor = 0
        print 'new min is', self.data_view.currentminvalcolor               
                
    def set_color_bar_settings(self):
        self.data_view.currentmaxvalcolor = self.maxval
        self.data_view.currentminvalcolor = 0
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
        if self.data_view.display_ev:
            self.data_view.slider_val = sliderval-1
        else:
            self.data_view.slider_val = 1600 - sliderval           
        plot_tools.plot_image(self.img, self.img_axes, self.ycube, self.xdata,
                              self.data_view)
                              
    def update_visualization_settings(self):
        """
        updates data view to have correct values from text boxes.
        min slice and max slice switch places depending on whether the program
        is in ev mode. This is because ev's max is wavelength's min.
        """
        self.data_view.visualization_min_color = float(self.visualization_min_color_textbox.text())
        self.data_view.visualization_max_color = float(self.visualization_max_color_textbox.text())
        min_slice = float(self.visualization_min_slice_textbox.text())
        max_slice = float(self.visualization_max_slice_textbox.text())
        if self.data_view.display_ev:
            self.data_view.visualization_min_slice =1599 - analysis.ev_to_slice(max_slice, self.xdata)
            print "min slice is:", self.data_view.visualization_min_slice
            self.data_view.visualization_max_slice =1599 - analysis.ev_to_slice(min_slice, self.xdata)
            print "max slice is:", self.data_view.visualization_max_slice
        else:
            self.data_view.visualization_min_slice = 1599 - analysis.wavelength_to_slice(min_slice, self.xdata)
            self.data_view.visualization_max_slice = 1599 -analysis.wavelength_to_slice(max_slice, self.xdata)
            print "min slice is:", self.data_view.visualization_min_slice
            print "max slice is:", self.data_view.visualization_max_slice

