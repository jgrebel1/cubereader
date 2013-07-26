# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 18:26:34 2013

@author: JG
"""
import numpy as np
from PySide import QtCore
from PySide import QtGui

#project specific items
import plot_tools
import control
import analysis


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
        slice_input = float(self.window.imageslice.text())
        if self.current_tab.data_view.display_ev:
            imageval = analysis.ev_to_slice(slice_input, 
                                            self.current_tab.xdata) 
            self.current_tab.slider.setValue(self.tab.number_of_slices - 1 - imageval) 
        else:      
            imageval = analysis.wavelength_to_slice(slice_input, 
                                                    self.current_tab.xdata)
            self.current_tab.slider.setValue(imageval) 

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
    imageslice_sig = QtCore.Signal()
    graphslicex_sig = QtCore.Signal() 
    graphslicey_sig = QtCore.Signal()    