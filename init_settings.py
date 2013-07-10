# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 13:29:29 2013

@author: JG
"""


import matplotlib
from PySide import QtCore
from PySide import QtGui
matplotlib.rcParams['backend.qt4']='PySide'

#project specific items

                 
class InitialSettingsWindow(QtGui.QDialog):
    """Pop-up window confirming image dimensions"""
    def __init__(self, dimension1, dimension2, global_bool, parent=None):
        super(InitialSettingsWindow, self).__init__(parent)
        self.setWindowTitle('Initial Settings')
        self.dimension1 = dimension1
        self.dimension2 = dimension2
        self.global_bool = global_bool
        self.inputs()
        
    def inputs(self):
        
        dimension1label = QtGui.QLabel('Enter Dimension 1:')
        dimension2label = QtGui.QLabel('Enter Dimension 2:')
        
        self.dimension1Edit = QtGui.QLineEdit("%d"%self.dimension1)
        self.dimension2Edit = QtGui.QLineEdit("%d"%self.dimension2)

        self.globalwavelength = QtGui.QCheckBox('Global Wavelength')
        self.globalwavelength.setChecked(self.global_bool)
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(dimension1label,1,0)
        grid.addWidget(self.dimension1Edit,1,1)
        
        grid.addWidget(dimension2label,2,0)
        grid.addWidget(self.dimension2Edit,2,1)
        
        grid.addWidget(self.globalwavelength,3,0)
        
        self.okButton = QtGui.QPushButton("OK")
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
        self.setGeometry(400,400,50,50)
        self.connect_events()
        self.show()

        
    def connect_events(self):
          self.connect(self.okButton, QtCore.SIGNAL('clicked()'),self.accept)
          self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.reject)
