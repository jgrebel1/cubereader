import sys
from PySide import QtGui

#project specific items
import data_holder
import analysis
import data_view

def file_dialog(title=None):
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    dialog = QtGui.QFileDialog()
    dialog.setWindowTitle(title)
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

def load_data(filename):
    data = data_holder.Data(filename)
    maxval = analysis.find_maxval(data.ycube[...])
    dimensions = analysis.get_dimensions(data.ycube)
    dataview = data_view.DataView(maxval, dimensions)
    return data, dataview

def load_fit(filename):
    fit_data = data_holder.FitData(filename)           
    fit_data_view = data_view.FitDataView()  
    return fit_data, fit_data_view