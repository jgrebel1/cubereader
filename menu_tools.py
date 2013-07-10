# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 13:58:24 2013

@author: JG
"""
import os
import numpy as np
import matplotlib
from PySide import QtCore
from PySide import QtGui
matplotlib.rcParams['backend.qt4']='PySide'
        
def add_actions(self, target, actions):
    """adds menu items to menu"""
    for action in actions:
        if action is None:
            target.addSeparator()
        else:
            target.addAction(action)    
            
def create_action(self, text, slot=None, shortcut=None, 
                    icon=None, tip=None, checkable=False, 
                    signal="triggered()"):
    """creates clickable menu items"""
    action = QtGui.QAction(text, self)
    if icon is not None:
        action.setIcon(QtGui.QIcon(":/%s.png" % icon))
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    if slot is not None:
        self.connect(action, QtCore.SIGNAL(signal), slot)
    if checkable:
        action.setCheckable(True)
    return action  
