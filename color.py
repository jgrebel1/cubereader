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

#project specific items
import analysis
import fit_analysis

def auto_adjust(img, data, dataview):
    dataview.auto_color = True
    img.autoscale()
    vmin, vmax = img.get_clim()
    dataview.maxcolor = vmax
    dataview.mincolor = vmin
    
def manual_adjust(img, data, dataview):
    dataview.auto_color = false
    vmin, vmax = img.get_clim()
    dataview.maxcolor = vmax
    dataview.mincolor = vmin

def on_pick_color_cube(event, img, data, data_view):
    """
    Clicking on the color bar will generate three different actions 
    depending on location. The upper third sets the max color value,
    the lower third sets min color value, and the middle pops up a
    window asking for custom values.
    """
    val = event.mouseevent.ydata
    clicked_number = (val*(data_view.maxcolor
                                     -data_view.mincolor)
                           +data_view.mincolor)
    bool_reset_colors = False
    
    if val < .33:
        data_view.mincolor = clicked_number
        mincolor = analysis.colors_calc_min(data_view.mincolor,
                                            data, data_view)
        img.set_clim(vmin=mincolor)

    elif val > .66:
        data_view.maxcolor = clicked_number
        maxcolor = analysis.colors_calc_max(data_view.maxcolor,
                                            data, data_view)
        img.set_clim(vmax=maxcolor)
    else:
        colorwindow = ColorWindow()
        colorwindow.exec_()
        
        if colorwindow.result() and colorwindow.maxcolor.text()!='':
            data_view.maxcolor = float(colorwindow.maxcolor.text())
            img.set_clim(vmax=data_view.maxcolor)
        if colorwindow.result() and colorwindow.mincolor.text()!='':
            data_view.mincolor = float(colorwindow.mincolor.text())
            img.set_clim(vmin=data_view.mincolor)
        if colorwindow.resetvalue:
            reset_colors_cube(img, data, data_view)
        if colorwindow.autoadjust_cb.checkState():
            auto_adjust(img, data, data_view)
        else:
            manual_adjust(img, data, data_view)
    return bool_reset_colors
    
def on_pick_color_fit(event, img, data, data_view):
    """
    Clicking on the color bar will generate three different actions 
    depending on location. The upper third sets the max color value,
    the lower third sets min color value, and the middle pops up a
    window asking for custom values.
    """
    val = event.mouseevent.ydata
    clicked_number = (val*(data_view.maxcolor
                                     -data_view.mincolor)
                           +data_view.mincolor)
    bool_reset_colors = False
    
    if val < .33:
        data_view.mincolor = clicked_number

        img.set_clim(vmin=data_view.mincolor)

    elif val > .66:
        data_view.maxcolor = clicked_number
        img.set_clim(vmax=data_view.maxcolor)
    else:
        colorwindow = ColorWindow()
        colorwindow.exec_()
        
        if colorwindow.result() and colorwindow.maxcolor.text()!='':
            data_view.maxcolor = float(colorwindow.maxcolor.text())
            img.set_clim(vmax=data_view.maxcolor)
        if colorwindow.result() and colorwindow.mincolor.text()!='':
            data_view.mincolor = float(colorwindow.mincolor.text())
            img.set_clim(vmin=data_view.mincolor)
        if colorwindow.resetvalue:
            reset_colors_fit(img, data, data_view)
    return bool_reset_colors
            
def reset_colors_cube(img, data, data_view):
    maxval = analysis.maxval_calc(data, data_view)
    img.set_clim(0, maxval)
    data_view.maxcolor = data_view.maxval
    data_view.mincolor = 0  
    
def reset_colors_fit(img, data, data_view):
    image = fit_analysis.get_image_from_data(data, data_view)
    maxcolor = np.amax(image)
    mincolor = np.amin(image)
    img.set_clim(mincolor, maxcolor)
    data_view.maxcolor = maxcolor
    data_view.mincolor = mincolor
            

class ColorWindow(QtGui.QDialog):
    """
    Window with inputs to control color values in an Image
    """
    def __init__(self):
        super(ColorWindow, self).__init__()
        self.setWindowTitle('Set Color Limits')
        self.inputs()

    def inputs(self):
        """populate screen"""
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
        self.autoadjust_cb = QtGui.QCheckBox("Auto Adjust")
        
        grid.addWidget(mincolorlabel,2,0)
        grid.addWidget(self.mincolor,2,1)
        grid.addWidget(self.autoadjust_cb,3,0)
        grid.addWidget(self.resetbutton,4,0)

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
        
        grid.addLayout(vbox,4,1)
        
        self.setLayout(grid)
        self.setGeometry(300,300,50,50)
        self.connect_events()
        self.show()
        
    def connect_events(self):
        self.connect(self.okButton, QtCore.SIGNAL('clicked()'),self.accept)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.reject)
        self.connect(self.resetbutton, QtCore.SIGNAL('clicked()'), self.reset)
#        self.connect(self.autoadjustbutton,QtCore.SIGNAL('clicked()'), self.auto_adjust)
    
    def reset(self):
        self.resetvalue = True
        self.accept()
