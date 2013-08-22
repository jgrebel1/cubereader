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
import convert_to_ev

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
        self.convert_mutex = QtCore.QMutex()
        self.press = False
        self.make_spectrum_holder()
        self.make_frame()
 
    
    def make_frame(self):
        

        self.fig = plt.figure(figsize=(16.0, 6.0))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)            
        self.img_axes = self.fig.add_subplot(121)
        self.img = plot_tools.initialize_image(self.img_axes,
                                               self.data,
                                               self.data_view)
        self.marker, = self.img_axes.plot(0,0,'wo')
        self.cbar = plt.colorbar(self.img)
        self.set_color_bar_settings()
        self.graph_axes = self.fig.add_subplot(122)  
        self.img2 = plot_tools.initialize_graph(self.graph_axes,
                                                self.data,
                                                self.data_view)

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


    def change_display(self):
        """
        changes the view between ev and wavelength
        """
        self. img2 = plot_tools.change_display(self.graph_axes,
                                               self.data,
                                               self.data_view)
                                               
        min_label, max_label = analysis.v_labels(self.data_view)
        min_text, max_text = analysis.v_text(self.data_view)
        
        self.label_vmin_slice.setText(min_label)           
        self.label_vmax_slice.setText(max_label)               
        self.textbox_vmin_slice.setText(min_text)     
        self.textbox_vmax_slice.setText(max_text)     
        
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
                                               
    def display_header(self):
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
        export.export_spectrum(self.filename, self.data, self.data_view)
        
    def export_cube(self):
        """
        export the entire cube to an excel file in the original file's
        folder.
        
        format is xdata, spectrum etc.
        """
        export.export_cube(self.filename, self.data, self.data_view)
    
    def initialize_vbox(self,label_vmin_slice, label_vmax_slice,
                             textbox_vmin_slice, textbox_vmax_slice):
        if self.data_view.display_ev:
            self.label_vmin_slice.setText('Min ev:')
            self.label_vmax_slice.setText('Max ev:')
        else:
            self.label_vmin_slice.setText('Min wavelength:')
            self.label_vmax_slice.setText('Max wavelength:')
        xdata = analysis.xdata_calc(self.data, self.data_view)
        textbox_vmin_slice.setText(str(xdata[0]))
        textbox_vmax_slice.setText(str(xdata[-1]))
        self.update_visualization_settings()

    def make_ev_cube(self):
        if not self.data.ev_ycube == []:
            print 'ev cube already exists'
            return
        
        convert_to_ev.ConvertEvCube(self.data.hdf5, self.data.xdata, 
                                    self.dimension1, self.dimension2,
                                    self.convert_mutex)
                    
    def make_spectrum_holder(self):
        self.spectrum_holder = spectrum_holder.SpectrumHolder(self.filename,
                                                              self.dimension1,
                                                              self.dimension2)
        
        
        
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
        val = event.mouseevent.ydata
        clicked_number = (val*(self.data_view.maxcolor
                                         -self.data_view.mincolor)
                               +self.data_view.mincolor)
        
        if val < .33:
            self.data_view.mincolor = clicked_number
            min_color = analysis.colors_calc_min(clicked_number,
                                                 self.data,
                                                 self.data_view)
            self.img.set_clim(vmin=min_color)
            print 'new min is ', self.data_view.mincolor
    
        elif val > .66:
            self.data_view.maxcolor = clicked_number
            max_color = analysis.colors_calc_max(clicked_number,
                                                 self.data,
                                                 self.data_view)
            self.img.set_clim(vmax=max_color)
            print 'new max is ', self.data_view.maxcolor
        else:
            colorwindow = color.ColorWindow()
            colorwindow.exec_()
            
            if colorwindow.result() and colorwindow.maxcolor.text()!='':
                self.data_view.maxcolor = int(colorwindow.maxcolor.text())
                self.img.set_clim(vmax=self.data_view.maxcolor)
                print 'new max is', self.data_view.maxcolor
            if colorwindow.result() and colorwindow.mincolor.text()!='':
                self.data_view.mincolor = int(colorwindow.mincolor.text())
                self.img.set_clim(vmin=self.data_view.mincolor)
                print 'new min is', self.data_view.mincolor
            if colorwindow.resetvalue:
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

        self.data.check_for_ev_cube(self.data.hdf5)
        ycube = analysis.mayavi_cube(self.data, self.data_view)
        if ycube == []:
            print "No ev cube in file. Press Make ev Cube"
            return
        min_slice, max_slice = analysis.mayavi_slices(self.data,
                                                      self.data_view)
        try:
            ycube_slice = ycube[:,:,min_slice:max_slice]
        except ValueError:
            ycube_slice = ycube[:,:,max_slice:min_slice]
        self.visualization_window = visualization.MayaviQWidget(ycube_slice)
        self.visualization_window.show()
        
    def open_wraith(self):
        xdata = analysis.xdata_calc(self.data, self.data_view)
        ydata = analysis.ydata_calc(self.data, self.data_view)
        self.wraith_window = wraith_for_cubereader.Form(self.filename,
                                                        self.data,
                                                        self.data_view,
                                                        self.spectrum_holder)
        self.wraith_window.show()                                                  
       
    def reset_colors(self):
        maxval = analysis.maxval_calc(self.data, self.data_view)
        self.img.set_clim(0, maxval)
        self.data_view.maxcolor = self.maxval
        print 'new max is', self.data_view.maxcolor
        self.data_view.currentminvalcolor = 0
        print 'new min is', self.data_view.mincolor               
                
    def set_color_bar_settings(self):
        self.data_view.maxcolor = self.maxval
        self.data_view.mincolor = 0
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
        data_stores input values in wavelength.
        """
        min_input = float(self.textbox_vmin_slice.text())
        max_input = float(self.textbox_vmax_slice.text())
        if self.data_view.display_ev:
            self.data_view.vmin_wavelength = 1240/max_input
            self.data_view.vmax_wavelength = 1240/min_input
        else:
            self.data_view.vmin_wavelength = min_input
            self.data_view.vmax_wavelength = max_input

