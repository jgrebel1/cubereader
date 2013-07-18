# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 14:58:18 2013

@author: JG
"""

from PySide import QtGui


class HeaderWindow(QtGui.QDialog):
        
    def __init__(self,basename, header, parent=None):
        super(HeaderWindow, self).__init__(parent)
        self.header = header
        self.setWindowTitle(basename)
        self.setModal(False)
        self.message()
        
    def message(self):

        text= QtGui.QLabel(self.header)
        text.setWordWrap(True)
        box = QtGui.QVBoxLayout()
        box.addWidget(text)
        self.setLayout(box)
        self.show()
 
