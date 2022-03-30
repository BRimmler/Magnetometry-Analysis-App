# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 15:24:14 2022

@author: rimmler
"""

from scipy.interpolate import interp1d

def get_enum_indices(X, ignore_edge_data, n_ignore):
    if ignore_edge_data is True:
        start_enum_index = n_ignore
        stop_enum_index = len(X) - n_ignore
    else:
        start_enum_index = 1
        stop_enum_index = len(X)
    return start_enum_index, stop_enum_index

def hyst_interp(data, xlabel, ylabel):
    data = data.sort_values(xlabel) # Sorting for interpolation
    x = data[xlabel]
    y = data[ylabel]
    f_interp = interp1d(x, y)
    y_interp = f_interp(x)
    return f_interp, y_interp


def scale_tuple(tup, factor, axis):
    if axis == 0:
        out = (tup[0]*factor, tup[1])
    else:
        out = (tup[0], tup[1]*factor)
    return out