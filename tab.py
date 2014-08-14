# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 13:14:51 2013

@author: JG
"""

import os
os.environ['ETS_TOOLKIT'] = 'qt4'
#from pyface.qt import QtGui, QtCore
from traits.api import HasTraits, Instance, on_trait_change, \
    Int, Dict
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
        SceneEditor

import numpy as np
from numpy import array
import matplotlib
from matplotlib import pyplot as plt
from PySide import QtCore, QtGui, QtUiTools
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
import navigation_tools
import h_cubereader
import view_windows
import view_windows_pyqtgraph

plt.ioff()
            
class Tab(QtGui.QWidget):

    def __init__(self,filename, parent=None):
        QtGui.QWidget.__init__(self, parent)   
        self.filename = filename
        print self.filename
        self.cube = h_cubereader.load_data(filename)
        self.basename = analysis.get_file_basename(self.filename)
        self.data = self.cube[0]
        self.dataview = self.cube[1]
        self.convert_mutex = QtCore.QMutex()
        self.bool_press = False
        self.make_spectrum_holder()
        self.make_frame()
        self.connect_buttons()
#         self.view.show()
#         self.show()
        
 
    
    def make_frame(self):
        """populate screen"""
        
        # Layout 
        ui_loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile("tab.ui")
        ui_file.open(QtCore.QFile.ReadOnly); 
        self.ui = ui_loader.load(ui_file)
        ui_file.close()
        self.ui.setParent(self)
        
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(self.ui)
        self.setLayout(self.vbox)
        
        self.view = view_windows_pyqtgraph.ViewData(self.cube)
        
        self.initialize_vbox(self.ui.label_min, self.ui.label_max,
                               self.ui.edit_min, self.ui.edit_max)
        self.ui.view.addWidget(self.view.ui)


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
        
    def connect_buttons(self):
        self.ui.button_display_header.clicked.connect(self.display_header)
        self.ui.button_export_spectrum.clicked.connect(self.export_spectrum)
        self.ui.button_export_cube.clicked.connect(self.export_cube)
        self.ui.button_wraith.clicked.connect(self.open_wraith)
        self.ui.button_mayavi.clicked.connect(self.open_visualization)
        self.ui.button_make_ev_cube.clicked.connect(self.make_ev_cube)
        self.ui.edit_min.setText = str(self.data.xdata[0])
        self.ui.edit_min.editingFinished.connect(self.update_visualization_settings)
        self.ui.edit_max.setText = str(self.data.xdata[-1])
        self.ui.edit_max.editingFinished.connect(self.update_visualization_settings)
        
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
    
    def initialize_vbox(self,label_min, label_max,
                             edit_min, edit_max):
        label_min.setText('Min')
        label_max.setText('Max')
        xdata = analysis.xdata_calc(self.data, self.dataview)
        edit_min.setText(str(xdata[0]))
        edit_max.setText(str(xdata[-1]))
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

    def update_visualization_settings(self):
        """
        updates data view to have correct values from text boxes.
        data_stores input values in wavelength.
        """
        min_input = float(self.ui.edit_min.text())
        max_input = float(self.ui.edit_max.text())
        if self.dataview.display_ev:
            self.dataview.vmin_wavelength = 1240/max_input
            self.dataview.vmax_wavelength = 1240/min_input
        else:
            self.dataview.vmin_wavelength = min_input
            self.dataview.vmax_wavelength = max_input

