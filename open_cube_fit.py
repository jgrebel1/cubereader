# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 16:27:52 2013

@author: JG
"""
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
import fit_analysis
import fit_plot_tools
import data_holder
import data_view
import color

plt.ioff()

class CubeFit(QtGui.QWidget):

    def __init__(self,filename, parent=None):
        super(CubeFit, self).__init__(parent) 
        self.filename = filename
        self.data = data_holder.FitData(self.filename)
        self.peak_list = self.get_peak_list(self.data)
        self.data_view = data_view.FitDataView()
        self.variable_list = self.get_variable_list(self.data, self.data_view)
        self.make_frame()
        
    def make_frame(self):
        self.fig = plt.figure(figsize=(16.0, 6.0))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)            
        self.img_axes = self.fig.add_subplot(111)
        self.img = fit_plot_tools.initialize_image(self.img_axes,
                                                   self.data,
                                                   self.data_view)
        self.cbar = plt.colorbar(self.img)
        self.cbar.ax.set_picker(5) 
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
        

        
        grid.addLayout(vbox1,0,0)
        grid.addLayout(vbox2,0,1)
        
        
        self.setLayout(grid)
        self.cidpick = self.canvas.mpl_connect('pick_event',
                                               self.on_pick_color)
                                               
    def display_attributes(self):
        function = self.data.peaks[self.data_view.current_peak].attrs['function']
        name = self.data.peaks[self.data_view.current_peak].attrs['name']
        penalty_function = self.data.peaks[self.data_view.current_peak].attrs['penalty_function']
        ranges = self.data.peaks[self.data_view.current_peak].attrs['ranges']
        variables = self.data.peaks[self.data_view.current_peak].attrs['variables']
        function_msg = "Function is " + str(function)
        name_msg = "Name is " + str(name)
        penalty_function_msg = "Penalty Function is " + str(penalty_function)
        ranges_msg = "Ranges are " + str(ranges)
        variables_msg = "Variables are "  + str(variables)
        full_msg = function_msg + '\n' + name_msg + '\n' \
                    +penalty_function_msg + '\n' + ranges_msg \
                    + '\n' + variables_msg
        QtGui.QMessageBox.about(self,"Attributes for %s"%self.data_view.current_peak,
                                full_msg.strip()) 
                                
    def display_residuals(self):
        fit_plot_tools.set_image_from_residuals(self.img, self.img_axes,
                                                self.data, self.data_view)
                                      
    def filter_from_residuals(self):
        filtered_current_image = fit_analysis.filter_current_image_from_residuals(self.data_view.min_filter,
                                                                                  self.data_view.max_filter,
                                                                                  self.data,
                                                                                  self.data_view)
        fit_plot_tools.set_image_from_input(self.img, self.img_axes,
                                            filtered_current_image,
                                            self.data_view)
    
    def peak_changed(self, index):
        self.data_view.current_peak = self.peak_list[index]
        fit_plot_tools.set_image_from_data(self.img, self.img_axes,
                                  self.data, self.data_view)
        self.variable_list = self.get_variable_list(self.data, self.data_view)
        self.dropdown_variables.clear()
        self.dropdown_variables.addItems(self.variable_list)
        
        
    def get_peak_list(self, data):
        peak_list = []
        for peak in data.peaks.keys():
            peak_list.append(peak)
        
        return peak_list
        
    def get_variable_list(self, data, data_view):
        variable_list = []
        peak = data.peaks[data_view.current_peak]
        for variable in peak.keys():
            variable_list.append(variable)
        return variable_list
        
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
            self.img.set_clim(vmin=self.data_view.mincolor)
            print 'new min is ', self.data_view.mincolor
    
        elif val > .66:
            self.data_view.maxcolor = clicked_number
            self.img.set_clim(vmax=self.data_view.maxcolor)
            print 'new max is ', self.data_view.maxcolor
        else:
            colorwindow = color.ColorWindow()
            colorwindow.exec_()
            
            if colorwindow.result() and colorwindow.maxcolor.text()!='':
                self.data_view.maxcolor = float(colorwindow.maxcolor.text())
                self.img.set_clim(vmax=self.data_view.maxcolor)
                print 'new max is', self.data_view.maxcolor
            if colorwindow.result() and colorwindow.mincolor.text()!='':
                self.data_view.mincolor = float(colorwindow.mincolor.text())
                self.img.set_clim(vmin=self.data_view.mincolor)
                print 'new min is', self.data_view.mincolor
            if colorwindow.resetvalue:
                self.reset_colors(self.img, self.data, self.data_view)
        self.canvas.draw()   
        
    def reset_colors(self, img, data, data_view):
        image = fit_analysis.get_image_from_data(data, data_view)
        data_view.mincolor = np.amin(image)
        data_view.maxcolor = np.amax(image)
        img.set_clim(data_view.mincolor, data_view.maxcolor)
        
    def update_filter_settings(self):
        """
        updates data view to have correct values from text boxes.
        data_stores input values in wavelength.
        """
        min_filter = float(self.textbox_min_filter.text())
        max_filter = float(self.textbox_max_filter.text())
        self.data_view.min_filter = min_filter
        self.data_view.max_filter = max_filter

        
    def variable_changed(self, index):
        self.data_view.current_variable = self.variable_list[index]
        fit_plot_tools.set_image_from_data(self.img, self.img_axes,
                                  self.data, self.data_view)
        