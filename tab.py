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
from PyQt4 import QtCore
from PyQt4 import QtGui
#matplotlib.rcParams['backend.qt4']='PySide'
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
import convert_to_ev
import navigation_tools

plt.ioff()
            
class Tab(QtGui.QWidget):

    def __init__(self,filename, parent=None):
        super(Tab, self).__init__(parent)      
        self.filename = filename
        print self.filename
        self.basename = analysis.get_file_basename(self.filename)
        self.data = data_holder.Data(self.filename)
        self.maxval = analysis.find_maxval(self.data.ycube[...])
        dimensions = analysis.get_dimensions(self.data.ycube) 
        self.dataview = data_view.DataView(self.maxval, dimensions)
        self.convert_mutex = QtCore.QMutex()
        self.bool_press = False
        self.make_spectrum_holder()
        self.make_frame()
 
    
    def make_frame(self):
        """populate screen"""

        self.fig = plt.figure(figsize=(16.0, 6.0))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)            
        self.img_axes = self.fig.add_subplot(121)
        self.img = plot_tools.initialize_image(self.img_axes,
                                               self.data,
                                               self.dataview)
        self.marker, = self.img_axes.plot(0,0,'wo')
        self.cbar = plt.colorbar(self.img)
        self.set_color_bar_settings()
        self.graph_axes = self.fig.add_subplot(122)  
        self.img2 = plot_tools.initialize_graph(self.graph_axes,
                                                self.data,
                                                self.dataview)

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
        
        self.button_display_header = QtGui.QPushButton('Display Header')
        self.button_display_header.setSizePolicy(QtGui.QSizePolicy.Fixed, 
                                               QtGui.QSizePolicy.Fixed)
        self.button_display_header.clicked.connect(self.display_header)
        
        self.button_export_spectrum = QtGui.QPushButton('Export Spectrum')
        self.button_export_spectrum.setSizePolicy(QtGui.QSizePolicy.Fixed, 
                                               QtGui.QSizePolicy.Fixed)
        self.button_export_spectrum.clicked.connect(self.export_spectrum)
        
        self.button_export_cube = QtGui.QPushButton('Export Cube')
        self.button_export_cube.setSizePolicy(QtGui.QSizePolicy.Fixed, 
                                               QtGui.QSizePolicy.Fixed)
        self.button_export_cube.clicked.connect(self.export_cube)
        
        self.button_wraith = QtGui.QPushButton('Open Wraith for Current Graph')
        self.button_wraith.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                  QtGui.QSizePolicy.Fixed)
        self.button_wraith.clicked.connect(self.open_wraith)
        
        self.button_visualization = QtGui.QPushButton('Open Visualization')
        self.button_visualization.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                         QtGui.QSizePolicy.Fixed)
        self.button_visualization.clicked.connect(self.open_visualization)
        
        self.button_make_ev_cube = QtGui.QPushButton('Make ev Cube')
        self.button_make_ev_cube.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                         QtGui.QSizePolicy.Fixed)
        self.button_make_ev_cube.clicked.connect(self.make_ev_cube)
                     
        self.label_vmin_slice = QtGui.QLabel()  
        self.textbox_vmin_slice = QtGui.QLineEdit(str(self.data.xdata[0]))
        self.connect(self.textbox_vmin_slice, 
                     QtCore.SIGNAL('editingFinished ()'), 
                     self.update_visualization_settings)
          
                     
        self.label_vmax_slice = QtGui.QLabel()
        self.textbox_vmax_slice = QtGui.QLineEdit(str(self.data.xdata[-1]))
        self.connect(self.textbox_vmax_slice, 
                     QtCore.SIGNAL('editingFinished ()'), 
                     self.update_visualization_settings)
        
        self.initialize_vbox(self.label_vmin_slice, self.label_vmax_slice,
                               self.textbox_vmin_slice, self.textbox_vmax_slice)
        
        hbox = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)       
        vbox.addWidget(self.canvas)
        hbox.addWidget(left_spacer)
        hbox.addWidget(self.slider)
        vbox.addLayout(hbox)
        vbox.addWidget(self.button_display_header)
        vbox.addWidget(self.button_export_spectrum)
        vbox.addWidget(self.button_export_cube)
        vbox.addWidget(self.button_wraith)
        hbox_visualization = QtGui.QHBoxLayout()
        hbox_visualization.addStretch(1)
        hbox_visualization.setDirection(QtGui.QBoxLayout.LeftToRight)
        hbox_visualization.addWidget(self.button_visualization)
        hbox_visualization.addWidget(self.button_make_ev_cube)
        hbox_visualization.addWidget(self.label_vmin_slice)
        hbox_visualization.addWidget(self.textbox_vmin_slice)
        hbox_visualization.addWidget(self.label_vmax_slice)
        hbox_visualization.addWidget(self.textbox_vmax_slice)
        vbox.addLayout(hbox_visualization)

        self.setLayout(vbox)
        
        self.connect_events()
        self.connect_shortcuts()


    def change_display(self):
        """
        changes the view between ev and wavelength
        """
        self. img2 = plot_tools.change_display(self.graph_axes,
                                               self.data,
                                               self.dataview)
                                               
        min_label, max_label = analysis.v_labels(self.dataview)
        min_text, max_text = analysis.v_text(self.dataview)
        
        self.label_vmin_slice.setText(min_label)           
        self.label_vmax_slice.setText(max_label)               
        self.textbox_vmin_slice.setText(min_text)     
        self.textbox_vmax_slice.setText(max_text)     
        
    def close_tab(self):
        """closes hdf5 file before closing tab"""
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
                                               
    def connect_shortcuts(self):
        self.shortcut_up = QtGui.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+Up")),
                                           self)
        self.shortcut_up.activated.connect(self.move_up)
        
        self.shortcut_down = QtGui.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+Down")),
                                           self)
        self.shortcut_down.activated.connect(self.move_down)
        
        self.shortcut_left = QtGui.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+Left")),
                                           self)
        self.shortcut_left.activated.connect(self.move_left)
        
        self.shortcut_right = QtGui.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+Right")),
                                           self)
        self.shortcut_right.activated.connect(self.move_right)
                                               
    def display_header(self):
        """popup header"""
        try:
            msg = self.data.header
            QtGui.QMessageBox.about(self, "Header for %s"%self.basename, msg.strip()) 
        except:
            print 'File has no header'
                     
    def export_spectrum(self):
        """
        exports the current graph to a two column excel file in the
        original file's folder
        """
        export.export_spectrum(self.filename, self.data, self.dataview)
        
    def export_cube(self):
        """
        export the entire cube to an excel file in the original file's
        folder.
        
        format is xdata, spectrum etc.
        """
        export.export_cube(self.filename, self.data, self.dataview)
    
    def initialize_vbox(self,label_vmin_slice, label_vmax_slice,
                             textbox_vmin_slice, textbox_vmax_slice):
        if self.dataview.display_ev:
            self.label_vmin_slice.setText('Min ev:')
            self.label_vmax_slice.setText('Max ev:')
        else:
            self.label_vmin_slice.setText('Min wavelength:')
            self.label_vmax_slice.setText('Max wavelength:')
        xdata = analysis.xdata_calc(self.data, self.dataview)
        textbox_vmin_slice.setText(str(xdata[0]))
        textbox_vmax_slice.setText(str(xdata[-1]))
        self.update_visualization_settings()

    def make_ev_cube(self):
        if not self.data.ev_ycube == []:
            print 'ev cube already exists'
            return
        
        convert_to_ev.ConvertEvCube(self.data.hdf5, self.data.xdata, 
                                    self.dataview.dimension1, self.dataview.dimension2,
                                    self.convert_mutex)
                    
    def make_spectrum_holder(self):
        self.spectrum_holder = spectrum_holder.SpectrumHolder(self.filename,
                                                              self.dataview.dimension1,
                                                              self.dataview.dimension2)
                                                              
    def move_down(self):
        """move marker down and update graph"""
        navigation_tools.move_down(self.dataview, self.dataview.dimension1)
        self.update_graph()
        
    
    def move_left(self):
        """move marker left and update graph"""
        navigation_tools.move_left(self.dataview)
        self.update_graph()
    
    def move_right(self):
        """move marker right and update graph"""
        navigation_tools.move_right(self.dataview, self.dataview.dimension2)
        self.update_graph()
      
    def move_up(self):
        """move marker up and update graph"""
        navigation_tools.move_up(self.dataview)
        self.update_graph()
      
    def on_motion(self, event):        
        """
        dragging the marker will change the graph.
        """
        if self.bool_press is False: return
        if event.inaxes != self.img.axes: return
    
        navigation_tools.change_coordinates(event, self.dataview)
        self.update_graph()
        self.canvas.draw()

        
    def on_pick_color(self, event):
        """
        Clicking on the color bar will generate three different actions 
        depending on location. The upper third sets the max color value,
        the lower third sets min color value, and the middle pops up a
        window asking for custom values.
        """
        color.on_pick_color_cube(event, self.img, self.data, self.dataview)
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
            
        navigation_tools.change_coordinates(event, self.dataview)
        self.bool_press = True
        self.update_graph()


    def on_release(self, event):
        'on release we reset the press data'
        self.bool_press = False
    
    def open_visualization(self):
        """opens mayavi window"""
        self.data.check_for_ev_cube(self.data.hdf5)
        ycube = analysis.mayavi_cube(self.data, self.dataview)
        if ycube == []:
            print "No ev cube in file. Press Make ev Cube"
            return
        min_slice, max_slice = analysis.mayavi_slices(self.data,
                                                      self.dataview)
        try:
            ycube_slice = ycube[:,:,min_slice:max_slice]
        except ValueError:
            ycube_slice = ycube[:,:,max_slice:min_slice]
        self.visualization_window = visualization.MayaviQWidget(ycube_slice)
        self.visualization_window.show()
        
    def open_wraith(self):
        """opens wraith window"""
        self.wraith_window = wraith_for_cubereader.Form(self.data,
                                                        self.dataview,
                                                        self.spectrum_holder)
        self.wraith_window.show()                                                  
       
    def reset_colors(self):
        color.reset_colors_cube(self.img, self.data, self.dataview)           
                
    def set_color_bar_settings(self):
        self.dataview.maxcolor = self.maxval
        self.dataview.mincolor = 0
        self.cbar.ax.set_picker(5) 
        
    def set_slider_settings(self):
        self.slider.setRange(1, self.dataview.number_of_slices)
        self.slider.setValue(1)
        self.slider.setTracking(True)
        
    def show_ev(self):     
        self.dataview.display_ev = True
        self.change_display()
        plot_tools.plot_image(self.img,
                              self.img_axes,
                              self.data,
                              self.dataview)
       
    def show_wavelength(self):      
        self.dataview.display_ev = False
        self.change_display()
        plot_tools.plot_image(self.img,
                              self.img_axes,
                              self.data,
                              self.dataview)

    def update_graph(self):
        self.marker.set_xdata(self.dataview.xcoordinate)
        self.marker.set_ydata(self.dataview.ycoordinate)        
        plot_tools.plot_graph(self.img2,
                              self.graph_axes, 
                              self.data,
                              self.dataview)

        
    def update_image_from_slider(self, sliderval):
        
        if self.dataview.display_ev:
            self.dataview.slider_val = sliderval-1
        else:
            self.dataview.slider_val = self.dataview.number_of_slices - sliderval           
        plot_tools.plot_image(self.img,
                              self.img_axes,
                              self.data,
                              self.dataview)
                              
    def update_visualization_settings(self):
        """
        updates data view to have correct values from text boxes.
        data_stores input values in wavelength.
        """
        min_input = float(self.textbox_vmin_slice.text())
        max_input = float(self.textbox_vmax_slice.text())
        if self.dataview.display_ev:
            self.dataview.vmin_wavelength = 1240/max_input
            self.dataview.vmax_wavelength = 1240/min_input
        else:
            self.dataview.vmin_wavelength = min_input
            self.dataview.vmax_wavelength = max_input

