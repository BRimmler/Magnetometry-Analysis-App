# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 11:15:55 2021

@author: rimmler
"""

import os
import pandas as pd

# Generic file class
class File:
    def __init__(self, *fileLoc):
        '''
        Parameters
        ----------
        *fileLoc : str or tuple of str
            Full file path or directory and file name (with file extension) given
            separately.

        Returns
        -------
        File object.

        '''
        if len(fileLoc) == 1: # Single string file directory and name
            fileLoc = fileLoc[0].replace('\\', '/')
            self.fileDirName = fileLoc
            self.fileDir = '/'.join(fileLoc.split('/')[:-1])
            self.fileName = fileLoc.split('/')[-1]
        elif len(fileLoc) == 2: # File directory and file name
            self.fileDir = fileLoc[0]
            self.fileName = fileLoc[1]
            self.fileDirName = self.fileDir + '/' + self.fileName
        else:
            raise SyntaxError('fileLoc must be of length 1 or 2.')

        self.fileExt = '.' + self.fileName.split('.')[-1]
        self.fileNameWOExt = '.'.join(self.fileName.split('.')[:-1])
        
    def makeDirIfNotExist(self):
        ''' Creates the directory of the file if it does not already exist '''
        if os.path.isdir(self.fileDir) == False:
            os.makedirs(self.fileDir)
            print(self.fileDir+' created.')

    def create_subDir(self, name):
        ''' Create a subdirectory with given name '''
        subDir = self.firDir + '/' + name
        if os.path.isdir(subDir) is False:
            os.makedirs(subDir)
            # print(subDir+' created.')
        return subDir
    
    def create_subFile(self, name):
        ''' Create file with same file name in sub directory '''
        subDir = self.create_subDir(name)
        subFile = File(subDir, self.fileName)
        return subFile

    def read(self, sep=',', info_stop_key=None, data_start_key=None, dropna=True, **kwargs):
        '''
        A simple file reader based on pandas. Assumes the file content consists 
        of two parts: 
            First, general info written in separate lines. 
            Secondly, the main data in a format readable by pandas (a simple data table). 
        The breaking point of the two can be defined by info_stop_kley or data_start_key.
        
        Parameters
        ----------
        sep : str, optional
            Delimiter of data. The default is ','.
        info_stop_key: str, optional
            String at the start of the last line of the info section.
            The default is None
        data_start_key : str, optional
            String at the beginning of the first line of the data section. 
            The default is None.
        dropna: bool, optional
            Drop empty rows. Default is True
        **kwargs : kwargs
            Passed on to pandas.read_csv().

        Returns
        -------
        Adds info and data to self.

        '''
        
        if info_stop_key is not None and data_start_key is not None :
            raise ValueError('Either info_stop_key aor data_start_key mus be None')
        
        with open(self.fileDirName, 'r') as f:
            self.raw = f.readlines()
            
        for i, line in enumerate(self.raw):
            if info_stop_key is not None:
                if line.startswith(info_stop_key):
                    data_start_index = i + 1
            if data_start_key is not None:
                if line.startswith(data_start_key):
                    data_start_index = i
            
        self.info = self.raw[:data_start_index]
        delattr(self, 'raw')
        self.data = pd.read_csv(self.fileDirName, sep=sep, skiprows=data_start_index)
        if dropna is True:
            self.data.dropna(how='all', inplace=True)
            self.data.reset_index(drop=True, inplace=True)

    def split_by_const_col(self, column, noise):
        if not hasattr(self, 'info'):
            raise ValueError('File must be read first')
            
        const_col = self.data[column]
        j = -1
        unique_vals = []
        for i, row in const_col.iteritems():
            j += 1
            if j == 0:
                unique_vals.append(row)
            if j > 0:
                if abs(row - const_col.iloc[i-1]) > abs(noise):
                    unique_vals.append(row)
        
        unique_vals = sorted(unique_vals)
             
        split_data = []
        for val in unique_vals:
            splt = self.data[abs(self.data[column]-val)<abs(noise)]
            split_data.append(splt)
            
        return split_data
            
        
            
        
        
        
        














