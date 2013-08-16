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


class SpectrumHolder(QtGui.QDialog):
    """
    Holds peaks 
    """
    def __init__(self, basename, dimension1, dimension2):
        super(SpectrumHolder, self).__init__()
        self.setWindowTitle('Spectrum Holder for %s'%basename)
        self.resize(600,300)
        self.dimension1 = dimension1
        self.dimension2 = dimension2
        self.spectrum_box = ''
        self.cube_peaks = []
        self.cube_spectra = []
        self.amplitudes = []
        self.mu = []
        self.sigma = []
        self.m = []
        self.widths = []
        self.cube_residuals = []
        self.cube_fitted = False
        self.cube_fitting = False
        self.cube_mutex = QtCore.QMutex()
        self.inputs()

    def inputs(self):
        
        self.table = QtGui.QTableWidget()  
        self.table.setColumnCount(1)
        
        self.textbox_spectrum_box = QtGui.QTextEdit()
        self.textbox_spectrum_box.textChanged.connect(self.update_spectrum_box)
        
        self.button_empty_spectrum_box = QtGui.QPushButton("&Empty Spectrum Box")
        self.button_empty_spectrum_box.clicked.connect(self.empty_spectrum_box)    
       
        self.label_cube_fitted = QtGui.QLabel("Cube Box Empty")       
        
        self.button_display_peak_amplitudes = QtGui.QPushButton("&Display Peak Amplitudes")
        self.button_display_peak_amplitudes.clicked.connect(self.display_peak_amplitudes)
        
        self.button_display_peak_m = QtGui.QPushButton("&Display Peak M")
        self.button_display_peak_m.clicked.connect(self.display_peak_m)
        
        self.button_display_peak_mu = QtGui.QPushButton("&Display Peak Mu")
        self.button_display_peak_mu.clicked.connect(self.display_peak_mu)
             
        self.button_display_peak_sigma = QtGui.QPushButton("&Display Peak Sigmas")
        self.button_display_peak_sigma.clicked.connect(self.display_peak_sigma)
        
        self.button_display_cube_residuals = QtGui.QPushButton("&Display Cube Residuals")
        self.button_display_cube_residuals.clicked.connect(self.display_cube_residuals)
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(self.textbox_spectrum_box,0,0)  
        grid.addWidget(self.button_empty_spectrum_box,1,0)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.label_cube_fitted)
        vbox.addWidget(self.button_display_peak_amplitudes)
        vbox.addWidget(self.button_display_peak_mu)
        vbox.addWidget(self.button_display_peak_sigma)
        vbox.addWidget(self.button_display_peak_m)
        vbox.addWidget(self.button_display_cube_residuals)
        
        grid.addLayout(vbox,0,1)
        
        
        self.setLayout(grid)
        
    def cube_warning(self):
        msg = """
        Cube not fitted yet. Fit a cube to display.
        """
        QtGui.QMessageBox.about(self, "Spectrum Holder Message", msg.strip())
        
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
        for i in np.arange(self.peak_count):

            axes = plt.subplot(self.peak_count, 1, i)
            axes.set_title("Peak Number %s"%str(i+1))            
            plt.imshow(self.amplitudes[:,:,i], interpolation='nearest')
            plt.colorbar()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.window_amplitude.canvas)
        self.window_amplitude.setLayout(vbox)

        self.window_amplitude.show()
        
    def display_peak_m(self):
        if not self.cube_fitted:
            self.cube_warning()
            return                           
        self.window_m = QtGui.QWidget()
        self.window_m.setWindowTitle("Peak M's")
        
        self.window_m.fig = plt.figure(figsize=(8.0, 6.0))
        self.window_m.canvas = FigureCanvas(self.window_m.fig)
        self.window_m.canvas.setParent(self.window_m)
        for i in np.arange(self.peak_count):

            axes = plt.subplot(self.peak_count, 1, i)
            axes.set_title("Peak Number %s"%str(i+1))            
            plt.imshow(self.m[:,:,i], interpolation='nearest')
            plt.colorbar()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.window_m.canvas)
        self.window_m.setLayout(vbox)

        self.window_m.show()
        
    def display_peak_mu(self):
        if not self.cube_fitted:
            self.cube_warning()
            return                           
        self.window_mu = QtGui.QWidget()
        self.window_mu.setWindowTitle("Peak Mu's")
        
        self.window_mu.fig = plt.figure(figsize=(8.0, 6.0))
        self.window_mu.canvas = FigureCanvas(self.window_mu.fig)
        self.window_mu.canvas.setParent(self.window_mu)
        for i in np.arange(self.peak_count):

            axes = plt.subplot(self.peak_count, 1, i)
            axes.set_title("Peak Number %s"%str(i+1))            
            plt.imshow(self.mu[:,:,i], interpolation='nearest')
            plt.colorbar()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.window_mu.canvas)
        self.window_mu.setLayout(vbox)

        self.window_mu.show()
    
    def display_peak_sigma(self):
        if not self.cube_fitted:
            self.cube_warning()
            return                                     
        self.window_sigma = QtGui.QWidget()
        self.window_sigma.setWindowTitle("Peak Sigmas")
        
        self.window_sigma.fig = plt.figure(figsize=(8.0, 6.0))
        self.window_sigma.canvas = FigureCanvas(self.window_sigma.fig)
        self.window_sigma.canvas.setParent(self.window_sigma)
        for i in np.arange(self.peak_count):
            axes = plt.subplot(self.peak_count, 1, i)
            axes.set_title("Peak Number %s"%str(i+1)) 
            plt.imshow(self.sigma[:,:,i], interpolation='nearest')
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
        
    def empty_cube_box(self):
        self.cube_fitted = False
        self.cube_peaks = []
        self.cube_residuals = []
        self.amplitudes = []
        self.sigma = []
        
     
    def empty_spectrum_box(self):
        if not self.textbox_spectrum_box.isReadOnly():
            self.textbox_spectrum_box.clear()

    def generate_amplitudes_picture(self):  
        for spectrum in self.cube_peaks:
            for peak in spectrum:
                self.amplitudes.append(peak['values'][0])
        print 'shape is', np.shape(self.amplitudes)
        self.amplitudes = np.reshape(self.amplitudes,
                                     (self.dimension1,
                                      self.dimension2,
                                      self.peak_count))
                                      
    def generate_m_picture(self):
        for spectrum in self.cube_peaks:
            for peak in spectrum:
                self.m.append(peak['values'][3])
            
        self.m = np.reshape(self.m,
                            (self.dimension1,
                             self.dimension2,
                             self.peak_count))
                                      
    def generate_mu_picture(self):
        for spectrum in self.cube_peaks:
            for peak in spectrum:
                self.mu.append(peak['values'][1])
            
        self.mu = np.reshape(self.mu,
                             (self.dimension1,
                              self.dimension2,
                              self.peak_count))
                                     
    def generate_residuals_picture(self):
        self.cube_residuals = np.reshape(self.cube_residuals,
                                         (self.dimension1,
                                          self.dimension2))
    
    def generate_sigma_picture(self):
        for spectrum in self.cube_peaks:
            for peak in spectrum:
                self.sigma.append(peak['values'][2])
            
        self.sigma = np.reshape(self.sigma,
                                (self.dimension1,
                                 self.dimension2,
                                 self.peak_count))

    def hide_window(self):
        self.hide()
    
    def notify_cube_fitted(self):
        self.label_cube_fitted.setText("Cube Box Loaded")
        for spectrum in self.cube_peaks:
            self.peak_count = 0            
            for peak in spectrum:
                self.peak_count += 1
            break
        self.generate_amplitudes_picture()
        self.generate_mu_picture()
        self.generate_sigma_picture() 
        self.generate_m_picture()
        self.generate_residuals_picture()
        self.cube_fitted = True
        self.cube_fitting = False
        self.textbox_spectrum_box.setReadOnly(False)
    
    def notify_cube_fitting(self):
        self.empty_cube_box()
        self.textbox_spectrum_box.setReadOnly(True)
        self.cube_fitting = True
       
    def stop_fit(self):
        self.cube_fitted = False
        self.cube_fitting = False
        self.textbox_spectrum_box.setReadOnly(False)

    def update_spectrum_box(self):
        self.spectrum_box = self.textbox_spectrum_box.toPlainText()
        

        
        