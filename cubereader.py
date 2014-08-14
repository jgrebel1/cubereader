"""
@authors: Joel Grebel and Aaron Hammack

used Eli Bendersky's (eliben@gmail.com) embeding matplotlib into pyqt 
Gui Demo for some of the structure.
"""


#from pyface.qt import QtGui, QtCore

import matplotlib
from PySide import QtCore, QtGui, QtUiTools
matplotlib.rcParams['backend.qt4']='PySide'
#project specific items



import analysis
import tab
import control_relay
import menu_tools
import convert_file
import rebin_hdf5
import open_cube_fit


class AppForm(object):
    """Gui Application to display Data Cube"""
    def __init__(self, parent=None):
        self.create_main_window()
        self.connect_buttons()
        
        
#         self.create_main_window()
        
    def create_main_window(self):
        """populate screen"""
        # Load Qt UI from .ui file
        ui_loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile("cubereader.ui")
        ui_file.open(QtCore.QFile.ReadOnly); 
        self.ui = ui_loader.load(ui_file)
        ui_file.close()

        
        self.ui.tabWidget.setTabsClosable(True)
        self.ui.tabWidget.tabCloseRequested.connect(self.close_tab)

        
    def close_tab(self):
        """closes hdf5 files before closing tab"""
        try:
            if self.ui.tabWidget.currentWidget().data.hdf5:
                self.ui.tabWidget.currentWidget().data.hdf5.close()
        except:
            pass
        try:
            if self.ui.tabWidget.currentWidget().cube_data.hdf5:
                self.ui.tabWidget.currentWidget().cube_data.hdf5.close()
            if self.ui.tabWidget.currentWidget().fit_data.hdf5:
                self.ui.tabWidget.currentWidget().cube_data.hdf5.close()
        except:
            pass
        self.ui.tabWidget.removeTab(self.ui.tabWidget.currentIndex())             
        
    def control_panel_update(self):
        self.control.update_current()
        
    def connect_buttons(self):
        self.ui.button_open_file.clicked.connect(self.open_file)
        self.ui.button_open_fit.clicked.connect(self.open_fit)
        self.ui.button_convert_mf1.clicked.connect(convert_file.ConvertToCubeReader)
        self.ui.button_rebin_file.clicked.connect(rebin_hdf5.RebinHDF5)


    def create_menu(self):
        """makes the menu toolbar on the top of the main window"""
        self.file_menu = self.menuBar().addMenu("&File")
        open_action = menu_tools.create_action(self, "&Open New HDF5 File", 
                                         slot=self.open_file,
                                         shortcut="Ctrl+N",
                                         tip="Open a New HDF5 File"
                                         )
        open_fit_action = menu_tools.create_action(self, "&Open Cube Fit",
                                                   slot=self.open_fit)
        convert_action = menu_tools.create_action(self, "&Convert File",
                                            slot=convert_file.ConvertToCubeReader,
                                            shortcut="Ctrl+A",
                                            tip="Convert an Mf1 file to HDF5")
        quit_action = menu_tools.create_action(self, "&Quit", slot=self.close, 
                                         shortcut="Ctrl+Q", 
                                         tip="Close the application")
        #control_action = menu_tools.create_action(self, "&Open Control Panel",
        #                                    slot = self.open_control,
        #                                    shortcut="Ctrl+P",
        #                                    tip="Open the Control Panel")
        rebin_action = menu_tools.create_action(self, "&Rebin HDF5",
                                                slot=rebin_hdf5.RebinHDF5)
        menu_tools.add_actions(self, self.file_menu, 
                               (open_action,open_fit_action,
                                convert_action,
                                rebin_action,None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = menu_tools.create_action(self, "&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About Mf1Reader')
        menu_tools.add_actions(self, self.help_menu, (about_action,))
        
    def on_about(self):
        """Displays pop-up about box"""
        msg = """A File Reader for Mf1 Files. Joel Grebel and Aaron Hammack
        """
        QtGui.QMessageBox.about(self, "About the Cube Reader", msg.strip())    
        
        
    def open_control(self):
        """
        opens control panel. The control panel always affects the currently
        selected tab.
        """
        self.control = control_relay.ControlRelay(self.ui.tabWidget)
        self.ui.tabWidget.currentChanged.connect(self.control_panel_update)
    

    def open_file(self):
        """opens a file in a new tab"""
        dialog = QtGui.QFileDialog(self.ui)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        dialog.setNameFilter('HDF5 (*.hdf5)')
        if dialog.exec_():
            filenames = dialog.selectedFiles()
        for filename in filenames:
            if filename:
                basename = analysis.get_file_basename(filename)   
                newtab = tab.Tab(filename)         
                newtab.setWindowTitle('%s' %basename)
                self.ui.tabWidget.addTab(newtab, '%s' %basename)
            else:
                print 'No file selected'
                
    def open_fit(self):
        """opens a cube fit in a new tab"""
        dialog = QtGui.QFileDialog(self.ui)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        dialog.setNameFilter('HDF5 (*.hdf5)')
        if dialog.exec_():
            filenames = dialog.selectedFiles()
        for filename in filenames:
            if filename:
                basename = analysis.get_file_basename(filename)   
                newtab = open_cube_fit.CubeFit(filename)         
                newtab.setWindowTitle('%s' %basename)
                self.ui.tabWidget.addTab(newtab, '%s' %basename)
            else:
                print 'No file selected'
                
    def show(self):
        self.ui.show()
                                                                          

def main():
    app = QtGui.QApplication.instance()
    form = AppForm()
    form.show()
    app.exec_()
    
if __name__ == "__main__":
    main()
