"""
@authors: Joel Grebel and Aaron Hammack

used Eli Bendersky's (eliben@gmail.com) embeding matplotlib into pyqt 
Gui Demo for some of the structure.
"""

import os
import sys
import matplotlib
from PySide import QtCore
from PySide import QtGui
matplotlib.rcParams['backend.qt4']='PySide'

#project specific items



import analysis
import tab
import control_relay
import menu_tools
import convert_file


class AppForm(QtGui.QMainWindow):
    """Gui Application to display Data Cube"""
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle('Mf1 File Reader')
        
        self.create_menu()
        self.create_main_window()
        #self.create_status_bar()
        
    def control_panel_update(self):
        self.control.update_current()
        
    def create_main_window(self):
        self.main_window = QtGui.QWidget()
        self.tab = QtGui.QTabWidget()
        self.tab.setTabsClosable(True)
        self.tab.tabCloseRequested.connect(self.tab.removeTab)
        layout = QtGui.QHBoxLayout()
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
                                            slot=convert_file.convert_mf1,
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
        """
        opens control panel. The control panel always affects the currently
        selected tab.
        """
        self.control = control_relay.ControlRelay(self.tab)
        self.tab.currentChanged.connect(self.control_panel_update)
    

    def open_file(self):
        """opens a file in a new tab"""
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        #dialog.setNameFilter('HDF5 (*.hdf5)')
        if dialog.exec_():
            filenames = dialog.selectedFiles()
        for filename in filenames:
            if filename:
                basename = analysis.get_file_basename(filename)            
                with open(filename,'rb') as f:
                    QtGui.QMessageBox.information(self,basename, f.read(2048).strip())  
    
                newtab = tab.Tab(filename)        
                newtab.setWindowTitle('%s' %basename)
                self.tab.addTab(newtab, '%s' %basename)
        

def main():
    app = QtGui.QApplication(os.sys.argv)
    form = AppForm()
    form.show()
    app.exec_()
    
if __name__ == "__main__":
    main()
