# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 14:02:13 2014

@author: jg
"""
import sys
from PyQt4 import QtCore
from PyQt4 import QtGui
import matplotlib
from matplotlib import pyplot as plt
#matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

#project specific items

import analysis
import color
import data_view
import plot_tools
import data_holder
import navigation_tools

class ViewData(QtGui.QMainWindow):
    def __init__(self,cube=None, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        if cube == None:
            dialog = QtGui.QFileDialog(self)
            dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
            dialog.setNameFilter('HDF5 (*.hdf5)')
            if dialog.exec_():
                filenames = dialog.selectedFiles()
            for name in filenames:
                if name:
                    filename = name
                else:
                    print 'No file selected'   
            cube = self.load_data(filename)
        self.data = cube[0] 
        self.dataview = cube[1]
        self.maxval = self.dataview.maxval
        self.bool_press = False
        self.create_main_frame()
    
    def create_main_frame(self):
        self.main_frame = QtGui.QWidget()
        
        # Figures
        
        self.fig = plt.figure(figsize=(16.0, 6.0))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)            
        self.img_axes = self.fig.add_subplot(121)
        self.img = plot_tools.initialize_image(self.img_axes,
                                               self.data,
                                               self.dataview)
        self.marker, = self.img_axes.plot(0,0,'wo')
        self.cbar = plt.colorbar(self.img)
        self.set_color_bar_settings()
        self.graph_axes = self.fig.add_subplot(122)  
        self.img2 = plot_tools.initialize_graph(self.graph_axes,
                                                self.data,
                                                self.dataview)
        #
        # Layout with box sizers
        left_spacer = QtGui.QWidget()
        left_spacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                  QtGui.QSizePolicy.Expanding)      
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.set_slider_settings()

        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # Control
        
        self.imageslicelabel= QtGui.QLabel('Image Slice ev:')        
        graphslicelabelx = QtGui.QLabel('Graph Slice X Coordinate:')
        graphslicelabely = QtGui.QLabel('Graph Slice Y Coordinate:')
        self.wavelength = QtGui.QRadioButton("wavelength", self)
        self.ev = QtGui.QRadioButton("ev", self)

        self.imageslice = QtGui.QLineEdit()   
        self.maxcolor = QtGui.QLineEdit()
        self.mincolor = QtGui.QLineEdit()
        self.graphslicex = QtGui.QLineEdit()
        self.graphslicey = QtGui.QLineEdit()
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.imageslicelabel,1,0)
        grid.addWidget(self.imageslice,1,1)
  
        grid.addWidget(graphslicelabelx,1,2)
        grid.addWidget(self.graphslicex,1,3)
        
        grid.addWidget(graphslicelabely,2,2)
        grid.addWidget(self.graphslicey,2,3)
        
        grid.addWidget(self.wavelength,1,4)
        grid.addWidget(self.ev,2,4)
        
        # Organization
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        hbox = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)       
        vbox.addWidget(self.canvas)
        hbox.addWidget(left_spacer)
        hbox.addWidget(self.slider)
        vbox.addLayout(hbox)
        vbox.addLayout(grid)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
        self.connect_events()
        self.connect_shortcuts()
        self.show()
        
    def change_display(self):
        """
        changes the view between ev and wavelength
        """
        self.img2 = plot_tools.change_display(self.graph_axes,
                                               self.data,
                                               self.dataview)
                                               
        self.update_label() 
        
    def closeEvent(self, event):
        """closes hdf5 files before closing window"""
       # try:
       #     if self.data.hdf5:
       #         self.data.hdf5.close()
       # except:
       #     pass
        event.accept()
    

    def connect_events(self):
        """connect to all the events we need"""
        self.cidpress = self.img.figure.canvas.mpl_connect(
            'button_press_event', self.on_press_image)
        self.cidpress2 = self.img.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)
        self.cidpress3 = self.img.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'),
                     self.update_image_from_slider)
        self.cidpick = self.canvas.mpl_connect('pick_event',
                                               self.on_pick_color)
        self.connect(self.imageslice, QtCore.SIGNAL('editingFinished ()'), 
                     self.update_imageslice_from_control)
        self.connect(self.graphslicex, QtCore.SIGNAL('editingFinished ()'), 
                     self.update_graphslicex_from_control)
        self.connect(self.graphslicey, QtCore.SIGNAL('editingFinished ()'), 
                     self.update_graphslicey_from_control)
        self.ev.clicked.connect(self.show_ev)
        self.wavelength.clicked.connect(self.show_wavelength)
            
    def connect_shortcuts(self):
        self.shortcut_up = QtGui.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+Up")),
                                           self)
        self.shortcut_up.activated.connect(self.move_up)
        
        self.shortcut_down = QtGui.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+Down")),
                                           self)
        self.shortcut_down.activated.connect(self.move_down)
        
        self.shortcut_left = QtGui.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+Left")),
                                           self)
        self.shortcut_left.activated.connect(self.move_left)
        
        self.shortcut_right = QtGui.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+Right")),
                                           self)
        self.shortcut_right.activated.connect(self.move_right)
        
    def control_panel_update(self):
        self.control.update_current()
        
    def load_data(self, filename):
        data = data_holder.Data(filename)
        maxval = analysis.find_maxval(data.ycube[...])
        dimension1, dimension2, number_of_slices = analysis.get_dimensions(data.ycube) 
        dimensions = analysis.get_dimensions(data.ycube)
        dataview = data_view.DataView(maxval, dimensions)
        #convert_mutex = QtCore.QMutex()
        #bool_press = False
        return data, dataview
        
    def move_down(self):
        """move marker down and update graph"""
        navigation_tools.move_down(self.dataview, self.dataview.dimension1)
        self.update_graph()
        
    
    def move_left(self):
        """move marker left and update graph"""
        navigation_tools.move_left(self.dataview)
        self.update_graph()
    
    def move_right(self):
        """move marker right and update graph"""
        navigation_tools.move_right(self.dataview, self.dataview.dimension2)
        self.update_graph()
      
    def move_up(self):
        """move marker up and update graph"""
        navigation_tools.move_up(self.dataview)
        self.update_graph()
      
    def on_motion(self, event):        
        """
        dragging the marker will change the graph.
        """
        if self.bool_press is False: return
        if event.inaxes != self.img.axes: return
    
        navigation_tools.change_coordinates(event, self.dataview)
        self.update_graph()
        self.canvas.draw()

        
    def on_pick_color(self, event):
        """
        Clicking on the color bar will generate three different actions 
        depending on location. The upper third sets the max color value,
        the lower third sets min color value, and the middle pops up a
        window asking for custom values.
        """
        color.on_pick_color_cube(event, self.img, self.data, self.dataview)
        self.canvas.draw()      
        
    def on_press_image(self, event):
        """
        This changes the spec graph to theclicked xy coordinate and moves
        the marker on the image.
        
        The .5 addition in the floor function is there to make xdata print 
        correct coordinates.        
        """
        if event.inaxes != self.img.axes: return    
        contains, attrd = self.img.contains(event)
    
        if not contains: return
            
        navigation_tools.change_coordinates(event, self.dataview)
        self.bool_press = True
        self.update_graph()


    def on_release(self, event):
        'on release we reset the press data'
        self.bool_press = False
    
       
    def reset_colors(self):
        color.reset_colors_cube(self.img, self.data, self.dataview)           
                
    def set_color_bar_settings(self):
        self.dataview.maxcolor = self.maxval
        self.dataview.mincolor = 0
        self.cbar.ax.set_picker(5) 

    def set_slider_settings(self):
        self.slider.setRange(1, self.dataview.number_of_slices)
        self.slider.setValue(1)
        self.slider.setTracking(True)

    def show_ev(self):     
        self.dataview.display_ev = True
        self.change_display()
        plot_tools.plot_image(self.img,
                              self.img_axes,
                              self.data,
                              self.dataview)
       
    def show_wavelength(self):      
        self.dataview.display_ev = False
        self.change_display()
        plot_tools.plot_image(self.img,
                              self.img_axes,
                              self.data,
                              self.dataview)
    def update_control(self):
        xdata = analysis.xdata_calc(self.data, self.dataview) 
        slice1 = self.dataview.slider_val
        if self.dataview.display_ev:
            self.imageslice.setText('%0.2f'%float(xdata[slice1]))
        else:
            self.imageslice.setText('%0.0f '%float(xdata[slice1]))
        self.graphslicex.setText('%d'%self.dataview.xcoordinate)
        self.graphslicey.setText('%d'%self.dataview.ycoordinate)
        
    def update_graphslicex_from_control(self):
        """
        takes control panel input and changes the current tab's
        x coordinate for the displayed graph
        """
        try:
            self.dataview.xcoordinate = int(self.graphslicex.text())
        except:
            return
        self.marker.set_xdata(self.dataview.xcoordinate)
        self.update_graph()


            
    def update_graphslicey_from_control(self):
        """
        takes control panel input and changes the current tab's
        y coordinate for the displayed graph
        """
        try:
            self.dataview.ycoordinate = int(self.graphslicey.text())
        except:
            return
        self.marker.set_ydata(self.dataview.ycoordinate)
        self.update_graph()
        
    def update_imageslice_from_control(self):
        """
        updates the imageslice from the input from the control panel. 
        the image displayed is the image with the first integer value
        of the input
        """
        try:
            slice_input = float(self.imageslice.text())
        except:
            return
        if self.dataview.display_ev:
            imageval = analysis.ev_to_index(slice_input, self.data) 
            self.slider.setValue(imageval) 
        else:      
            imageval = analysis.wavelength_to_index(slice_input, self.data)
            self.slider.setValue(self.dataview.number_of_slices - 1-imageval) 
        self.update_graph()

        
    def update_graph(self):
        self.marker.set_xdata(self.dataview.xcoordinate)
        self.marker.set_ydata(self.dataview.ycoordinate)        
        plot_tools.plot_graph(self.img2,
                              self.graph_axes, 
                              self.data,
                              self.dataview)
        self.update_control()
                              
    def update_image_from_slider(self, sliderval):
        
        if self.dataview.display_ev:
            self.dataview.slider_val = sliderval-1
        else:
            self.dataview.slider_val = self.dataview.number_of_slices - sliderval           
        plot_tools.plot_image(self.img,
                              self.img_axes,
                              self.data,
                              self.dataview)
        self.update_control()

    def update_label(self):
        if self.ev.isChecked():
            self.imageslicelabel.setText('Image Slice ev:')
        else:
            self.imageslicelabel.setText('Image Slice wavelength:')
        
#main function to start up program
def main(cube=None):
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
        form = ViewData(cube)
        form.show()
        app.exec_()
        return form
    else:
        form = ViewData(cube)
        #app.form.show()
        return form
    

    
#function to start up program from interactive terminal
def view_data(cube = None):
    #matplotlib.rcParams['mathtext.fontset'] = 'stixsans'
    app = QtCore.QCoreApplication.instance()
    app.form = ViewData(cube)
    #QApplication.setStyle(QStyleFactory.create('Plastique'))
    #QApplication.setPalette(QApplication.style().standardPalette())
    app.form.show()
    #app.exec_()

#if run from commandline then start up by calling main()
if __name__ == "__main__":
    main()
else:
    app = QtCore.QCoreApplication.instance()