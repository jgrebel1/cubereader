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
    Window with inputs to control color values in an Image
    """
    def __init__(self):
        super(PeakBank, self).__init__()
        self.setWindowTitle('PeakBank')
        self.peaks = {}
        self.inputs()

    def inputs(self):
        
        self.table = QtGui.QTableWidget()  
        #self.table.setRowCount(6)
        self.table.setColumnCount(1)
        
        #self.table.setItem(1, 1, QtGui.QTableWidgetItem(str(self.peaks)))

        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(self.table)  
        self.setLayout(grid)
    
    def display_window(self):
        self.show()
    
    def hide_window(self):
        self.hide()
        
        