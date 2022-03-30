# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 14:59:19 2022

@author: rimmler
"""

import pandas as pd

# _____________________________________________________________________________
# Pandas
def add_constant_column(df, name, val):
    # adding column with constant value
    df[name] = pd.Series([val for x in range(len(df.index))])
    return df
    
def shift_column_to_pos(df, col_name, loc):
    col = df[col_name]
    df = df.drop(columns=[col_name])
    df.insert(loc=loc, column=col_name, value=col)
    return df
    
def shift_column_to_start(df, col_name):
    df = shift_column_to_pos(df, col_name, 0)
    return df

def pd_find_closest(df, val):
    '''
    Parameters
    ----------
    df : pd.Series
        A pandas Series.
    val : float
        A target value.

    Returns
    -------
    index : int
        The index of the element in df closest to val.
    val : TYPE
        The value of element in df closest to val.
    '''
    sort = df.iloc[(df-val).abs().argsort()[:1]]
    index = sort.index.tolist()[0]
    val = sort.tolist()[0]
    return index, val
