# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 13:35:48 2013

@author: JG
"""
import os
import numpy as np
import matplotlib
from PySide import QtCore
from PySide import QtGui
matplotlib.rcParams['backend.qt4']='PySide'
from scipy import interpolate

#project specific items

class ControlWindow(QtGui.QDialog):
        
    def __init__(self, current_tab, parent=None):
        super(ControlWindow, self).__init__(parent)
        self.current_tab = current_tab
        self.setWindowTitle('Control Panel')
        self.setModal(False)
        self.inputs()
        
    def inputs(self):

        self.imageslicelabel= QtGui.QLabel('Image Slice Wavelength:')
        maxcolorlabel = QtGui.QLabel('Max Color Value:')
        mincolorlabel = QtGui.QLabel('Min Color Value:')        
        graphslicelabelx = QtGui.QLabel('Graph Slice X Coordinate:')
        graphslicelabely = QtGui.QLabel('Graph Slice Y Coordinate:')
        self.wavelength = QtGui.QRadioButton("wavelength", self)
        self.ev = QtGui.QRadioButton("ev", self)

        self.imageslice = QtGui.QLineEdit()   
        self.maxcolor = QtGui.QLineEdit()
        self.mincolor = QtGui.QLineEdit()
        self.graphslicex = QtGui.QLineEdit()
        self.graphslicey = QtGui.QLineEdit()
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.imageslicelabel,1,0)
        grid.addWidget(self.imageslice,1,1)
        
        grid.addWidget(maxcolorlabel,2,0)
        grid.addWidget(self.maxcolor,2,1)
        
        grid.addWidget(mincolorlabel,3,0)
        grid.addWidget(self.mincolor,3,1)
  
        grid.addWidget(graphslicelabelx,4,0)
        grid.addWidget(self.graphslicex,4,1)
        
        grid.addWidget(graphslicelabely,5,0)
        grid.addWidget(self.graphslicey,5,1)
        
        grid.addWidget(self.wavelength,6,0)
        grid.addWidget(self.ev,6,1)
        
        self.update = QtGui.QPushButton("Update")



        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.update)


        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        grid.addLayout(vbox,7,1)
        
        self.c = Communicate()
        
        self.setLayout(grid)
        self.setGeometry(300,300,50,50)
        self.connect_events()
        self.show()
    
    def connect_events(self):
        self.connect(self.update, QtCore.SIGNAL('clicked()'),
                     self.update_values)
        self.connect(self.ev, QtCore.SIGNAL('clicked()'),
                     self.update_label)
        self.connect(self.wavelength, QtCore.SIGNAL('clicked()'),
                     self.update_label)
        self.c.mincolor_sig.connect(self.update_mincolor_from_control)
        self.c.maxcolor_sig.connect(self.update_maxcolor_from_control)
        self.c.imageslice_sig.connect(self.update_imageslice_from_control)
        self.c.graphslicex_sig.connect(self.update_graphslicex_from_control)
        self.c.graphslicey_sig.connect(self.update_graphslicey_from_control)
        self.ev.clicked.connect(self.display_ev)
        self.wavelength.clicked.connect(self.display_wavelength)
    
    def display_ev(self):
        self.current_tab.show_ev()
    
    def display_wavelength(self):
        self.current_tab.show_wavelength()
    
    def update_label(self):
        if self.ev.isChecked():
            self.imageslicelabel.setText('Image Slice ev:')
        else:
            self.imageslicelabel.setText('Image Slice wavelength:')
    
    def update_values(self):
        """Updates values in main window and clears textboxes"""
        objects = {self.c.maxcolor_sig:self.maxcolor,
             self.c.mincolor_sig:self.mincolor,
             self.c.imageslice_sig:self.imageslice,
             self.c.graphslicex_sig:self.graphslicex,
             self.c.graphslicey_sig:self.graphslicey}

        for signal, item in objects.iteritems():
            if item.text() != '':
                signal.emit()
            else:
                pass
            item.setText('')
            
    def update_graphslicex_from_control(self):
        """
        takes control panel input and changes the current tab's
        x coordinate for the displayed graph
        """
        self.current_tab.xcoordinate = int(self.graphslicex.text())
        try:
            self.current_tab.update_graph(self.current_tab.xcoordinate,
                                                 self.current_tab.ycoordinate)
        except:
            print 'the x coordinate is out of range'
            
    def update_graphslicey_from_control(self):
        """
        takes control panel input and changes the current tab's
        y coordinate for the displayed graph
        """
        self.current_tab.ycoordinate = int(self.graphslicey.text())
        try:
            self.current_tab.update_graph(self.current_tab.xcoordinate,
                                                 self.current_tab.ycoordinate)
        except:
            print 'the y coordinate is out of range'            

    def update_imageslice_from_control(self):
        """
        updates the imageslice from the input from the control panel. 
        the image displayed is the image with the first integer value
        of the input
        """
        if self.current_tab.display_ev:
            text_input = 1240/float(self.imageslice.text())
            xdata = np.array(self.current_tab.xdata[...])
            f = interpolate.interp1d(xdata[::-1], np.arange(1600)) 
            for number in np.arange(1600):
                if number > f(float(text_input)):
                    self.current_tab.imagewavelength = xdata[1600-number]
                    self.current_tab.imageval = 1600-number
                    break            
            self.current_tab.slider.setValue(self.current_tab.imageval)  
            print 'The image ev is now :%0.2f'%float(1240/self.current_tab.imagewavelength)            
        else:
            text_input = float(self.imageslice.text())            
            xdata = np.array(self.current_tab.xdata[...])
            f = interpolate.interp1d(xdata[::-1], np.arange(1600)) 
            for number in np.arange(1600):
                if number > f(float(text_input)):
                    self.current_tab.imagewavelength = xdata[1600-number]
                    self.current_tab.imageval = number
                    break            
            self.current_tab.slider.setValue(self.current_tab.imageval) 
            print 'The image wavelength is now %0.0f'%self.current_tab.imagewavelength

    def update_maxcolor_from_control(self):
        """
        takes control panel input and changes the current tab's
        max color for the displayed graph
        """
        self.current_tab.currentmaxvalcolor = int(self.maxcolor.text())
        self.current_tab.img.set_clim(vmax=self.current_tab.currentmaxvalcolor)
        print 'new max is', self.current_tab.currentmaxvalcolor
        self.current_tab.canvas.draw()

    def update_mincolor_from_control(self):
        """
        takes control panel input and changes the current tab's
        min color for the displayed graph
        """        
        self.current_tab.currentminvalcolor = int(self.mincolor.text())
        self.current_tab.img.set_clim(vmin=self.current_tab.currentminvalcolor)
        print 'new min is', self.current_tab.currentminvalcolor          
        self.current_tab.canvas.draw()
              
          
class Communicate(QtCore.QObject):
    """Connects control panel to main window"""
    maxcolor_sig = QtCore.Signal() 
    mincolor_sig = QtCore.Signal() 
    imageslice_sig = QtCore.Signal() 
    imageslice_ev_sig = QtCore.Signal()
    graphslicex_sig = QtCore.Signal() 
    graphslicey_sig = QtCore.Signal()    