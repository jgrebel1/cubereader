import sys
from PySide import QtGui

def file_dialog():
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    dialog = QtGui.QFileDialog()
    dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
    dialog.setNameFilter('HDF5 (*.hdf5)')
    if dialog.exec_():
        filenames = dialog.selectedFiles()
    for name in filenames:
        if name:
            filename = name
        else:
            print 'No file selected'
    return filename