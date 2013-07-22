
import os
os.environ['ETS_TOOLKIT'] = 'qt4'
from pyface.qt import QtGui, QtCore
from traits.api import HasTraits, Instance, on_trait_change, \
    Int, Dict
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, \
        SceneEditor

class Visualization(HasTraits):
    scene = Instance(MlabSceneModel, ())
    
    def __init__(self, ycube, visualization_min_color, visualization_max_color):
        self.ycube = ycube
        self.visualization_min_color = visualization_min_color
        self.visualization_max_color = visualization_max_color
        self.update_plot()

    @on_trait_change('scene.activated')
    def update_plot(self):
        self.scene.mlab.pipeline.volume(self.scene.mlab.pipeline.scalar_field(self.ycube[:,:,:]), 
                                        vmin=self.visualization_min_color,
                                        vmax=self.visualization_max_color)
        #mlab.pipeline.image_plane_widget(mlab.pipeline.scalar_field(s),
                                         #plane_orientation='x_axes',
                                         #slice_index=10, vmin=100, vmax=800)
        
        self.scene.mlab.pipeline.image_plane_widget(self.scene.mlab.pipeline.scalar_field(self.ycube[:,:,:]),
                                                    plane_orientation='y_axes',
                                                    slice_index=10, 
                                                    vmin=self.visualization_min_color,
                                                    vmax=self.visualization_max_color)
        self.scene.mlab.pipeline.image_plane_widget(self.scene.mlab.pipeline.scalar_field(self.ycube[:,:,:]),
                                         plane_orientation='z_axes',
                                         slice_index=10, vmin=self.visualization_min_color, vmax=self.visualization_max_color)   
                                  
        self.scene.mlab.outline()
        #self.scene.mlab.test_points3d()

    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
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