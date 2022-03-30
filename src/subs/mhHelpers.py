# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 10:55:58 2021

@author: rimmler
"""

import numpy as np
import pandas as pd
import os
from .files  import File


class mhFile(File):
    def __init__(self, fileDir, systemSettings, MeasModeScan):
        super().__init__(fileDir) # Get attributes of generic File class
        
        # Settings
        self.systemSettings = systemSettings
        self.MeasModeScan = MeasModeScan
        
    def get_data(self):
        systemSettings = self.systemSettings
        MeasModeScan = self.MeasModeScan
        
        # Get full data
        self.read(sep=systemSettings.IPFileDelimiter, 
                  info_stop_key=systemSettings.infoStopKey)
        
        # Get crucial data
        # MPMS3
        if systemSettings.system_name == 'Quantum Design MPMS3 SQUID-VSM':
            self.T = self.data[systemSettings.Tlabel]
            self.H = self.data[systemSettings.Hlabel]
            if MeasModeScan == 0:
                self.M = self.data[systemSettings.Mlabel]
                self.dM = self.data[systemSettings.Merrlabel]
    
            elif self.MeasModeScan == 1:
                self.M = self.data[systemSettings.DC_fixed_Mlabel]
                self.dM = self.data[systemSettings.DC_fixed_Merrlabel]
                
            elif self.MeasModeScan == 2:
                self.M = self.data[systemSettings.DC_free_Mlabel]
                self.dM = self.data[systemSettings.DC_free_Merrlabel]
                
        # Lakeshore
        elif systemSettings.system_name == 'Lakeshore VSM':
            self.H = self.data[systemSettings.Hlabel]
            self.M = self.data[systemSettings.Mlabel]
            self.dM = None
            self.T = None

    def split_mh_data(self):
        all_T = self.data[systemSettings.Tlabel].unique().sorted()

            
    def det_MeasType(self):
        Tavg = np.average(self.T)
        Havg = np.average(self.H)
        for t in self.T:
            if abs(t - Tavg) <= self.systemSettings.NoiseT:
                T_isconst = True
            else:
                T_isconst = False
        for h in self.H:
            if abs(h - Havg) <= self.systemSettings.NoiseH:
                H_isconst = True
            else:
                H_isconst = False
        if T_isconst == True and H_isconst == True:
            raise ValueError('Both temperature and field seem to be constant.')
        else:
            if T_isconst == True:
                self.FixedT = int(round(Tavg))
                self.MeasType = 'MH'
                # print('In the measurement in file {}, the temperature is fixed at {} K'.format(self.FileName, self.FixedT))
            elif H_isconst == True:
                self.FixedH = int(round(Havg))
                self.MeasType = 'MT'
                # print('In the measurement in file {}, the field is fixed at {} Oe'.format(self.FileName, self.FixedH))

    def set_MeasType(self, MeasType, FixedParam):
        self.MeasType = MeasType
        if MeasType == 'MH':
            self.FixedT = int(round(FixedParam))
        elif MeasType == 'MT':
            self.FixedH = int(round(FixedParam))
            

class Input:
    def __init__(self, systemSettings, IPFolder, MeasModeScan):
        self.systemSettings = systemSettings
        self.IPFileFormat = systemSettings.IPFileFormat
        self.NoiseT = systemSettings.NoiseT
        self.NoiseH = systemSettings.NoiseH
        self.IPFolder = IPFolder
        self.MeasModeScan = MeasModeScan

        self.read_AllAnaFiles()

    def read_AllAnaFiles(self):
        self.AllFilesInFolder = os.listdir(self.IPFolder)
        self.AllAnaFiles = []
        for ipName in self.AllFilesInFolder:
            file = mhFile(self.IPFolder+'/'+ipName, self.systemSettings, self.MeasModeScan)
            if file.fileExt == self.IPFileFormat:
                file.get_data()
                self.AllAnaFiles.append(file)

class Sample:
    def __init__(self, SampleID, IPSampleParamDBFileFolder, IPSampleParamDBFileFile):
        self.SampleID = SampleID
        self.IPSampleParamDBFileFolder = IPSampleParamDBFileFolder
        self.IPSampleParamDBFileFile = IPSampleParamDBFileFile
        self.IPSampleParamDBFileDir = IPSampleParamDBFileFolder+'/'+IPSampleParamDBFileFile

        self.read_SampleParamDB()

    def read_SampleParamDB(self):
        with open(self.IPSampleParamDBFileDir, 'r') as f:
            self.SampleParamDB = pd.read_csv(f, index_col='SampleID')
        self.Stack = self.SampleParamDB['Stack'].loc[self.SampleID]
        L1 = float(self.SampleParamDB['L1 (mm)'].loc[self.SampleID])
        L2 = float(self.SampleParamDB['L2 (mm)'].loc[self.SampleID])
        Area = float(self.SampleParamDB['Area (mm2)'].loc[self.SampleID])

        t = float(self.SampleParamDB['t (nm)'].loc[self.SampleID])
        self.Vuc = self.SampleParamDB['Vuc (nm3/f.u.)'].loc[self.SampleID]
        self.SampleDim = (L1, L2, Area, t) # (mm, mm, mm2, nm)

        self.rho = self.SampleParamDB['rho (g/cm3)'].loc[self.SampleID]
        self.M_uc = self.SampleParamDB['M_uc (g/mol)'].loc[self.SampleID]


class FileAnalysis:
    def __init__(self, file, Sample):
        self.file = file
        self.Sample = Sample


def report_progress(file_nb, AllFileAnalysis):
    FileAna = AllFileAnalysis[file_nb]
    print(f'Progress ({file_nb+1}/{len(AllFileAnalysis)}):')
    print(f'File: "{FileAna.file.fileName}"')


def saveIPparams(Sample, IP,
                 AutoParamSearch, MeasModeOrient, MeasModeMT, ModeMT, ModeMH,
                 MeasModeScan, HFLimit, MomOOM, FigBaseSizeMH, FigBaseSizeMT, FigBaseDPI,
                 OPFolder, SavePlot, PlotExt, SavePlotData):
    IPparams = {'SampleID': Sample.SampleID,
                'Stack': Sample.Stack,
                'SampleDim': Sample.SampleDim,
                'Vuc': Sample.Vuc,
                'IPFolder': IP.IPFolder,
                'IPFileFormat': IP.IPFileFormat,
                'IPFileDelimiterCode': IP.IPFileDelimiterCode,
                'NoiseT': IP.NoiseT,
                'NoiseH': IP.NoiseH,
                'AutoParamSearch': AutoParamSearch,
                'MeasModeOrient': MeasModeOrient,
                'MeasModeMT': MeasModeMT,
                'ModeMT': ModeMT,
                'ModeMH': ModeMH,
                'MeasModeScan': MeasModeScan,
                'HFLimit': HFLimit,
                'MomOOM': MomOOM,
                'FigBaseSizeMH': FigBaseSizeMH,
                'FigBaseSizeMT': FigBaseSizeMT,
                'FigBaseDPI': FigBaseDPI,
                'OPFolder': OPFolder,
                'SavePlot': SavePlot,
                'PlotExt': PlotExt,
                'SavePlotData': SavePlotData
                }
    IPparams = pd.Series(IPparams)
    OPIPparamsDir = OPFolder+r'/MHAnalyzer_inputParameters.csv'
    if os.path.isdir(OPFolder) == False:
                os.makedirs(OPFolder)
    # with open(OPIPparamsDir, 'w') as f:
    IPparams.to_csv(OPIPparamsDir, index=True)




















