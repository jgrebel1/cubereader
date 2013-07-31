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
from numpy import array
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
import wraith_for_cubereader
import visualization
import spectrum_holder
import data_holder

plt.ioff()
            
class Tab(QtGui.QWidget):

    def __init__(self,filename, parent=None):
        super(Tab, self).__init__(parent)      
        self.filename = filename
        print self.filename
        self.basename = analysis.get_file_basename(self.filename)
        self.data = data_holder.Data(self.filename)
        self.maxval = analysis.find_maxval(self.data.ycube[...])
        self.dimension1, self.dimension2, self.number_of_slices = analysis.get_dimensions(self.data.ycube) 
        self.data_view = data_view.DataView(self.maxval, self.number_of_slices)
        self.press = False
        self.make_spectrum_holder()
        self.make_frame()
 
    
    def make_frame(self):
        

        self.fig = plt.figure(figsize=(16.0, 6.0))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)            
        self.img_axes = self.fig.add_subplot(121)
        self.img = plot_tools.initialize_image(self.img_axes,
                                               data = self.data,
                                               slice1=1,
                                               maxval=self.maxval)
        self.marker, = self.img_axes.plot(0,0,'wo')
        self.cbar = plt.colorbar(self.img)
        self.set_color_bar_settings()
        self.graph_axes = self.fig.add_subplot(122)        
        self.img2 = plot_tools.initialize_graph(self.graph_axes,
                                                self.data,
                                                self.maxval)

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
        
        self.button_export_graph = QtGui.QPushButton('Export Graph')
        self.button_export_graph.setSizePolicy(QtGui.QSizePolicy.Fixed, 
                                               QtGui.QSizePolicy.Fixed)
        self.button_export_graph.clicked.connect(self.export_graph)
        
        self.button_wraith = QtGui.QPushButton('Open Wraith for Current Graph')
        self.button_wraith.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                  QtGui.QSizePolicy.Fixed)
        self.button_wraith.clicked.connect(self.open_wraith)
        
        self.button_visualization = QtGui.QPushButton('Open Visualization')
        self.button_visualization.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                         QtGui.QSizePolicy.Fixed)
        self.button_visualization.clicked.connect(self.open_visualization)
        
        #visualization inputs
        self.label_vmin_color = QtGui.QLabel('Min Color:')
        self.textbox_vmin_color = QtGui.QLineEdit(str(self.data_view.vmin_color))
        self.connect(self.textbox_vmin_color, 
                     QtCore.SIGNAL('editingFinished ()'), 
                     self.update_visualization_settings)
                     
        self.label_vmax_color= QtGui.QLabel('Max Color:')
        self.textbox_vmax_color = QtGui.QLineEdit(str(self.data_view.vmax_color))
        self.connect(self.textbox_vmax_color, 
                     QtCore.SIGNAL('editingFinished ()'), 
                     self.update_visualization_settings)
                     
        self.label_vmin_slice = QtGui.QLabel('Min Wavelength:')
        self.textbox_vmin_slice = QtGui.QLineEdit(str(self.data.xdata[-1]))
        self.connect(self.textbox_vmin_slice, 
                     QtCore.SIGNAL('editingFinished ()'), 
                     self.update_visualization_settings)
                     
        self.label_vmax_slice = QtGui.QLabel('Max Wavelength:')
        self.textbox_vmax_slice = QtGui.QLineEdit(str(self.data.xdata[0]))
        self.connect(self.textbox_vmax_slice, 
                     QtCore.SIGNAL('editingFinished ()'), 
                     self.update_visualization_settings)
        
        hbox = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)       
        vbox.addWidget(self.canvas)
        hbox.addWidget(left_spacer)
        hbox.addWidget(self.slider)
        vbox.addLayout(hbox)
        vbox.addWidget(self.button_export_graph)
        vbox.addWidget(self.button_wraith)
        hbox_visualization = QtGui.QHBoxLayout()
        hbox_visualization.addStretch(1)
        hbox_visualization.setDirection(QtGui.QBoxLayout.LeftToRight)
        hbox_visualization.addWidget(self.button_visualization)
        hbox_visualization.addWidget(self.label_vmin_color)
        hbox_visualization.addWidget(self.textbox_vmin_color)
        hbox_visualization.addWidget(self.label_vmax_color)
        hbox_visualization.addWidget(self.textbox_vmax_color)
        hbox_visualization.addWidget(self.label_vmin_slice)
        hbox_visualization.addWidget(self.textbox_vmin_slice)
        hbox_visualization.addWidget(self.label_vmax_slice)
        hbox_visualization.addWidget(self.textbox_vmax_slice)
        vbox.addLayout(hbox_visualization)

        self.setLayout(vbox)
        
        self.connect_events()


    def change_display(self):
        """
        changes the view between ev and wavelength
        """
        self. img2 = plot_tools.change_display(self.graph_axes,
                                               self.data,
                                               self.data_view)
        if self.data_view.display_ev:
            self.label_vmin_slice.setText('Min ev:')
            self.textbox_vmin_slice.setText(str(1240/self.data.xdata[self.data_view.vmax_slice]))
            self.label_vmax_slice.setText('Max ev:')
            self.textbox_vmax_slice.setText(str(1240/self.data.xdata[self.data_view.vmin_slice]))
        else:
            self.label_vmin_slice.setText('Min Wavelength:')
            self.textbox_vmin_slice.setText(str(self.data.xdata[self.data_view.vmin_slice]))         
            self.label_vmax_slice.setText('Max Wavelength:')
            self.textbox_vmax_slice.setText(str(self.data.xdata[self.data_view.vmax_slice]))      
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
        
                    
    def make_spectrum_holder(self):
        self.spectrum_holder = spectrum_holder.SpectrumHolder(self.basename, self.dimension1, self.dimension2)
        
        
        
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
        try:
            self.visualization_window = visualization.MayaviQWidget(self.data.ycube[:,:,self.data_view.vmax_slice:self.data_view.vmin_slice],
                                                                self.data_view.vmin_color,
                                                                self.data_view.vmax_color)
        except ValueError:
            self.visualization_window = visualization.MayaviQWidget(self.data.ycube[:,:,self.data_view.vmin_slice:self.data_view.vmax_slice],
                                                                self.data_view.vmin_color,
                                                                self.data_view.vmax_color)
        self.visualization_window.show()
    def open_wraith(self):
        if self.data_view.display_ev:
            self.wraith_window = wraith_for_cubereader.Form(self.filename, 1240/self.data.xdata,
                                                     self.data.ycube[self.data_view.ycoordinate,
                                                           self.data_view.xcoordinate,:],
                                                     self.data_view.xcoordinate,
                                                     self.data_view.ycoordinate,
                                                     self.spectrum_holder,
                                                     self.data.ycube)
        else:
            self.wraith_window = wraith_for_cubereader.Form(self.filename, self.data.xdata,
                                                     self.data.ycube[self.data_view.ycoordinate,
                                                           self.data_view.xcoordinate,:],
                                                     self.data_view.xcoordinate,
                                                     self.data_view.ycoordinate,
                                                     self.spectrum_holder, 
                                                     self.data.ycube)
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
        self.slider.setRange(1, self.number_of_slices)
        self.slider.setValue(1)
        self.slider.setTracking(True)
        
    def show_ev(self):     
        self.data_view.display_ev = True
        self.change_display()
        plot_tools.plot_image(self.img,
                              self.img_axes,
                              self.data,
                              self.data_view)
       
    def show_wavelength(self):      
        self.data_view.display_ev = False
        self.change_display()
        plot_tools.plot_image(self.img,
                              self.img_axes,
                              self.data,
                              self.data_view)

    def update_graph(self):
        plot_tools.plot_graph(self.img2,
                              self.graph_axes, 
                              self.data,
                              self.data_view)
        self.marker.set_xdata(self.data_view.xcoordinate)
        self.marker.set_ydata(self.data_view.ycoordinate)
        
    def update_image_from_slider(self, sliderval):
        
        if self.data_view.display_ev:
            self.data_view.slider_val = sliderval-1
        else:
            self.data_view.slider_val = self.number_of_slices - sliderval           
        plot_tools.plot_image(self.img,
                              self.img_axes,
                              self.data,
                              self.data_view)
                              
    def update_visualization_settings(self):
        """
        updates data view to have correct values from text boxes.
        """
        self.data_view.vmin_color = float(self.textbox_vmin_color.text())
        self.data_view.vmax_color = float(self.textbox_vmax_color.text())
        min_slice = float(self.textbox_vmin_slice.text())
        max_slice = float(self.textbox_vmax_slice.text())
        # the -1 compensates for python lists starting at 0
        if self.data_view.display_ev:
            self.data_view.vmin_slice = self.number_of_slices -1 - analysis.ev_to_slice(min_slice, 
                                                             self.data)
            print "min slice is:", self.data_view.vmin_slice
            self.data_view.vmax_slice  = self.number_of_slices - 1 - analysis.ev_to_slice(max_slice,
                                                             self.data)
            print "max slice is:", self.data_view.vmax_slice
        else:
            self.data_view.vmin_slice = analysis.wavelength_to_slice(min_slice,
                                                                     self.data)
            self.data_view.vmax_slice = analysis.wavelength_to_slice(max_slice,
                                                                     self.data)
            print "min slice is:", self.data_view.vmin_slice
            print "max slice is:", self.data_view.vmax_slice

