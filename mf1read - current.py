"""
@authors: Joel Grebel and Aaron Hammack

used Eli Bendersky's (eliben@gmail.com) embeding matplotlib into pyqt 
Gui Demo for much of the structure.
"""

import os
import numpy as np
from matplotlib import pyplot as plt
import re
from PySide import QtCore
from PySide import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

#project specific items

import cube_loader_nonglobal
import cube_loader_global

class AppForm(QtGui.QMainWindow):
    """Gui Application to display Data Cube"""
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle('Mf1 File Reader')

        self.create_menu()
        self.create_main_frame()
        #self.create_status_bar()


    def create_main_frame(self):
        """adds all the graphs/controllers to the main window"""
        self.main_frame = QtGui.QWidget()
        self.filename, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        #self.filename = "C:/Users/JG/Documents/College Documents/2013 - Summer/lbl/Programming project/spectral maps/RHK_002.mf1"
        print self.filename
        self.open_initial_settings()
        
        self.mf1 = self.make_cube()
            
        self.fig = plt.figure(figsize=(16.0, 6.0))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)            

        self.ax = self.fig.add_subplot(121)

        

        self.img = self.show_single_slice(self.ax,self.mf1.ycube, 1)
        self.cbar = plt.colorbar(self.img)
        self.set_color_bar_settings()

        self.ax2 = self.fig.add_subplot(122)        
        self.show_single_graph(self.ax2, 0, 0)

        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        #
        # Layout with box sizers
        left_spacer = QtGui.QWidget()
        left_spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.set_slider_settings()
        self.connect_events()
        
        hbox = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)       
        vbox.addWidget(self.canvas)
        hbox.addWidget(left_spacer)
        hbox.addWidget(self.slider)
        vbox.addLayout(hbox)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

        #self.show_slices()

    def add_actions(self, target, actions):
        """adds menu items to menu"""
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
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

    def create_menu(self):
        """makes the menu toolbar on the top of the main window"""
        self.file_menu = self.menuBar().addMenu("&File")
        
        quit_action = self.create_action("&Quit", slot=self.close, 
                                         shortcut="Ctrl+Q", 
                                         tip="Close the application")
        control_action = self.create_action("&Open Control Panel",
                                            slot = self.open_control,
                                            shortcut="Ctrl+P",
                                            tip="Open the Control Panel")
        self.add_actions(self.file_menu, 
            (control_action,None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About Mf1Reader')
        self.add_actions(self.help_menu, (about_action,))

    def dimension_finder(self):
        """finds the picture dimension"""
        dimension = re.search('\d+x\d+',self.text_header).group()
        dimension1 = re.findall('\d+',dimension)[0]
        dimension1 = float(dimension1)
        dimension2 = re.findall('\d+',dimension)[1]
        dimension2 = float(dimension2)
        return (dimension1,dimension2)
        
    def disconnect(self):
        """disconnect all the stored connection ids"""
        self.img.figure.canvas.mpl_disconnect(self.cidpress) 
        
    def make_cube(self):
        if self.globalwavelength:
            mf1 = cube_loader_global.Mf1File(self.filename, self.dimension1, self.dimension2)
        else:
            mf1 = cube_loader_nonglobal.Mf1File(self.filename, self.dimension1, self.dimension2)
        return mf1

    def open_control(self):
        self.control = ControlWindow()
        self.control.c.mincolor_sig.connect(self.update_mincolor)
        self.control.c.maxcolor_sig.connect(self.update_maxcolor)
        self.control.c.imageslice_sig.connect(self.update_imageslice)
        self.control.c.graphslicex_sig.connect(self.update_graphslicex)
        self.control.c.graphslicey_sig.connect(self.update_graphslicey)
        
    def open_file(self):
        """possible future menu item. Not implemented yet."""
        openFile = QtGui.QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        #self.filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
        #                                                         '/home')
        #newfile = Mf1File(self.filename)
    
    def open_initial_settings(self):
        """
        calls the Initial Settings window and changes the default values
        if necessary.
        """
        with open(self.filename,'rb') as fid:
            self.text_header=fid.read(2048)
        try:
            self.dimension1, self.dimension2 = self.dimension_finder()
        except:
            self.dimension1, self.dimension2 = 0,0
            
        self.initialsettings = InitialSettingsWindow(self.dimension1, self.dimension2) 
        self.initialsettings.exec_()
        
        if self.initialsettings.result() and self.initialsettings.dimension1Edit.text()!='':
            print 'Dimension 1 is now ', self.initialsettings.dimension1Edit.text()
            self.dimension1 = int(self.initialsettings.dimension1Edit.text())
        if self.initialsettings.result() and self.initialsettings.dimension2Edit.text()!='':   
            print 'Dimension 2 is now ', self.initialsettings.dimension2Edit.text()
            self.dimension2 = int(self.initialsettings.dimension2Edit.text())
        if self.initialsettings.result():
            self.globalwavelength = self.initialsettings.globalwavelength.isChecked()

    def update_graphslicex(self):
        self.xcoordinate = int(self.control.graphslicex.text())
        try:
            self.update_single_graph(self.xcoordinate,self.ycoordinate)
            self.canvas.draw()
        except:
            print 'the x coordinate is out of range'
            
    def update_graphslicey(self):
        self.ycoordinate = int(self.control.graphslicey.text())
        try:
            self.update_single_graph(self.xcoordinate,self.ycoordinate)
            self.canvas.draw()
        except:
            print 'the y coordinate is out of range'            

    def update_imageslice(self):
        """
        updates the imageslice from the input from the control panel. 
        the image displayed is the image with the first integer value
        of the input
        """
        self.imagewavelength = int(self.control.imageslice.text())
        try:
            self.imageval = np.where(np.rint((self.mf1.xdata))==self.imagewavelength)[0][0]
            self.slider.setValue(1599 - self.imageval)
            print 'The image wavelength is now', self.imagewavelength
        except:
            print 'wavelength is out of range'



    def update_maxcolor(self):
        self.currentmaxval = int(self.control.maxcolor.text())
        self.img.set_clim(vmax=self.currentmaxval)
        print 'new max is', self.currentmaxval
        self.canvas.draw()

    def update_mincolor(self):
        self.currentminval = int(self.control.mincolor.text())
        self.img.set_clim(vmin=self.currentminval)
        print 'new min is', self.currentminval
        self.canvas.draw()
            
   
    def on_about(self):
        """Displays pop-up about box"""
        msg = """A File Reader for Mf1 Files. Joel Grebel and Aaron Hammack
        """
        QtGui.QMessageBox.about(self, "About the Mf1Reader", msg.strip())    
        
    def connect_events(self):
        """connect to all the events we need"""
        self.cidpress = self.img.figure.canvas.mpl_connect(
            'button_press_event', self.on_press_image)
        self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'),
                     self.update_single_slice)
        self.cidpick = self.canvas.mpl_connect('pick_event', self.on_pick_color)
        
    def on_pick_color(self, event):
        """
        Clicking on the color bar will generate three different actions 
        depending on location. The upper third sets the max color value,
        the lower third sets min color value, and the middle pops up a
        window asking for custom values.
        """
        self.val = event.mouseevent.ydata
        self.clicked_number = (self.val*(self.currentmaxval-self.currentminval)
                               +self.currentminval)
        
        if self.val < .33:
            self.currentminval = self.clicked_number
            self.img.set_clim(vmin=self.clicked_number)
            print 'new min is ', self.currentminval

        elif self.val > .66:
            self.currentmaxval = self.clicked_number
            self.img.set_clim(vmax=self.clicked_number)
            print 'new max is ', self.currentmaxval
        else:
            self.colorwindow = ColorWindow()
            self.colorwindow.exec_()
            if self.colorwindow.result() and self.colorwindow.maxcolor.text()!='':
                self.currentmaxval = int(self.colorwindow.maxcolor.text())
                self.img.set_clim(vmax=self.currentmaxval)
                print 'new max is', self.currentmaxval
            if self.colorwindow.result() and self.colorwindow.mincolor.text()!='':
                self.currentminval = int(self.colorwindow.mincolor.text())
                self.img.set_clim(vmin=self.currentminval)
                print 'new min is', self.currentminval
            if self.colorwindow.resetvalue:
                self.reset_colors()
        self.canvas.draw()      
        
    def on_press_image(self, event):
        """
        This gets click data from graph.
        The .5 addition in the floor function is there to make xdata print 
        correct coordinates.
        This also changes the spec graph to the clicked xy coordinate.
        """

        if event.inaxes != self.img.axes: return

        contains, attrd = self.img.contains(event)
        if not contains: return

        #xcoordinates start at 0
        #ycoordinates start at 0
        print 'xcoordinate=%d, ycoordinate=%d'%(event.xdata + .5,
                                                event.ydata + .5)
        self.xcoordinate = np.floor(event.xdata + .5)
        self.ycoordinate = np.floor(event.ydata + .5)
        self.update_single_graph(self.xcoordinate, self.ycoordinate)
        self.img.figure.canvas.draw()
        
    def reset_colors(self):
        self.img.set_clim(0, self.maxval)
        

        
    def set_color_bar_settings(self):
        self.currentmaxval = self.maxval
        self.currentminval = 0
        self.cbar.ax.set_picker(5) 
        
    def set_slider_settings(self):
        self.slider.setRange(1, 1600)
        self.slider.setValue(800)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QtGui.QSlider.TicksBothSides)    
        
    def show_slices(self,N=100,axis=0):
        """
        Remnant of Aaron's original code. I need to update this for the
        new version.
        show N slices out of a data cube. N square root must be an integer
        """      
        
        self.slices = QtGui.QWidget()
        
        self.slices.fig = plt.figure(figsize=(8.0, 6.0))
        self.slices.canvas = FigureCanvas(self.slices.fig)
        self.slices.canvas.setParent(self.slices) 
        
        dE = 1600/N
        inds = np.r_[0:dE]
        m = self.maxval*(N/16)
        NN = np.floor(np.sqrt(N))
        for i in np.arange(0,N):
            plt.subplot(NN,NN,i+1)
            plt.imshow(np.sum(self.mf1.ycube[i*dE + inds,:],axis=0),
                       interpolation='nearest'  )
            #plt.title('%0.0f to %0.0f nm'%tuple(self.mf1.xdata[np.r_[i*dE + inds][[0,-1]],1,1].tolist()))
            #plt.colorbar()
            plt.yticks([])
            plt.xticks([])
            plt.clim(0,m)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.slices.canvas)
        self.slices.setLayout(vbox)
        


        self.slices.show()
        
    def show_single_graph(self,ax2, xcoordinate, ycoordinate):
        """initializes the graph on screen"""
        #xcoordinates and ycoordinates start from 0
        self.xcoordinate = xcoordinate
        self.ycoordinate = ycoordinate
        self.img2 = ax2.plot(self.mf1.xdata[:,ycoordinate, xcoordinate],
                                  self.mf1.ycube[:,ycoordinate,xcoordinate],'.')
        plt.ylim(ymin=-self.maxval/10, ymax=self.maxval)
        plt.xlabel('$\lambda$ [nm]')
        return ax2        
        
    def show_single_slice(self,ax,ycube, slice1):
        'shows a given slice from the datacube'
        
        #self.maxval = np.amax(ycube)
        #self.maxval = np.amax(np.array(self.mf1.graph1[1600:3200]))
        self.maxval = self.mf1.maxval

        self.slicedata = np.sum(ycube[[slice1],:],axis = 0)
        self.img = ax.imshow(self.slicedata, interpolation='nearest',
                              clim = (0,self.maxval))
        ax.set_title('Current Slice Wavelength:%0.0f '
                           %float(self.mf1.xdata[slice1,0,0]))
        plt.yticks([])
        plt.xticks([])
        return self.img

    def update_single_graph(self, xcoordinate, ycoordinate):
        """updates the graph on screen with the given x and y coordinates"""
        self.ax2.cla()
        self.img2 = self.ax2.plot(self.mf1.xdata[:,ycoordinate, xcoordinate],
                                  self.mf1.ycube[:,ycoordinate, xcoordinate],'.')
        self.ax2.set_ylim(ymin=-self.maxval/10, ymax=self.maxval)
        self.ax2.set_xlabel('$\lambda$ [nm]')

    def update_single_slice(self, val):
        """updates the image on screen with a new cube slice"""
        slice1 = 1600-val
        self.slicedata = np.sum(self.mf1.ycube[[slice1],:],axis = 0)
        self.img.set_array(self.slicedata)
        self.ax.set_title('Current Slice Wavelength:%0.0f '
                          %float(self.mf1.xdata[slice1,0,0]))
        self.canvas.draw()     
      
class InitialSettingsWindow(QtGui.QDialog):
    """Pop-up window confirming image dimensions"""
    def __init__(self, dimension1, dimension2, parent=None):
        super(InitialSettingsWindow, self).__init__(parent)
        self.setWindowTitle('Initial Settings')
        self.dimension1 = dimension1
        self.dimension2 = dimension2
        self.inputs()
        
    def inputs(self):
        
        dimension1label = QtGui.QLabel('Enter Dimension 1:')
        dimension2label = QtGui.QLabel('Enter Dimension 2:')
        
        self.dimension1Edit = QtGui.QLineEdit("%d"%self.dimension1)
        self.dimension2Edit = QtGui.QLineEdit("%d"%self.dimension2)

        self.globalwavelength = QtGui.QCheckBox('Global Wavelength')
        self.globalwavelength.setChecked(False)
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(dimension1label,1,0)
        grid.addWidget(self.dimension1Edit,1,1)
        
        grid.addWidget(dimension2label,2,0)
        grid.addWidget(self.dimension2Edit,2,1)
        
        grid.addWidget(self.globalwavelength,3,0)
        
        self.okButton = QtGui.QPushButton("OK")
        self.cancelButton = QtGui.QPushButton("Cancel")

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)


        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        
        grid.addLayout(vbox,3,1)
        
        self.setLayout(grid)
        self.setGeometry(400,400,50,50)
        self.connect_events()
        self.show()

        
    def connect_events(self):
          self.connect(self.okButton, QtCore.SIGNAL('clicked()'),self.accept)
          self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.reject)


class ColorWindow(QtGui.QDialog):
    
    def __init__(self):
        super(ColorWindow, self).__init__()
        self.setWindowTitle('Set Color Limits')
        self.inputs()

    def inputs(self):
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
        
        grid.addWidget(mincolorlabel,2,0)
        grid.addWidget(self.mincolor,2,1)
        grid.addWidget(self.resetbutton,3,0)

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
        
        grid.addLayout(vbox,3,1)
        
        self.setLayout(grid)
        self.setGeometry(300,300,50,50)
        self.connect_events()
        self.show()

        
    def connect_events(self):
        self.connect(self.okButton, QtCore.SIGNAL('clicked()'),self.accept)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.reject)
        self.connect(self.resetbutton, QtCore.SIGNAL('clicked()'), self.reset)
    
    def reset(self):
        self.resetvalue = True
        self.accept()


class ControlWindow(QtGui.QDialog):
        
    def __init__(self, parent=None):
        super(ControlWindow, self).__init__(parent)
        self.setWindowTitle('Control Panel')
        self.setModal(False)
        self.inputs()
        
    def inputs(self):
        maxcolorlabel = QtGui.QLabel('Enter Max Color Value:')
        mincolorlabel = QtGui.QLabel('Enter Min Color Value:')
        imageslicelabel = QtGui.QLabel('Enter Image Slice Wavelength:')
        graphslicelabelx = QtGui.QLabel('Enter Graph Slice X Coordinate:')
        graphslicelabely = QtGui.QLabel('Enter Graph Slice Y Coordinate:')
        
        self.maxcolor = QtGui.QLineEdit()
        self.mincolor = QtGui.QLineEdit()
        self.imageslice = QtGui.QLineEdit()
        self.graphslicex = QtGui.QLineEdit()
        self.graphslicey = QtGui.QLineEdit()
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(maxcolorlabel,1,0)
        grid.addWidget(self.maxcolor,1,1)
        
        grid.addWidget(mincolorlabel,2,0)
        grid.addWidget(self.mincolor,2,1)

        grid.addWidget(imageslicelabel,3,0)
        grid.addWidget(self.imageslice,3,1)
        
        grid.addWidget(graphslicelabelx,4,0)
        grid.addWidget(self.graphslicex,4,1)
        
        grid.addWidget(graphslicelabely,5,0)
        grid.addWidget(self.graphslicey,5,1)
        
        self.update = QtGui.QPushButton("Update")



        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.update)


        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        
        grid.addLayout(vbox,6,1)
        
        self.c = Communicate()
        
        self.setLayout(grid)
        self.setGeometry(300,300,50,50)
        self.connect_events()
        self.show()
    
    def connect_events(self):
                self.connect(self.update, QtCore.SIGNAL('clicked()'), self.update_values)
    
    def update_values(self):
        """Updates values in main window and clears textboxes"""
        objects = {self.c.maxcolor_sig:self.maxcolor,
             self.c.mincolor_sig:self.mincolor,
             self.c.imageslice_sig:self.imageslice,
             self.c.graphslicex_sig:self.graphslicex,
             self.c.graphslicey_sig:self.graphslicey}

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
    graphslicex_sig = QtCore.Signal() 
    graphslicey_sig = QtCore.Signal()    
    
    
def main():
    app = QtGui.QApplication(os.sys.argv)
    form = AppForm()
    form.show()
    app.exec_()
    
if __name__ == "__main__":
    main()

