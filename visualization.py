
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
    show_volume = Bool()
    show_image_plane_widget_1 = Bool()
    show_image_plane_widget_2 = Bool()
    show_ismetric_surface = Bool()
    try:
        engine = mayavi.engine
    except:
        from mayavi.api import Engine
        engine = Engine()
        engine.start()
    
    def __init__(self,
                 ycube,
                 visualization_min_color,
                 visualization_max_color):
        self.ycube = ycube
        self.visualization_min_color = visualization_min_color
        self.visualization_max_color = visualization_max_color
        self.update_plot()

    @on_trait_change('scene.activated, show_volume')
    def update_plot(self):
        #if self.show_volume.get_value:
        self.scene.mlab.pipeline.volume(self.scene.mlab.pipeline.scalar_field(self.ycube[:,:,:]), 
                                        vmin=self.visualization_min_color,
                                        vmax=self.visualization_max_color)
        #mlab.pipeline.image_plane_widget(mlab.pipeline.scalar_field(s),
                                         #plane_orientation='x_axes',
                                         #slice_index=10, vmin=100, vmax=800)
        data = self.ycube
        self.scene.mlab.pipeline.image_plane_widget(self.scene.mlab.pipeline.scalar_field(data),
                                                    plane_orientation='y_axes',
                                                    slice_index=10, 
                                                    vmin=self.visualization_min_color,
                                                    vmax=self.visualization_max_color)
        self.scene.mlab.pipeline.image_plane_widget(self.scene.mlab.pipeline.scalar_field(data),
                                         plane_orientation='z_axes',
                                         slice_index=10, vmin=self.visualization_min_color, vmax=self.visualization_max_color)   
                        
        self.scene.mlab.outline()
        #self.scene.mlab.array_source.spacing = np.array([ 4.,  1.,  1.])
        #self.scene.mlab.test_points3d()
        #array_source = self.engine.scenes[0].children[0]
        #image_plane_widget = array_source.children[0].children[0]
        #array_source.spacing = np.array([ 4.,  1.,  1.])
        #image_plane_widget.ipw.point2 = np.array([100, 11, .5])
        volume = self.engine.scenes[0].children[0].children[0].children[0]
        volume.volume_mapper.cropping = self.show_volume

    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                Item('show_volume'),
                resizable=True # We need this to resize with the parent widget
                )

class MayaviQWidget(QtGui.QWidget):
    def __init__(self,ycube, visualization_min_color, visualization_max_color, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('3D Data Visualization')
        layout = QtGui.QVBoxLayout(self)

        self.visualization = Visualization(ycube,
                                           visualization_min_color,
                                           visualization_max_color)
        self.hide_button = QtGui.QPushButton('Close Window')
        self.connect(self.hide_button, QtCore.SIGNAL('clicked()'), 
                    self.hide_window)

        self.ui = self.visualization.edit_traits(parent=self,
                                                 kind='subpanel').control
        layout.addWidget(self.hide_button)
        layout.addWidget(self.ui)
        self.ui.setParent(self)
    def hide_window(self):
        self.visualization.scene.mlab.close()
        self.hide()

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