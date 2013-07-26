# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 17:28:09 2013

@author: JG
"""

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from PySide import QtCore
from PySide import QtGui
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar


class PeakBank(QtGui.QDialog):
    """
    Holds peaks 
    """
    def __init__(self, basename, dimension1, dimension2):
        super(PeakBank, self).__init__()
        self.setWindowTitle('PeakBank for %s'%basename)
        self.dimension1 = dimension1
        self.dimension2 = dimension2
        self.cube_peaks = []
        self.amplitudes = []
        self.sigma = []
        self.widths = []
        self.cube_residuals = []
        self.cube_fitted = False
        self.inputs()

    def inputs(self):
        
        self.table = QtGui.QTableWidget()  
        self.table.setColumnCount(1)
        
        self.button_remove_peak = QtGui.QPushButton("&Remove Peak")
        self.button_remove_peak.clicked.connect(self.remove_peak)    
       
        self.label_cube_fitted = QtGui.QLabel("Cube Box Empty")       
        
        self.button_display_peak_amplitudes = QtGui.QPushButton("&Display 1st Peak Amplitudes")
        self.button_display_peak_amplitudes.clicked.connect(self.display_peak_amplitudes)
        
        
        self.button_display_peak_sigma = QtGui.QPushButton("&Display 1st Peak Sigmas")
        self.button_display_peak_sigma.clicked.connect(self.display_peak_sigma)
        
        self.button_display_cube_residuals = QtGui.QPushButton("&Display Cube Residuals")
        self.button_display_cube_residuals.clicked.connect(self.display_cube_residuals)
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(self.table,0,0)  
        grid.addWidget(self.button_remove_peak,1,0)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.label_cube_fitted)
        vbox.addWidget(self.button_display_peak_amplitudes)
        vbox.addWidget(self.button_display_peak_sigma)
        vbox.addWidget(self.button_display_cube_residuals)
        
        grid.addLayout(vbox,0,1)
        
        
        self.setLayout(grid)
    
    def display_window(self):
        self.show()
    
    def display_peak_amplitudes(self):
        if not self.cube_fitted:
            self.cube_warning()
            return                           
        self.window_amplitude = QtGui.QWidget()
        self.window_amplitude.setWindowTitle("Peak Amplitudes")
        
        self.window_amplitude.fig = plt.figure(figsize=(8.0, 6.0))
        self.window_amplitude.canvas = FigureCanvas(self.window_amplitude.fig)
        self.window_amplitude.canvas.setParent(self.window_amplitude)
        plt.subplot()
        plt.imshow(self.amplitudes, interpolation='nearest')
        plt.colorbar()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.window_amplitude.canvas)
        self.window_amplitude.setLayout(vbox)

        self.window_amplitude.show()
    
    def display_peak_sigma(self):
        if not self.cube_fitted:
            self.cube_warning()
            return                                     
        self.window_sigma = QtGui.QWidget()
        self.window_sigma.setWindowTitle("Peak Sigmas")
        
        self.window_sigma.fig = plt.figure(figsize=(8.0, 6.0))
        self.window_sigma.canvas = FigureCanvas(self.window_sigma.fig)
        self.window_sigma.canvas.setParent(self.window_sigma)
        plt.subplot()
        plt.imshow(self.sigma, interpolation='nearest')
        plt.colorbar()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.window_sigma.canvas)
        self.window_sigma.setLayout(vbox)

        self.window_sigma.show()
    
    def display_cube_residuals(self):
        if not self.cube_fitted:
            self.cube_warning()
            return                                     
        self.window_residuals = QtGui.QWidget()
        self.window_residuals.setWindowTitle("Peak Residuals")
        
        self.window_residuals.fig = plt.figure(figsize=(8.0, 6.0))
        self.window_residuals.canvas = FigureCanvas(self.window_residuals.fig)
        self.window_residuals.canvas.setParent(self.window_residuals)
        plt.subplot()
        plt.imshow(self.cube_residuals, interpolation='nearest')
        plt.colorbar()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.window_residuals.canvas)
        self.window_residuals.setLayout(vbox)

        self.window_residuals.show()
     
    def generate_amplitudes_picture(self):
        for pixel in self.cube_peaks:
            #for peak in pixel:
            peak = pixel[0]
            self.amplitudes.append(peak['values'][0])
        self.amplitudes = np.reshape(self.amplitudes,
                                     (self.dimension1,
                                     self.dimension2))
                                     
    def generate_residuals_picture(self):
        self.cube_residuals = np.reshape(self.cube_residuals,
                                         (self.dimension1,
                                          self.dimension2))
    
    def generate_sigma_picture(self):
        for pixel in self.cube_peaks:
            #for peak in pixel:
            peak = pixel[0]
            self.sigma.append(peak['values'][2])
        self.sigma = np.reshape(self.sigma,
                                     (self.dimension1,
                                     self.dimension2))

    def hide_window(self):
        self.hide()
    
    def notify_cube_fitted(self):
        self.cube_fitted = True
        self.label_cube_fitted.setText("Cube Box Loaded")
        self.generate_amplitudes_picture()
        self.generate_sigma_picture() 
        self.generate_residuals_picture()
        
    def remove_peak(self):
        self.table.removeRow(self.table.currentRow())
       
    def cube_warning(self):
        msg = """
        Cube not fitted yet. Fit a cube to display.
        """
        QtGui.QMessageBox.about(self, "Peak Bank Message", msg.strip())
    
    def empty_cube_box(self):
        self.cube_fitted = False
        self.cube_peaks = []
        self.cube_residuals = []
        self.amplitudes = []
        self.sigma = []
        
        