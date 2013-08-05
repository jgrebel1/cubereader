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
import control_relay

class ControlWindow(QtGui.QDialog):
        
    def __init__(self, parent=None):
        super(ControlWindow, self).__init__(parent)
        self.setWindowTitle('Control Panel')
        self.setModal(False)
        self.inputs()
        
    def inputs(self):

        self.imageslicelabel= QtGui.QLabel('Image Slice ev:')
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
    
        
        self.setLayout(grid)
        self.setGeometry(300,300,50,50)
        self.connect_events()
        self.show()
    
    def connect_events(self):
        self.connect(self.ev, QtCore.SIGNAL('clicked()'),
                     self.update_label)
        self.connect(self.wavelength, QtCore.SIGNAL('clicked()'),
                     self.update_label)
 
    def update_label(self):
        if self.ev.isChecked():
            self.imageslicelabel.setText('Image Slice ev:')
        else:
            self.imageslicelabel.setText('Image Slice wavelength:')
    
