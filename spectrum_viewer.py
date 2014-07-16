import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from PySide import QtCore
from PySide import QtGui
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


#project specific items

import analysis
import fit_analysis

class SpectrumViewer(QtGui.QDialog):
    """
    Viewer for Spectrum Holder
    """
    def __init__(self, spectrum_holder):
        super(SpectrumViewer, self).__init__()
        self.filename = spectrum_holder.filename
        basename = analysis.get_file_basename(spectrum_holder.filename)
        self.setWindowTitle('Spectrum Holder for %s'%basename)
        self.resize(600,300)
        self.spectrum_holder = spectrum_holder
        self.cube_mutex = QtCore.QMutex()
        self.inputs()
    
    def inputs(self):
        """populate screen"""
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
        
        self.button_save_cube = QtGui.QPushButton("&Save Cube")
        self.button_save_cube.clicked.connect(self.save_cube)
        
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
        vbox.addWidget(self.button_save_cube)
        
        grid.addLayout(vbox,0,1)
        
        
        self.setLayout(grid)
        
    def cube_warning(self):
        """popup warning when cube is not fitted yet"""
        msg = """
        Cube not fitted yet. Fit a cube to display.
        """
        QtGui.QMessageBox.about(self, "Spectrum Holder Message", msg.strip())
        
    def display_window(self):
        self.show()
    
    def display_peak_amplitudes(self):
        """popup window with all peak amplitudes"""
        if not self.spectrum_holder.cube_fitted:
            self.cube_warning()
            return    
            
        self.window_amplitude = QtGui.QWidget()
        self.window_amplitude.setWindowTitle("Peak Amplitudes")       
        self.window_amplitude.fig = plt.figure(figsize=(8.0, 6.0))
        self.window_amplitude.canvas = FigureCanvas(self.window_amplitude.fig)
        self.window_amplitude.canvas.setParent(self.window_amplitude)
        
        image_cube = self.spectrum_holder.amplitudes
        self.plot_peaks(image_cube, self.spectrum_holder.peak_count)
            
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.window_amplitude.canvas)
        self.window_amplitude.setLayout(vbox)
        self.window_amplitude.show()
        
    def display_peak_m(self):
        """popup window with all peak m's"""
        if not self.spectrum_holder.cube_fitted:
            self.cube_warning()
            return 
                          
        self.window_m = QtGui.QWidget()
        self.window_m.setWindowTitle("Peak M's")        
        self.window_m.fig = plt.figure(figsize=(8.0, 6.0))
        self.window_m.canvas = FigureCanvas(self.window_m.fig)
        self.window_m.canvas.setParent(self.window_m)
        
        image_cube = self.spectrum_holder.m
        self.plot_peaks(image_cube, self.spectrum_holder.peak_count)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.window_m.canvas)
        self.window_m.setLayout(vbox)
        self.window_m.show()
        
    def display_peak_mu(self):
        """popup window with all peak mu's"""
        if not self.spectrum_holder.cube_fitted:
            self.cube_warning()
            return     
                      
        self.window_mu = QtGui.QWidget()
        self.window_mu.setWindowTitle("Peak Mu's")        
        self.window_mu.fig = plt.figure(figsize=(8.0, 6.0))
        self.window_mu.canvas = FigureCanvas(self.window_mu.fig)
        self.window_mu.canvas.setParent(self.window_mu)

        image_cube = self.spectrum_holder.mu
        self.plot_peaks(image_cube, self.spectrum_holder.peak_count)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.window_mu.canvas)
        self.window_mu.setLayout(vbox)
        self.window_mu.show()
    
    def display_peak_sigma(self):
        """popup window with all peak sigmas"""
        if not self.spectrum_holder.cube_fitted:
            self.cube_warning()
            return        
                             
        self.window_sigma = QtGui.QWidget()
        self.window_sigma.setWindowTitle("Peak Sigmas")        
        self.window_sigma.fig = plt.figure(figsize=(8.0, 6.0))
        self.window_sigma.canvas = FigureCanvas(self.window_sigma.fig)
        self.window_sigma.canvas.setParent(self.window_sigma)
        
        image_cube = self.spectrum_holder.sigma
        self.plot_peaks(image_cube, self.spectrum_holder.peak_count)
            
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.window_sigma.canvas)
        self.window_sigma.setLayout(vbox)
        self.window_sigma.show()

    def display_cube_residuals(self):
        """popup window with integrated residuals"""
        if not self.spectrum_holder.cube_fitted:
            self.cube_warning()
            return                                     
        self.window_residuals = QtGui.QWidget()
        self.window_residuals.setWindowTitle("Peak Residuals")
        
        self.window_residuals.fig = plt.figure(figsize=(8.0, 6.0))
        self.window_residuals.canvas = FigureCanvas(self.window_residuals.fig)
        self.window_residuals.canvas.setParent(self.window_residuals)
        plt.subplot()
        plt.imshow(self.spectrum_holder.cube_residuals, interpolation='nearest')
        plt.colorbar()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.window_residuals.canvas)
        self.window_residuals.setLayout(vbox)

        self.window_residuals.show()
        
    def empty_spectrum_box(self):
        if not self.textbox_spectrum_box.isReadOnly():
            self.textbox_spectrum_box.clear()
 
    def hide_window(self):
        self.hide()
    
    def plot_peaks(self, image_cube, peak_count):
        for peak_number in np.arange(peak_count):
            axes = plt.subplot(1, peak_count, peak_number)
            axes.set_title("Peak Number %s"%str(peak_number+1))
            image = fit_analysis.get_image_from_cube(image_cube, peak_number)
            plt.imshow(image, interpolation='nearest')
            plt.colorbar() 

    def save_cube(self):
        self.spectrum_holder.save_cube()
        
    def update_spectrum_box(self):
        self.spectrum_holder.spectrum_box = self.textbox_spectrum_box.toPlainText()
        

#main function to start up program

def main(spectrum_holder):
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
        form = SpectrumViewer(spectrum_holder)
        form.hide()
        app.exec_()
        return form.data
    else:
        form = SpectrumViewer(spectrum_holder)
        #app.form.show()
        app.exec_()
        return form.data

#holder function to start up program from interactive terminal
def holder(filename, dimension1, dimension2):
    #matplotlib.rcParams['mathtext.fontset'] = 'stixsans'
    app = QtCore.QCoreApplication.instance()
    app.form = SpectrumViewer(filename, dimension1, dimension2)
    #QApplication.setStyle(QStyleFactory.create('Plastique'))
    #QApplication.setPalette(QApplication.style().standardPalette())
    #app.form.show()
    #app.exec_()
    return app.form