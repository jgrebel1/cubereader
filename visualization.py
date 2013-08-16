
import os
import mayavi
os.environ['ETS_TOOLKIT'] = 'qt4'
from pyface.qt import QtGui, QtCore
from traits.api import HasTraits, Instance, on_trait_change, \
    Int, Dict, Bool
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
        SceneEditor
from tvtk.api import tvtk
import numpy as np

class Visualization(HasTraits):
    scene = Instance(MlabSceneModel, ())
    try:
        engine = mayavi.engine
    except:
        from mayavi.api import Engine
        engine = Engine()
        engine.start()
        
    
    def __init__(self,xdata, ycube):#, vmin_color, vmax_color):
        self.xdata = xdata
        self.ycube = ycube
        #self.x_scale = np.ones(np.shape(self.ycube[:,0,0]))
        #self.y_scale = np.ones(np.shape(self.ycube[0,:,0]))
        
        self.initialize = True        
        self.update_plot()
        
        self.plane1 = self.engine.scenes[0].children[0].children[0].children[0]
        self.plane2 = self.engine.scenes[0].children[0].children[0].children[1]
        self.iso_surface = self.engine.scenes[0].children[0].children[0].children[2]
        self.volume = self.engine.scenes[0].children[0].children[0].children[3]
        
    def align_z_coordinates(self, xdata):
        """
        aligns middle of xdata to origin 
        """
        middle = len(xdata)/2
        middle_value = xdata[middle]
        new_xdata = (xdata)-(middle_value)
        return new_xdata

    def show_iso(self, check_state):
        self.iso_surface.actor.actor.visibility = check_state

    def show_plane1(self, check_state):
        #self.plane1.ipw.enabled = check_state
        self.plane1.actor.actor.visibility = check_state
        self.plane1.implicit_plane.widget.enabled = check_state
    
    def show_plane2(self, check_state):
        #self.plane2.ipw.enabled = check_state
        self.plane2.actor.actor.visibility = check_state
        self.plane2.implicit_plane.widget.enabled = check_state
        
    #def show_volume(self, check_state):
        #self.volume.volume_mapper.cropping = not check_state
        
    @on_trait_change('scene.activated')
    def update_plot(self):
        data = self.ycube
        
        #r = tvtk.RectilinearGrid()
        #r.point_data.scalars = data.ravel()
        #r.point_data.scalars.name = 'scalars'
        #r.dimensions = data.shape
        #r.x_coordinates = self.x_scale
        #r.y_coordinates = self.y_scale
        #r.z_coordinates = self.align_z_coordinates(self.xdata)
        scalar_field_data = self.scene.mlab.pipeline.scalar_field(data)
        self.scene.mlab.pipeline.scalar_cut_plane(scalar_field_data,
                                                  plane_orientation='y_axes')
        
        self.scene.mlab.pipeline.scalar_cut_plane(scalar_field_data,
                                                  plane_orientation='z_axes') 
        self.scene.mlab.pipeline.iso_surface(scalar_field_data)

        self.scene.mlab.outline()
        
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                resizable=True # We need this to resize with the parent widget
                )

class MayaviQWidget(QtGui.QWidget):
    def __init__(self,xdata, ycube,parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('3D Data Visualization')
        layout = QtGui.QVBoxLayout(self)

        self.visualization = Visualization(xdata, ycube)#,
                                           #visualization_min_color,
                                           #visualization_max_color)
        button_hide = QtGui.QPushButton('Close Window')
        button_hide.clicked.connect(self.hide_window)
        
        self.group_checkbox = QtGui.QGroupBox()  
        self.group_checkbox.setTitle("Display Objects")
          
        #self.checkbox_volume = QtGui.QCheckBox("Show Volume")
        #self.checkbox_volume.setChecked(True)
        #self.checkbox_volume.stateChanged.connect(self.show_volume)        
        
        self.checkbox_plane1 = QtGui.QCheckBox("Show Plane 1")
        self.checkbox_plane1.setChecked(True)
        self.checkbox_plane1.stateChanged.connect(self.show_plane1)
        
        self.checkbox_plane2 = QtGui.QCheckBox("Show Plane 2")
        self.checkbox_plane2.setChecked(True)
        self.checkbox_plane2.stateChanged.connect(self.show_plane2)
        
        self.checkbox_iso = QtGui.QCheckBox("Show Isometric Surface")
        self.checkbox_iso.setChecked(True)
        self.checkbox_iso.stateChanged.connect(self.show_iso)
        
        hbox = QtGui.QHBoxLayout()
        #hbox.addWidget(self.checkbox_volume)
        hbox.addWidget(self.checkbox_plane1)
        hbox.addWidget(self.checkbox_plane2)        
        hbox.addWidget(self.checkbox_iso)    
        self.group_checkbox.setLayout(hbox)

        self.ui = self.visualization.edit_traits(parent=self,
                                                 kind='subpanel').control
        layout.addWidget(button_hide)
        layout.addWidget(self.ui)
        layout.addWidget(self.group_checkbox)
        self.ui.setParent(self)
        
    def hide_window(self):
        self.visualization.scene.mlab.close()
        self.hide()
            
    def show_iso(self):
        value = self.checkbox_iso.isChecked()
        self.visualization.show_iso(value)            
            
    def show_plane1(self):
        value = self.checkbox_plane1.isChecked()
        self.visualization.show_plane1(value)            
            
    def show_plane2(self):
        value = self.checkbox_plane2.isChecked()
        self.visualization.show_plane2(value)            
    
    def show_volume(self):
        value = self.checkbox_volume.isChecked()
        self.visualization.show_volume(value)

"""
if __name__ == "__main__":
    app = QtGui.QApplication.instance()
    container = QtGui.QWidget()
    container.setWindowTitle("Embedding Mayavi in a PyQt4 Application")
    layout = QtGui.QGridLayout(container)

    mayavi_widget = MayaviQWidget(container)

    layout.addWidget(mayavi_widget, 1, 1)
    container.show()
    window = QtGui.QMainWindow()
    window.setCentralWidget(container)
    window.show()

    # Start the main event loop.
    app.exec_()
"""