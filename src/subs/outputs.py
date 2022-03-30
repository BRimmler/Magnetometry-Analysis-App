# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 08:33:01 2022

@author: rimmler
"""
from .files import File
import matplotlib.pyplot as plt
import pandas as pd
from .plots import GenPlot

class Output:
    def __init__(self, obj, opBaseDir, opFileName):
        self.obj = obj
        self.opBaseDir = opBaseDir
        self.opFileName = opFileName
        
    def make_subFile(self, name):
        opSubDir = self.opBaseDir + '/' + name
        self.opSubFile = File(opSubDir, self.opFileName)
        self.opSubFile.makeDirIfNotExist()
        
        
class PlotOutput(Output):
    def __init__(self, fig, opBaseDir, opFileName, subDir='plots', saveDataFrame=None, datFileExt='.csv'):
        if not isinstance(fig, plt.Figure):
            raise TypeError(f'{fig} is not a plt.Figure instance')
        
        super().__init__(fig, opBaseDir, opFileName)
        self.subDir = subDir
        self.saveDataFrame = saveDataFrame
        self.datFileExt = datFileExt
        
    def save(self):
        self.make_subFile(self.subDir)
        
        self.obj.savefig(self.opSubFile.fileDirName, bbox_inches='tight')
        if self.saveDataFrame is not None:
            figDataOutputName = self.opSubFile.fileNameWOExt+'_dat'+self.datFileExt
            self.figDataOutput = DataFrameOutput(self.saveDataFrame, self.opSubFile.fileDir, 
                                                 figDataOutputName, subDir='/plot_data', )
            self.figDataOutput.save()


class GenPlotOutput:
    def __init__(self, fig, opDir, opName, SI=(), saveData=False, fig_ext='.png', dat_ext='.csv'):
        if not isinstance(fig, GenPlot):
            raise TypeError(f'{fig} is not a GenPlot instance')
            
        self.fig = fig
        self.opDir = opDir
        self.opName = opName
        self.SI = SI
        self.saveData = saveData
        self.fig_ext = fig_ext
        self.dat_ext = dat_ext
        
    def save(self):
        self.fig.report(self.opDir+'/plots', self.opName, 
                        SI=self.SI, saveData=self.saveData, fig_ext=self.fig_ext, dat_ext=self.dat_ext)


class DataFrameOutput(Output):
    def __init__(self, df, opBaseDir, opFileName, subDir='data', index=False, **kwargs):
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f'{df} is not a pd.DataFrame instance')
        
        super().__init__(df, opBaseDir, opFileName)
        self.subDir = subDir
        self.index = index
        self.kwargs = kwargs
        
    def save(self):
        self.make_subFile(self.subDir)
        self.obj.to_csv(self.opSubFile.fileDirName, index=self.index, **self.kwargs)


class ParamsOutput(Output):
    def __init__(self, params_dict, opBaseDir, opFileName, subDir='parameters', header=False, **kwargs):
        if not isinstance(params_dict, dict):
            raise TypeError(f'{params_dict} is not a dict instance')
            
        super().__init__(params_dict, opBaseDir, opFileName)
        self.subDir = subDir
        self.header = header
        self.kwargs = kwargs
        
    def save(self):
        params_series = pd.Series(self.obj)
        seriesOP = SeriesOutput(params_series, self.opBaseDir, opFileName=self.opFileName,
                                subDir=self.subDir, **self.kwargs)
        seriesOP.save()

class SeriesOutput(Output):
    def __init__(self, df, opBaseDir, opFileName, subDir='data', header=False, **kwargs):
        if not isinstance(df, pd.Series):
            if isinstance(df, dict):
                df = pd.Series(df)
            else:
                raise TypeError(f'{df} is not a pd.Series instance')
        
        super().__init__(df, opBaseDir, opFileName)
        self.subDir = subDir
        self.header = header
        self.kwargs = kwargs
        
    def save(self):
        self.make_subFile(self.subDir)
        self.obj.to_csv(self.opSubFile.fileDirName, header=self.header, **self.kwargs)
















