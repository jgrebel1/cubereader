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
    def __init__(self, dimension1, dimension2):
        super(PeakBank, self).__init__()
        self.setWindowTitle('PeakBank')
        self.dimension1 = dimension1
        self.dimension2 = dimension2
        self.cube_peaks = []
        self.amplitudes = []
        self.sigma = []
        self.widths = []
        self.residuals = []
        self.inputs()

    def inputs(self):
        
        self.table = QtGui.QTableWidget()  
        self.table.setColumnCount(1)
        
        self.button_remove_peak = QtGui.QPushButton("&Remove Peak")
        self.button_remove_peak.clicked.connect(self.remove_peak)        
        
        self.button_display_peak_amplitudes = QtGui.QPushButton("&Display 1st Peak Amplitudes")
        self.button_display_peak_amplitudes.clicked.connect(self.display_peak_amplitudes)
        
        
        self.button_display_peak_sigma = QtGui.QPushButton("&Display 1st Peak Sigmas")
        self.button_display_peak_sigma.clicked.connect(self.display_peak_sigma)
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(self.table,0,0)  
        grid.addWidget(self.button_remove_peak,1,0)
        grid.addWidget(self.button_display_peak_amplitudes,0,1)
        grid.addWidget(self.button_display_peak_sigma,1,1)
        
        self.setLayout(grid)
    
    def display_window(self):
        self.show()
    
    def hide_window(self):
        self.hide()
    
    def remove_peak(self):
        self.table.removeRow(self.table.currentRow())
    
    def display_peak_amplitudes(self):
        for pixel in self.cube_peaks:
            #for peak in pixel:
            peak = pixel[0]
            self.amplitudes.append(peak['values'][0])
        self.amplitudes = np.reshape(self.amplitudes,
                                     (self.dimension1,
                                     self.dimension2))
                                     
        self.amplitude_window = QtGui.QWidget()
        self.amplitude_window.setWindowTitle("Peak Amplitudes")
        
        self.amplitude_window.fig = plt.figure(figsize=(8.0, 6.0))
        self.amplitude_window.canvas = FigureCanvas(self.amplitude_window.fig)
        self.amplitude_window.canvas.setParent(self.amplitude_window)
        plt.subplot()
        plt.imshow(self.amplitudes, interpolation='nearest')
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.amplitude_window.canvas)
        self.amplitude_window.setLayout(vbox)

        self.amplitude_window.show()
    
    def display_peak_sigma(self):
        for pixel in self.cube_peaks:
            #for peak in pixel:
            peak = pixel[0]
            self.sigma.append(peak['values'][2])
        self.sigma = np.reshape(self.sigma,
                                     (self.dimension1,
                                     self.dimension2))
                                     
        self.sigma_window = QtGui.QWidget()
        self.sigma_window.setWindowTitle("Peak Sigmas")
        
        self.sigma_window.fig = plt.figure(figsize=(8.0, 6.0))
        self.sigma_window.canvas = FigureCanvas(self.sigma_window.fig)
        self.sigma_window.canvas.setParent(self.sigma_window)
        plt.subplot()
        plt.imshow(self.sigma, interpolation='nearest')
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.sigma_window.canvas)
        self.sigma_window.setLayout(vbox)

        self.sigma_window.show()
    
    def display_peak_residuals(self):
        pass
     
        
        