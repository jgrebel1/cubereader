#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 16:27:52 2013

@author: JG
"""
import sys
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
import fit_analysis
import fit_plot_tools
import plot_tools
import data_holder
import data_view
import color
import navigation_tools
from wraith import spectra_fitting
from wraith import fitting_machinery

plt.ioff()

class CubeFit(QtGui.QMainWindow):

    def __init__(self,filename=None, parent=None):
        #super(CubeFit, self).__init__(parent) 
        QtGui.QMainWindow.__init__(self, parent)
        if filename==None:
            dialog = QtGui.QFileDialog(self)
            dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
            dialog.setNameFilter('HDF5 (*.hdf5)')
            if dialog.exec_():
                filenames = dialog.selectedFiles()
            for name in filenames:
                if name:
                    filename = name
                else:
                    print 'No file selected'
        self.filename = filename
        self.fit_data = data_holder.FitData(self.filename)
        self.peak_list = self.get_peak_list(self.fit_data)
        self.cube_filename = fit_analysis.get_cube_filename(self.filename)
        self.cube_data = data_holder.Data(self.cube_filename)
        self.cube_maxval = analysis.find_maxval(self.cube_data.ycube[...])
        self.dimensions = analysis.get_dimensions(self.cube_data.ycube) 
        self.cube_data_view = data_view.DataView(self.cube_maxval, self.dimensions)                
        self.fit_data_view = data_view.FitDataView()
        self.variable_list = self.get_variable_list(self.fit_data, self.fit_data_view)
        self.load_spectrum()
        self.load_peaks()
        self.bool_press = False
        self.make_frame()
        
    def make_frame(self):
        """populate screen"""
        self.main_frame = QtGui.QWidget()
        self.fig = plt.figure(figsize=(16.0, 6.0))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)            
        self.img_axes = self.fig.add_subplot(121)
        self.img = fit_plot_tools.initialize_image(self.img_axes,
                                                   self.fit_data,
                                                   self.fit_data_view)
        self.marker, = self.img_axes.plot(0,0,'wo')
        self.cbar = plt.colorbar(self.img)
        self.cbar.ax.set_picker(5) 
        self.graph_axes = self.fig.add_subplot(122) 
        self.img2 = plot_tools.initialize_graph(self.graph_axes,
                                                self.cube_data,
                                                self.cube_data_view)
        self.plot_peaks()
        
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        
        self.dropdown_peaks = QtGui.QComboBox()
        self.dropdown_peaks.addItems(self.peak_list)   
        self.dropdown_peaks.currentIndexChanged.connect(self.peak_changed)
        
        self.dropdown_variables = QtGui.QComboBox()
        self.dropdown_variables.addItems(self.variable_list)
        self.dropdown_variables.currentIndexChanged.connect(self.variable_changed)
        
        self.button_display_residuals = QtGui.QPushButton('Display Integrated\nResiduals')
        self.button_display_residuals.clicked.connect(self.display_residuals)
        
        self.button_display_attributes = QtGui.QPushButton('Display Peak\nAttributes')
        self.button_display_attributes.clicked.connect(self.display_attributes)
        
        self.label_min_filter = QtGui.QLabel('Min Filter')
        self.textbox_min_filter = QtGui.QLineEdit(str(-1))

        self.textbox_min_filter.editingFinished.connect(self.update_filter_settings)
        
        self.label_max_filter = QtGui.QLabel('Max Filter')
        self.textbox_max_filter = QtGui.QLineEdit(str(1))
        self.textbox_max_filter.editingFinished.connect(self.update_filter_settings)
        
        self.button_filter_from_residuals = QtGui.QPushButton('Filter From Residuals')
        self.button_filter_from_residuals.clicked.connect(self.filter_from_residuals)
        
        #self.button_test = QtGui.QPushButton('test')
        #self.button_test.clicked.connect(self.test)
        
        
                     
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.mpl_toolbar)       
        vbox1.addWidget(self.canvas)
       
        filter_hbox1 = QtGui.QHBoxLayout()
        filter_hbox1.addWidget(self.label_max_filter)
        filter_hbox1.addWidget(self.textbox_max_filter)        
                
        filter_hbox2 = QtGui.QHBoxLayout()
        filter_hbox2.addWidget(self.label_min_filter)
        filter_hbox2.addWidget(self.textbox_min_filter)        
        
        vbox2 = QtGui.QVBoxLayout()
        vbox2.addWidget(self.dropdown_peaks)
        vbox2.addWidget(self.dropdown_variables)
        vbox2.addWidget(self.button_display_residuals)
        vbox2.addWidget(self.button_display_attributes)
        vbox2.addLayout(filter_hbox1)
        vbox2.addLayout(filter_hbox2)
        vbox2.addWidget(self.button_filter_from_residuals)
        #vbox2.addWidget(self.button_test)

        
        grid.addLayout(vbox1,0,0)
        grid.addLayout(vbox2,0,1)
        
        self.main_frame.setLayout(grid)
        self.setCentralWidget(self.main_frame)
        self.connect_events()
        self.connect_shortcuts()
                                               
    def connect_events(self):
        """connect to all the events we need"""
        self.cidpress = self.img.figure.canvas.mpl_connect(
            'button_press_event', self.on_press_image)
        self.cidpress2 = self.img.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)
        self.cidpress3 = self.img.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
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
                                               
    def display_attributes(self):
        """popup peak attributes"""
        peak = self.fit_data_view.current_peak
        function = self.fit_data.peaks[peak].attrs['function']
        name = self.fit_data.peaks[peak].attrs['name']
        penalty_function = self.fit_data.peaks[peak].attrs['penalty_function']
        ranges = self.fit_data.peaks[peak].attrs['ranges']
        variables = self.fit_data.peaks[peak].attrs['variables']
        function_msg = "Function is " + str(function)
        name_msg = "Name is " + str(name)
        penalty_function_msg = "Penalty Function is " + str(penalty_function)
        ranges_msg = "Ranges are " + str(ranges)
        variables_msg = "Variables are "  + str(variables)
        full_msg = function_msg + '\n' + name_msg + '\n' \
                    +penalty_function_msg + '\n' + ranges_msg \
                    + '\n' + variables_msg
        QtGui.QMessageBox.about(self,"Attributes for %s"%peak,
                                full_msg.strip()) 
                                
    def display_residuals(self):
        fit_plot_tools.set_image_from_residuals(self.img, self.img_axes,
                                                self.fit_data, self.fit_data_view)
                                      
    def filter_from_residuals(self):
        """
        display filtered image. Filter is from residual bounds input
        by user
        """
        filtered_current_image = fit_analysis.filter_current_image_from_residuals(self.fit_data_view.min_filter,
                                                                                  self.fit_data_view.max_filter,
                                                                                  self.fit_data,
                                                                                  self.fit_data_view)
        fit_plot_tools.set_image_from_input(self.img, self.img_axes,
                                            filtered_current_image,
                                            self.fit_data_view)
        self.reset_colors()
        self.canvas.draw()        
        
    def get_peak_list(self, fit_data):
        """generates list of peak names in hdf5 file"""
        peak_list = []
        for peak in fit_data.peaks.keys():
            peak_list.append(peak)
        
        return peak_list
        
    def get_variable_list(self, fit_data, fit_data_view):
        """generates list of variable names for a given peak"""
        variable_list = []
        peak = fit_data.peaks[fit_data_view.current_peak]
        for variable in peak.keys():
            variable_list.append(variable)
        return variable_list
        
    def load_peaks(self):
        """
        populates wraith spectrum with peaks from current x and y
        coordinates
        """
        peak_list = fit_analysis.spectrum_from_data(self.peak_list,
                                                   self.fit_data, 
                                                   self.cube_data_view)         
        for peak in peak_list:
              self.spectrum.peaks.peak_list.append(fitting_machinery.Peak(self.spectrum))
              self.spectrum.peaks.peak_list[-1].set_spec(peak)
        #spectrum.peaks.optimize_fit(spectrum.E(),spectrum.nobg())
        
    def load_spectrum(self):
        """initializes a wraith spectrum"""
        self.spectrum = spectra_fitting.Spectrum()
        xdata = analysis.xdata_calc(self.cube_data, self.cube_data_view)
        ydata = analysis.ydata_calc(self.cube_data, self.cube_data_view) 
        self.spectrum.EE = xdata
        self.spectrum.data = ydata   
        
    def move_down(self):
        """move marker down and update graph"""
        navigation_tools.move_down(self.cube_data_view, self.cube_data_view.dimension1)
        self.update_graph()
        self.canvas.draw()        
    
    def move_left(self):
        """move marker left and update graph"""
        navigation_tools.move_left(self.cube_data_view)
        self.update_graph()
        self.canvas.draw()
    
    def move_right(self):
        """move marker right and update graph"""
        navigation_tools.move_right(self.cube_data_view, self.cube_data_view.dimension2)
        self.update_graph()
        self.canvas.draw()
      
    def move_up(self):
        """move marker up and update graph"""
        navigation_tools.move_up(self.cube_data_view)
        self.update_graph()
        self.canvas.draw()
      
    def on_motion(self, event):        
        """
        dragging the marker will change the graph.
        """
        if self.bool_press is False: return
        if event.inaxes != self.img.axes: return
    
        navigation_tools.change_coordinates(event, self.fit_data_view)
        self.update_graph()
        self.canvas.draw()

        
    def on_pick_color(self, event):
        """
        Clicking on the color bar will generate three different actions 
        depending on location. The upper third sets the max color value,
        the lower third sets min color value, and the middle pops up a
        window asking for custom values.
        """
        color.on_pick_color_fit(event, self.img,
                            self.fit_data,self.fit_data_view)     
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
            
        navigation_tools.change_coordinates(event, self.cube_data_view)
        self.bool_press = True
        self.update_graph()
        self.canvas.draw()


    def on_release(self, event):
        'on release we reset the press data'
        self.bool_press = False
 
    def peak_changed(self, index):
        """
        changing dropdown peak generates new variable list
        
        """
        self.fit_data_view.current_peak = self.peak_list[index]
        fit_plot_tools.set_image_from_data(self.img, self.img_axes,
                                  self.fit_data, self.fit_data_view)
        self.variable_list = self.get_variable_list(self.fit_data,
                                                    self.fit_data_view)
        self.dropdown_variables.clear()
        self.dropdown_variables.addItems(self.variable_list)
        
    def plot_peaks(self):
        """plot all peaks in spectrum to graph"""
        self.spectrum.plot_individual_peaks(scale=1.0,
                                            axes=self.graph_axes, offset=0.0)
   
    def reset_colors(self):
        color.reset_colors_fit(self.img, self.fit_data, self.fit_data_view)
        
    def update_filter_settings(self):
        """
        updates data view to have correct values from text boxes.
        data_stores input values in wavelength.
        """
        min_filter = float(self.textbox_min_filter.text())
        max_filter = float(self.textbox_max_filter.text())
        self.fit_data_view.min_filter = min_filter
        self.fit_data_view.max_filter = max_filter

    def update_graph(self):
        self.marker.set_xdata(self.cube_data_view.xcoordinate)
        self.marker.set_ydata(self.cube_data_view.ycoordinate)

        plot_tools.initialize_graph(self.graph_axes,
                                    self.cube_data,
                                    self.cube_data_view)
        self.spectrum.clear_peaks()
        self.load_peaks()        
        self.plot_peaks()                            

        
    def variable_changed(self, index):
        """changing variable updates image"""
        self.fit_data_view.current_variable = self.variable_list[index]
        fit_plot_tools.set_image_from_data(self.img, self.img_axes,
                                  self.fit_data, self.fit_data_view)
        
#main function to start up program
def main():
    #matplotlib.rcParams['mathtext.fontset'] = 'stixsans'
    app = QtGui.QApplication(sys.argv)
    form = CubeFit()
    #QApplication.setStyle(QStyleFactory.create('Plastique'))
    #QApplication.setPalette(QApplication.style().standardPalette())
    form.show()
    app.exec_()

def cube_fit():
    #matplotlib.rcParams['mathtext.fontset'] = 'stixsans'
    app = QtCore.QCoreApplication.instance()
    app.form = CubeFit()
    #QApplication.setStyle(QStyleFactory.create('Plastique'))
    #QApplication.setPalette(QApplication.style().standardPalette())
    app.form.show()
    #app.exec_()


#if run from commandline then start up by calling main()
if __name__ == "__main__":
    main()
else:
   app = QtCore.QCoreApplication.instance()