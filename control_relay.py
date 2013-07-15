# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 18:26:34 2013

@author: JG
"""
import numpy as np
from scipy import interpolate
from PySide import QtCore
from PySide import QtGui

#project specific items
import plot_tools
import control


class ControlRelay(QtCore.QObject):
    
    def __init__(self,tab):
        self.tab = tab
        self.window = control.ControlWindow()
        self.current_tab = self.tab.currentWidget()
        self.c = Communicate()
        self.connect_events()
    
    
    def connect_events(self):
        self.window.connect(self.window.update, QtCore.SIGNAL('clicked()'),
                                  self.update_values)
        self.c.mincolor_sig.connect(self.update_mincolor_from_control)
        self.c.maxcolor_sig.connect(self.update_maxcolor_from_control)
        self.c.imageslice_sig.connect(self.update_imageslice_from_control)
        self.c.graphslicex_sig.connect(self.update_graphslicex_from_control)
        self.c.graphslicey_sig.connect(self.update_graphslicey_from_control)
        self.window.ev.clicked.connect(self.display_ev)
        self.window.wavelength.clicked.connect(self.display_wavelength)
        
    def update_current(self):
        self.current_tab = self.tab.currentWidget()
        if self.current_tab.data_view.display_ev:
            self.window.ev.setChecked(True)
        else:
            self.window.wavelength.setChecked(True)
    def display_ev(self):
        self.current_tab.show_ev()
    
    def display_wavelength(self):
        self.current_tab.show_wavelength()

    def update_graphslicex_from_control(self):
        """
        takes control panel input and changes the current tab's
        x coordinate for the displayed graph
        """

        self.current_tab.data_view.xcoordinate = int(self.window.graphslicex.text())
        plot_tools.plot_graph(self.current_tab.img2,
                              self.current_tab.graph_axes,
                              self.current_tab.ycube,
                              self.current_tab.xdata,
                              self.current_tab.data_view)

            
    def update_graphslicey_from_control(self):
        """
        takes control panel input and changes the current tab's
        y coordinate for the displayed graph
        """
        self.current_tab.data_view.ycoordinate = int(self.window.graphslicey.text())
        plot_tools.plot_graph(self.current_tab.img2,
                              self.current_tab.graph_axes,
                              self.current_tab.ycube,
                              self.current_tab.xdata,
                              self.current_tab.data_view)   


    def update_imageslice_from_control(self):
        """
        updates the imageslice from the input from the control panel. 
        the image displayed is the image with the first integer value
        of the input
        """
        if self.current_tab.data_view.display_ev:
            text_input = 1240/float(self.window.imageslice.text())
            xdata = np.array(self.current_tab.xdata[...])
            f = interpolate.interp1d(xdata[::-1], np.arange(1600)) 
            if text_input > xdata[0]:
                imagewavelength = xdata[0]
                imageval = 1599
            elif text_input < xdata[-1]:
                imagewavelength = xdata[1599]
                imageval = 0
            else:   
                for number in np.arange(1600):
                    if number > f(text_input):
                        imagewavelength = xdata[1600-number]
                        imageval = 1599-number
                        break            
            self.current_tab.slider.setValue(imageval)  
            print 'The image ev is now :%0.2f'%float(1240/imagewavelength)            
        else:
            text_input = float(self.window.imageslice.text())            
            xdata = np.array(self.current_tab.xdata[...])
            f = interpolate.interp1d(xdata[::-1], np.arange(1600)) 
            if text_input > xdata[0]:
                imagewavelength = xdata[0]
                imageval = 1599
            elif text_input < xdata[-1]:
                imagewavelength = xdata[1599]
                imageval = 0
            else:
                for number in np.arange(1600):
                    if number > f(text_input):
                        imagewavelength = xdata[1600-number]
                        imageval = number
                        break            
            self.current_tab.slider.setValue(imageval) 
            print 'The image wavelength is now %0.0f'%imagewavelength

    def update_maxcolor_from_control(self):
        """
        takes control panel input and changes the current tab's
        max color for the displayed graph
        """
        self.current_tab.data_view.currentmaxvalcolor = int(self.window.maxcolor.text())
        plot_tools.plot_image(self.current_tab.img,
                              self.current_tab.img_axes,
                              self.current_tab.ycube,
                              self.current_tab.xdata,
                              self.current_tab.data_view)  

    def update_mincolor_from_control(self):
        """
        takes control panel input and changes the current tab's
        min color for the displayed graph
        """        
        self.current_tab.data_view.currentminvalcolor = int(self.window.mincolor.text())
        plot_tools.plot_image(self.current_tab.img,
                              self.current_tab.img_axes,
                              self.current_tab.ycube,
                              self.current_tab.xdata,
                              self.current_tab.data_view)  
              
    def update_values(self):
        """Updates values in main window and clears textboxes"""
        objects = {self.c.maxcolor_sig:self.window.maxcolor,
             self.c.mincolor_sig:self.window.mincolor,
             self.c.imageslice_sig:self.window.imageslice,
             self.c.graphslicex_sig:self.window.graphslicex,
             self.c.graphslicey_sig:self.window.graphslicey}

        for signal, item in objects.iteritems():
            if item.text() != '':
                signal.emit()
            else:
                pass
            item.setText('')
            

          
class Communicate(QtCore.QObject):
    """Connects control panel to main window"""
    maxcolor_sig = QtCore.Signal() 
    mincolor_sig = QtCore.Signal() 
    imageslice_sig = QtCore.Signal() 
    imageslice_ev_sig = QtCore.Signal()
    graphslicex_sig = QtCore.Signal() 
    graphslicey_sig = QtCore.Signal()    