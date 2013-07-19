# -*- coding: utf-8 -*-
"""
Created on Mon Jul 08 17:44:52 2013

@author: JG
"""
import os
import h5py
import numpy as np

def export_graph(hdf5_file, output_file, xcoordinate, ycoordinate):
    graph = prepare_graph(hdf5_file, xcoordinate, ycoordinate)
    save_graph(output_file, graph)
    

def save_graph(output_file, graph):
    np.savetxt(output_file, graph)
        

def prepare_graph(hdf5_file, xcoordinate, ycoordinate):
    data = h5py.File(hdf5_file,'r')
    ycube = data['ycube']
    xdata = data['xdata']
    graph = np.vstack((xdata, ycube[xcoordinate, ycoordinate, :]))
    graph = graph.transpose()
    graph = np.flipud(graph)
    return graph