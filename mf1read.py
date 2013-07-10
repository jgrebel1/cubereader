"""
@authors: Joel Grebel and Aaron Hammack

used Eli Bendersky's (eliben@gmail.com) embeding matplotlib into pyqt 
Gui Demo for much of the structure.
"""

import os
import matplotlib
from PySide import QtCore
from PySide import QtGui
matplotlib.rcParams['backend.qt4']='PySide'

#project specific items


import default
import cube_loader
import analysis
import tab
import init_settings
import control
import menu_tools


class AppForm(QtGui.QMainWindow):
    """Gui Application to display Data Cube"""
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle('Mf1 File Reader')
        
        self.create_menu()
        self.create_main_window()
        #self.create_status_bar()

    def convert_file(self):
        self.filename, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        
        print('Reading file: %s'%self.filename)
        print 'Pick a folder to save the hdf5 file'
        self.hdf5_directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                                       'Choose a file Directory')
        self.default_values = default.DefaultValues(self.filename)
        filename, extension = os.path.splitext(self.filename)
        basename = analysis.get_file_basename(self.filename)
        hdf5_file = os.path.join(self.hdf5_directory, basename)
        
        self.open_initial_settings()
        print('Saving file: %s'%basename)        
        cube_loader.Mf1File(self.filename,hdf5_file,
                            self.dimension1, self.dimension2,
                            self.globalwavelength)
        print 'Conversion Complete'
        
    def create_main_window(self):
        self.main_window = QtGui.QWidget()
        #self.button = QtGui.QPushButton('Add Tab')
        #self.button.clicked.connect(self.open_file)
        self.tab = QtGui.QTabWidget()
        self.tab.setTabsClosable(True)
        self.tab.tabCloseRequested.connect(self.tab.removeTab)
        layout = QtGui.QHBoxLayout()
        #layout.addWidget(self.button)
        layout.addWidget(self.tab)

        self.main_window.setLayout(layout)
        self.setCentralWidget(self.main_window)
        self.resize(971,600)



    def create_menu(self):
        """makes the menu toolbar on the top of the main window"""
        self.file_menu = self.menuBar().addMenu("&File")
        open_action = menu_tools.create_action(self, "&Open New HDF5 File", 
                                         slot=self.open_file,
                                         shortcut="Ctrl+N",
                                         tip="Open a New HDF5 File"
                                         )
        convert_action = menu_tools.create_action(self, "&Convert MF1",
                                            slot=self.convert_file,
                                            shortcut="Ctrl+A",
                                            tip="Convert an Mf1 file to HDF5")
        quit_action = menu_tools.create_action(self, "&Quit", slot=self.close, 
                                         shortcut="Ctrl+Q", 
                                         tip="Close the application")
        control_action = menu_tools.create_action(self, "&Open Control Panel",
                                            slot = self.open_control,
                                            shortcut="Ctrl+P",
                                            tip="Open the Control Panel")
        menu_tools.add_actions(self, self.file_menu, 
            (open_action,convert_action, control_action,None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = menu_tools.create_action(self, "&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About Mf1Reader')
        menu_tools.add_actions(self, self.help_menu, (about_action,))
        
    def on_about(self):
        """Displays pop-up about box"""
        msg = """A File Reader for Mf1 Files. Joel Grebel and Aaron Hammack
        """
        QtGui.QMessageBox.about(self, "About the Mf1Reader", msg.strip())    
        
        
    def open_control(self):
        self.control = control.ControlWindow(self.tab.currentWidget())

        

    def open_file(self):
        """opens a file in a new tab"""

        filename, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        basename = analysis.get_file_basename(filename)
        newtab = tab.Tab(filename)        
        newtab.setWindowTitle('%s' %basename)
        self.tab.addTab(newtab, '%s' %basename)
        
    def open_initial_settings(self):
        """
        calls the Initial Settings window and changes the default values
        if necessary.
        """
        self.dimension1, self.dimension2 = self.default_values.default_dimensions() 
        self.global_bool = self.default_values.default_global()
        self.initialsettings = init_settings.InitialSettingsWindow(self.dimension1,
                                                                   self.dimension2,
                                                                   self.global_bool) 
        self.initialsettings.exec_()
        
        if self.initialsettings.result() and self.initialsettings.dimension1Edit.text()!='':
            print 'Dimension 1 is now ', self.initialsettings.dimension1Edit.text()
            self.dimension1 = int(self.initialsettings.dimension1Edit.text())
        if self.initialsettings.result() and self.initialsettings.dimension2Edit.text()!='':   
            print 'Dimension 2 is now ', self.initialsettings.dimension2Edit.text()
            self.dimension2 = int(self.initialsettings.dimension2Edit.text())
        if self.initialsettings.result():
            self.globalwavelength = self.initialsettings.globalwavelength.isChecked()
            

def main():
    app = QtGui.QApplication(os.sys.argv)
    form = AppForm()
    form.show()
    app.exec_()
    
if __name__ == "__main__":
    main()
