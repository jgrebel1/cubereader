# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 17:28:09 2013

@author: JG
"""

import os
import numpy as np
import matplotlib
from PySide import QtCore
from PySide import QtGui
matplotlib.rcParams['backend.qt4']='PySide'

class PeakBank(QtGui.QDialog):
    """
    Holds peaks 
    """
    def __init__(self):
        super(PeakBank, self).__init__()
        self.setWindowTitle('PeakBank')
        self.cube_peaks = {}
        self.inputs()

    def inputs(self):
        
        self.table = QtGui.QTableWidget()  
        self.table.setColumnCount(1)
        
        self.button_remove_peak = QtGui.QPushButton("&Remove Peak")
        self.button_remove_peak.clicked.connect(self.remove_peak)        
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(self.table,0,0)  
        grid.addWidget(self.button_remove_peak,1,0)
        self.setLayout(grid)
    
    def display_window(self):
        self.show()
    
    def hide_window(self):
        self.hide()
    
    def remove_peak(self):
        self.table.removeRow(self.table.currentRow())
        
        