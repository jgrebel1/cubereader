# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 14:02:13 2014

@author: jg
"""
import sys
from PySide import QtCore, QtGui, QtUiTools
import matplotlib
from matplotlib import pyplot as plt
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import pyqtgraph as pg
import numpy as np

#project specific items

import analysis
import color
import data_view
import plot_tools
import data_holder
import navigation_tools
import file_tools
import fit_plot_tools
import fit_analysis
from wraith import spectra_fitting
from wraith import fitting_machinery

class ViewData(QtGui.QMainWindow):
    def __init__(self,cube=None, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        if cube == None:
            filename = file_tools.file_dialog()
            cube = file_tools.load_data(filename)
        self.data = cube[0] 
        self.dataview = cube[1]
        self.maxval = self.dataview.maxval
        self.bool_press = False
        self.create_main_frame()
        self.sizeHint()
    
    def create_main_frame(self):
                # Load Qt UI from .ui file
        ui_loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile("view_data.ui")
        ui_file.open(QtCore.QFile.ReadOnly); 
        self.ui = ui_loader.load(ui_file)
        ui_file.close()
        
        self.ui.setParent(self)

        
        #set up image
        pg.setConfigOptions(useWeave=False)
        self.imv = pg.ImageView()
#         self.vLine_1, self.hLine_1 = self.cross_hair(self.imv)
        self.dot = self.make_dot(self.imv)
        
        self.imv.setMinimumSize(350, 350)
        plot_tools.plot_pyqt(self.imv,self.data , self.dataview)
        self.imv.scene.sigMouseClicked.connect(self.mouseMoved_image)
        self.imv.getView().setMouseEnabled(x=False, y=False)
        

        self.graph = self.setup_graph()
        
        self.ui.image.addWidget(self.imv)
        self.ui.graphs.addWidget(self.graph)
        
        self.set_slider_settings()

        self.connect_events()
#         self.connect_shortcuts()
#         self.show()
        
    def setup_graph(self):
        self.win = pg.GraphicsWindow()
        self.win.setMinimumSize(350, 350)
        self.graph_label = pg.LabelItem(justify='right')
        self.win.addItem(self.graph_label, row = 1, col=1)
        self.p1 = self.win.addPlot(row=2, col=1)
        self.p2 = self.win.addPlot(row=3, col=1)
        self.p1.vb.setMouseEnabled(x=False)

        # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this 
        # item when doing auto-range calculations.
        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        self.p2.addItem(self.region, ignoreBounds=True)
        self.p1.setAutoVisible(y=True)
        
        #plot data
        self.curve1 = self.p1.plot()
        self.curve2 = self.p2.plot()
        plot_tools.graph_pyqt(self.curve1, self.curve2, self.data, self.dataview)

        #add line inspection tool
        self.vLine_2 = pg.InfiniteLine(angle=90, movable=False)
        self.p1.addItem(self.vLine_2, ignoreBounds=True)
        self.p1.scene().sigMouseMoved.connect(self.mouseMoved_graph)

        return self.win

        
    def change_display(self):
        """
        changes the view between ev and wavelength
        """
        self.img2 = plot_tools.change_display(self.graph_axes,
                                               self.data,
                                               self.dataview)
                                               
        self.update_label() 
        
    def closeEvent(self, event):
        event.accept()
        #self.hide()
    

    def connect_events(self):
        """connect to all the events we need"""
        self.connect(self.ui.slider, QtCore.SIGNAL('valueChanged(int)'),
                     self.update_image_from_slider)
        self.connect(self.ui.imageslice, QtCore.SIGNAL('editingFinished ()'), 
                     self.update_imageslice_from_control)
        self.region.sigRegionChanged.connect(self.update_graph_view)
        self.p1.sigRangeChanged.connect(self.update_region)
        self.connect(self.ui.graphslicex, QtCore.SIGNAL('editingFinished ()'), 
                     self.update_graphslicex_from_control)
        self.connect(self.ui.graphslicey, QtCore.SIGNAL('editingFinished ()'), 
                     self.update_graphslicey_from_control)
        self.ui.ev.clicked.connect(self.show_ev)
        self.ui.wavelength.clicked.connect(self.show_wavelength)
            
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
        
    def cross_hair(self, plot):
        vLine = pg.InfiniteLine(angle=90, movable=True)
        hLine = pg.InfiniteLine(angle=0, movable=True)
        plot.addItem(vLine)#, ignoreBounds=True)
        plot.addItem(hLine)#, ignoreBounds=True)
        return vLine, hLine
    
    def make_dot(self, plot):
        
        x = self.dataview.x + .5
        y = self.dataview.y + .5
        dot = pg.CircleROI(pos=(x,y),size=(5,5) )
        plot.addItem(dot)

        return dot
        
    def mouseMoved_graph(self, evt):
        pos = evt
        if self.p1.sceneBoundingRect().contains(pos):
            mousePoint = self.p1.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            ydata = analysis.ydata_calc(self.data, self.dataview)
            if index > 0 and index < len(ydata):
                self.graph_label.setText("<span style='font-size: 12pt'>x=%0.1f,  y1=%0.3f" % (mousePoint.x(), ydata[index]))
            self.vLine_2.setPos(mousePoint.x())

            
    def mouseMoved_image(self, evt):
        pos = evt.pos()
        if self.imv.getImageItem().sceneBoundingRect().contains(pos):
            mousePoint = self.imv.getView().mapSceneToView(pos)
            self.dataview.x = np.floor(mousePoint.x())
            self.dataview.y = np.floor(mousePoint.y())
            self.update_graph()
            
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
        
    def set_slider_settings(self):
        self.ui.slider.setRange(1, self.dataview.number_of_slices)
        self.ui.slider.setValue(1)
        self.ui.slider.setTracking(True)
        
    def show(self):
        self.ui.show()

    def show_ev(self):     
        self.dataview.display_ev = True
        self.change_display()
       
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
            self.ui.imageslice.setText('%0.2f'%float(xdata[slice1]))
        else:
            self.ui.imageslice.setText('%0.0f '%float(xdata[slice1]))
        self.ui.graphslicex.setText('%d'%self.dataview.x)
        self.ui.graphslicey.setText('%d'%self.dataview.y)
        
    def update_graphslicex_from_control(self):
        """
        takes control panel input and changes the current tab's
        x coordinate for the displayed graph
        """
        try:
            self.dataview.x = int(self.ui.graphslicex.text())
        except:
            return
        self.marker.set_xdata(self.dataview.x)
        try:
            self.update_graph()
        except ValueError:
            return


            
    def update_graphslicey_from_control(self):
        """
        takes control panel input and changes the current tab's
        y coordinate for the displayed graph
        """
        try:
            self.dataview.y = int(self.ui.graphslicey.text())
        except:
            return
        self.marker.set_ydata(self.dataview.y)
        try:
            self.update_graph()
        except ValueError:
            return
        
    def update_imageslice_from_control(self):
        """
        updates the imageslice from the input from the control panel. 
        the image displayed is the image with the first integer value
        of the input
        """
        try:
            slice_input = float(self.ui.imageslice.text())
        except Exception as e:
            print e
        if self.dataview.display_ev:
            imageval = analysis.ev_to_index(slice_input, self.data) 
            self.ui.slider.setValue(imageval) 
        else:      
            imageval = analysis.wavelength_to_index(slice_input, self.data)
            self.ui.slider.setValue(self.dataview.number_of_slices - 1-imageval) 
#         self.update_graph()
        plot_tools.plot_pyqt(self.imv,self.data, self.dataview)
        
    def update_graph(self):
        x = self.dataview.x+.5
        y = self.dataview.y+.5
#         self.vLine_1.setPos(x)
#         self.hLine_1.setPos(y)
        self.dot.setPos((x,y))
        plot_tools.graph_pyqt(self.curve1, self.curve2, self.data, self.dataview)
        self.update_control()
        
    def update_graph_view(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.p1.setXRange(minX, maxX, padding=0)    
    
    def update_region(self, window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)       
                              
    def update_image_from_slider(self, sliderval):
        
        if self.dataview.display_ev:
            self.dataview.slider_val = sliderval-1
        else:
            self.dataview.slider_val = self.dataview.number_of_slices - sliderval           
#         plot_tools.plot_image(self.img,
#                               self.img_axes,
#                               self.data,
#                               self.dataview)
        plot_tools.plot_pyqt(self.imv,self.data, self.dataview)
        self.update_control()

    def update_label(self):
        if self.ev.isChecked():
            self.imageslicelabel.setText('Image Slice ev:')
        else:
            self.imageslicelabel.setText('Image Slice wavelength:')
            
            
class ViewFit(QtGui.QMainWindow):

    def __init__(self,fit=None,data=None, parent=None):
        #super(CubeFit, self).__init__(parent) 
        QtGui.QMainWindow.__init__(self, parent)
        #if fit==None:
        #    filename = file_tools.file_dialog('Please select fit file')
        #    fit = file_tools.load_fit(filename)
        #if data == None:
        #    filename = file_tools.file_dialog('Please select data file')
        #    fit = file_tools.load_fit(filename)
        self.fit_data = fit[0] 
        self.fit_dataview = fit[1]
        self.cube_data = data[0]
        self.cube_dataview = data[1]
        self.peak_list = self.get_peak_list(self.fit_data)  
        self.variable_list = self.get_variable_list(self.fit_data, self.fit_dataview)
        self.load_spectrum()
        self.load_peaks()
        self.bool_press = False
        self.make_frame()
        
    def make_frame(self):
        """populate screen"""
        self.main_frame = QtGui.QWidget()
        self.fig = plt.figure(figsize=(16.0, 6.0))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)            
        self.img_axes = self.fig.add_subplot(121)
        self.img = fit_plot_tools.initialize_image(self.img_axes,
                                                   self.fit_data,
                                                   self.fit_dataview)
        self.marker, = self.img_axes.plot(0,0,'wo')
        self.cbar = plt.colorbar(self.img)
        self.cbar.ax.set_picker(5) 
        self.graph_axes = self.fig.add_subplot(122) 
        self.img2 = plot_tools.initialize_graph(self.graph_axes,
                                                self.cube_data,
                                                self.cube_dataview)
        self.plot_peaks()
        
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        
        self.dropdown_peaks = QtGui.QComboBox()
        self.dropdown_peaks.addItems(self.peak_list)   
        self.dropdown_peaks.currentIndexChanged.connect(self.peak_changed)
        
        self.dropdown_variables = QtGui.QComboBox()
        self.dropdown_variables.addItems(self.variable_list)
        self.dropdown_variables.currentIndexChanged.connect(self.variable_changed)
        
        self.button_display_residuals = QtGui.QPushButton('Display Integrated\nResiduals')
        self.button_display_residuals.clicked.connect(self.display_residuals)
        
        self.button_display_attributes = QtGui.QPushButton('Display Peak\nAttributes')
        self.button_display_attributes.clicked.connect(self.display_attributes)
        
        self.label_min_filter = QtGui.QLabel('Min Filter')
        self.textbox_min_filter = QtGui.QLineEdit(str(-1))

        self.textbox_min_filter.editingFinished.connect(self.update_filter_settings)
        
        self.label_max_filter = QtGui.QLabel('Max Filter')
        self.textbox_max_filter = QtGui.QLineEdit(str(1))
        self.textbox_max_filter.editingFinished.connect(self.update_filter_settings)
        
        self.button_filter_from_residuals = QtGui.QPushButton('Filter From Residuals')
        self.button_filter_from_residuals.clicked.connect(self.filter_from_residuals)
        
        #self.button_test = QtGui.QPushButton('test')
        #self.button_test.clicked.connect(self.test)
        
        
                     
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.mpl_toolbar)       
        vbox1.addWidget(self.canvas)
       
        filter_hbox1 = QtGui.QHBoxLayout()
        filter_hbox1.addWidget(self.label_max_filter)
        filter_hbox1.addWidget(self.textbox_max_filter)        
                
        filter_hbox2 = QtGui.QHBoxLayout()
        filter_hbox2.addWidget(self.label_min_filter)
        filter_hbox2.addWidget(self.textbox_min_filter)        
        
        vbox2 = QtGui.QVBoxLayout()
        vbox2.addWidget(self.dropdown_peaks)
        vbox2.addWidget(self.dropdown_variables)
        vbox2.addWidget(self.button_display_residuals)
        vbox2.addWidget(self.button_display_attributes)
        vbox2.addLayout(filter_hbox1)
        vbox2.addLayout(filter_hbox2)
        vbox2.addWidget(self.button_filter_from_residuals)
        #vbox2.addWidget(self.button_test)

        
        grid.addLayout(vbox1,0,0)
        grid.addLayout(vbox2,0,1)
        
        self.main_frame.setLayout(grid)
        self.setCentralWidget(self.main_frame)
        self.connect_events()
        self.connect_shortcuts()
        self.show()
                                               
    def connect_events(self):
        """connect to all the events we need"""
        self.cidpress = self.img.figure.canvas.mpl_connect(
            'button_press_event', self.on_press_image)
        self.cidpress2 = self.img.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)
        self.cidpress3 = self.img.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidpick = self.canvas.mpl_connect('pick_event',
                                               self.on_pick_color)
                                               
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
                                               
    def display_attributes(self):
        """popup peak attributes"""
        peak = self.fit_dataview.current_peak
        function = self.fit_data.peaks[peak].attrs['function']
        name = self.fit_data.peaks[peak].attrs['name']
        penalty_function = self.fit_data.peaks[peak].attrs['penalty_function']
        ranges = self.fit_data.peaks[peak].attrs['ranges']
        variables = self.fit_data.peaks[peak].attrs['variables']
        function_msg = "Function is " + str(function)
        name_msg = "Name is " + str(name)
        penalty_function_msg = "Penalty Function is " + str(penalty_function)
        ranges_msg = "Ranges are " + str(ranges)
        variables_msg = "Variables are "  + str(variables)
        full_msg = function_msg + '\n' + name_msg + '\n' \
                    +penalty_function_msg + '\n' + ranges_msg \
                    + '\n' + variables_msg
        QtGui.QMessageBox.about(self,"Attributes for %s"%peak,
                                full_msg.strip()) 
                                
    def display_residuals(self):
        fit_plot_tools.set_image_from_residuals(self.img, self.img_axes,
                                                self.fit_data, self.fit_dataview)
                                      
    def filter_from_residuals(self):
        """
        display filtered image. Filter is from residual bounds input
        by user
        """
        filtered_current_image = fit_analysis.filter_current_image_from_residuals(self.fit_dataview.min_filter,
                                                                                  self.fit_dataview.max_filter,
                                                                                  self.fit_data,
                                                                                  self.fit_dataview)
        fit_plot_tools.set_image_from_input(self.img, self.img_axes,
                                            filtered_current_image,
                                            self.fit_dataview)
        self.reset_colors()
        self.canvas.draw()        
        
    def get_peak_list(self, fit_data):
        """generates list of peak names in hdf5 file"""
        peak_list = []
        for peak in fit_data.peaks.keys():
            peak_list.append(peak)
        
        return peak_list
        
    def get_variable_list(self, fit_data, fit_dataview):
        """generates list of variable names for a given peak"""
        variable_list = []
        peak = fit_data.peaks[fit_dataview.current_peak]
        for variable in peak.keys():
            variable_list.append(variable)
        return variable_list 
        
    def load_peaks(self):
        """
        populates wraith spectrum with peaks from current x and y
        coordinates
        """
        peak_list = fit_analysis.spectrum_from_data(self.peak_list,
                                                   self.fit_data, 
                                                   self.cube_dataview)         
        for peak in peak_list:
              self.spectrum.peaks.peak_list.append(fitting_machinery.Peak(self.spectrum))
              self.spectrum.peaks.peak_list[-1].set_spec(peak)
        #spectrum.peaks.optimize_fit(spectrum.E(),spectrum.nobg())
          
    def load_spectrum(self):
        """initializes a wraith spectrum"""
        self.spectrum = spectra_fitting.Spectrum()
        xdata = analysis.xdata_calc(self.cube_data, self.cube_dataview)
        ydata = analysis.ydata_calc(self.cube_data, self.cube_dataview) 
        self.spectrum.EE = xdata
        self.spectrum.data = ydata   
        
    def move_down(self):
        """move marker down and update graph"""
        navigation_tools.move_down(self.cube_dataview, self.cube_dataview.dimension1)
        self.update_graph()
        self.canvas.draw()        
    
    def move_left(self):
        """move marker left and update graph"""
        navigation_tools.move_left(self.cube_dataview)
        self.update_graph()
        self.canvas.draw()
    
    def move_right(self):
        """move marker right and update graph"""
        navigation_tools.move_right(self.cube_dataview, self.cube_dataview.dimension2)
        self.update_graph()
        self.canvas.draw()
      
    def move_up(self):
        """move marker up and update graph"""
        navigation_tools.move_up(self.cube_dataview)
        self.update_graph()
        self.canvas.draw()
      
    def on_motion(self, event):        
        """
        dragging the marker will change the graph.
        """
        if self.bool_press is False: return
        if event.inaxes != self.img.axes: return
    
        navigation_tools.change_coordinates(event, self.fit_dataview)
        self.update_graph()
        self.canvas.draw()

        
    def on_pick_color(self, event):
        """
        Clicking on the color bar will generate three different actions 
        depending on location. The upper third sets the max color value,
        the lower third sets min color value, and the middle pops up a
        window asking for custom values.
        """
        color.on_pick_color_fit(event, self.img,
                            self.fit_data,self.fit_dataview)     
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
            
        navigation_tools.change_coordinates(event, self.cube_dataview)
        self.bool_press = True
        self.update_graph()
        self.canvas.draw()


    def on_release(self, event):
        'on release we reset the press data'
        self.bool_press = False
 
    def peak_changed(self, index):
        """
        changing dropdown peak generates new variable list
        
        """
        self.fit_dataview.current_peak = self.peak_list[index]
        fit_plot_tools.set_image_from_data(self.img, self.img_axes,
                                  self.fit_data, self.fit_dataview)
        self.variable_list = self.get_variable_list(self.fit_data,
                                                    self.fit_dataview)
        self.dropdown_variables.clear()
        self.dropdown_variables.addItems(self.variable_list)
        
    def plot_peaks(self):
        """plot all peaks in spectrum to graph"""
        self.spectrum.plot_individual_peaks(scale=1.0,
                                            axes=self.graph_axes, offset=0.0)
   
    def reset_colors(self):
        color.reset_colors_fit(self.img, self.fit_data, self.fit_dataview)
        
    def update_filter_settings(self):
        """
        updates data view to have correct values from text boxes.
        data_stores input values in wavelength.
        """
        min_filter = float(self.textbox_min_filter.text())
        max_filter = float(self.textbox_max_filter.text())
        self.fit_dataview.min_filter = min_filter
        self.fit_dataview.max_filter = max_filter

    def update_graph(self):
        self.marker.set_xdata(self.cube_dataview.x)
        self.marker.set_ydata(self.cube_dataview.y)

        plot_tools.initialize_graph(self.graph_axes,
                                    self.cube_data,
                                    self.cube_dataview)
        self.spectrum.clear_peaks()
        self.load_peaks()        
        self.plot_peaks()                  
        
    def variable_changed(self, index):
        """changing variable updates image"""
        self.fit_dataview.current_variable = self.variable_list[index]
        fit_plot_tools.set_image_from_data(self.img, self.img_axes,
                                  self.fit_data, self.fit_dataview)
        
#main function to start up programs
def data(cube=None, parent = None):
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
        form = ViewData(cube, parent)
        form.show()
        app.exec_()
        return form
    else:
        form = ViewData(cube)
        form.show()
        app.exec_()
        return form
    
def fit(fit=None, cube=None):
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
        form = ViewFit(fit, cube)
        form.show()
        app.exec_()
        return form
    else:
        form = ViewFit(fit, cube)
        app.exec_()
        return form
