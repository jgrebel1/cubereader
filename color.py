# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 13:33:05 2013

@author: JG
"""
import os
import numpy as np
import matplotlib
from PySide import QtCore
from PySide import QtGui
matplotlib.rcParams['backend.qt4']='PySide'

class ColorWindow(QtGui.QDialog):
    """
    Window with inputs to control color values in an Image
    """
    def __init__(self):
        super(ColorWindow, self).__init__()
        self.setWindowTitle('Set Color Limits')
        self.inputs()

    def inputs(self):
        maxcolorlabel = QtGui.QLabel('Enter Max Color Value:')
        mincolorlabel = QtGui.QLabel('Enter Min Color Value:')
        
        self.maxcolor = QtGui.QLineEdit()
        self.mincolor = QtGui.QLineEdit()
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(maxcolorlabel,1,0)
        grid.addWidget(self.maxcolor,1,1)
        
        self.resetbutton = QtGui.QPushButton("Reset")   
        self.resetvalue = False
        
        grid.addWidget(mincolorlabel,2,0)
        grid.addWidget(self.mincolor,2,1)
        grid.addWidget(self.resetbutton,3,0)

        self.okButton = QtGui.QPushButton("OK")
        self.okButton.setDefault(True)
        self.cancelButton = QtGui.QPushButton("Cancel")


        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)


        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        
        grid.addLayout(vbox,3,1)
        
        self.setLayout(grid)
        self.setGeometry(300,300,50,50)
        self.connect_events()
        self.show()

        
    def connect_events(self):
        self.connect(self.okButton, QtCore.SIGNAL('clicked()'),self.accept)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.reject)
        self.connect(self.resetbutton, QtCore.SIGNAL('clicked()'), self.reset)
    
    def reset(self):
        self.resetvalue = True
        self.accept()
