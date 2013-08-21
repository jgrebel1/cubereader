# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 14:21:44 2013

@author: JG
"""
from PySide import QtCore
from PySide import QtGui

class GenericThread(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    #def __del__(self):
        #self.wait()

    def run(self):
        self.function(*self.args,**self.kwargs)
        return