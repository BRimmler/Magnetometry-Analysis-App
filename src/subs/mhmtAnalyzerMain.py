import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from  .mhHelpers import *
import tkinter as tk
from tkinter import filedialog
from .plots import GenPlot
from .hysteresis import GenHyst
from  .mhSystemSettings import squidSystemSettings, vsmSystemSettings
from .mhUnitConversion import *
from .outputs import *

def main(selectUI, IPFolder, SampleID, IPSampleParamDBFileFolder, IPSampleParamDBFileFile,
        system, MeasModeOrient, MeasModeScanMPMS, MeasModeLS, AutoParamSearch, moment_units,
        HFQuadrants, HFLimit, HFLimitMode, plot_type, show_H_offset, show_interp, interp_density,
        xaxis_in_Tesla, plt_error_bar, FigBaseSizeMH, FigBaseSizeMT, MHInsetLimit, FigBaseDPI, 
        fileSystem, OPFolder, SaveOutput, PlotExt, AnalysisModeMT, tempFileDirName):

    # Prepare output
    outputs = []

    # Get system settings
    if system == 0:
        systemSettings = squidSystemSettings
    elif system == 1:
        systemSettings = vsmSystemSettings
        MeasModeScanMPMS = 0
    else:
        raise

    # Get data and sample
    if selectUI is True:
        root = tk.Tk()
        IPFolder = filedialog.askdirectory (parent=root, title='Choose directory with input data.')
        root.destroy()
        
    # Berthold system:
    if fileSystem == 'Berthold':
        OPFolder = IPFolder.replace('DATA', 'ANALYSIS')

    IP = Input(systemSettings, IPFolder, MeasModeScanMPMS)
    sample = Sample(SampleID, IPSampleParamDBFileFolder, IPSampleParamDBFileFile)

    if os.path.isfile(tempFileDirName):
        os.remove(tempFileDirName) # remove temporary storage file


    if AutoParamSearch == True:
        for file in IP.AllAnaFiles:
            if system == 0:
                file.det_MeasType()
            elif system == 1:
                if MeasModeLS == 0:
                    file.set_MeasType('MH', 300)
                
    else:
        raise ValueError('Not implemented')

    # Analysis
    AllFileAnalysis = []
    for file in IP.AllAnaFiles:
        AllFileAnalysis.append(FileAnalysis(file, sample))

    extracted_params_summ = {}
    for file_nb, FileAna in enumerate(AllFileAnalysis):
        opData = pd.DataFrame()
        report_progress(file_nb, AllFileAnalysis)
        
        # _________________________________________________________________________
        # Analsis of M vs. T curves 
        if FileAna.file.MeasType == 'MT': 
            
            T = FileAna.file.T
            H = FileAna.file.H
            M = FileAna.file.M
            M_err = FileAna.file.dM
            
            for m_unit in moment_units:
                if m_unit == 0:
                    ylabel = '$m$ (emu)'
                    savelabel = 'emu'
                elif m_unit == 1:
                    M = conv_emu_to_emucc(M, FileAna.Sample.SampleDim)
                    M_err =  conv_emu_to_emucc(M_err, FileAna.Sample.SampleDim)
                    ylabel = '$M$ ($emu/cm^3$)'
                    savelabel = 'emucc'
                elif m_unit == 2:
                    M = conv_emu_to_muB_per_fu(M, FileAna.Sample.SampleDim,
                                                FileAna.Sample.rho, FileAna.Sample.M_uc)
                    M_err =  conv_emu_to_muB_per_fu(M_err, FileAna.Sample.SampleDim,
                                                FileAna.Sample.rho, FileAna.Sample.M_uc)
                    ylabel = '$M$ ($\mu_B/f.u.$)'
                    savelabel = 'muBfu'
                
                title = '{}: {}\n $M$($T$), {}'.format(FileAna.Sample.SampleID, FileAna.Sample.Stack, MeasModeOrient)
                
                mt_plt = GenPlot(xlabel='$T$ (K)', ylabel=ylabel, title=title, figsize=FigBaseSizeMT, dpi=FigBaseDPI)
        
                if plt_error_bar == False:
                    M_err = None
        
                MTScanType = {}
                if T.to_numpy()[0] > T.to_numpy()[-1]:
                    MTScanType['direction'] = 'C'
                else:
                    MTScanType['direction'] = 'W'
        
                H_avg = int(round(np.average(H.to_numpy())))
                if abs(H_avg) < 1:
                    MTScanType['H_avg (Oe)'] = 0
                    MTScanType['field'] = 'ZF'
                    MTScanType['labelAddition'] = ''
        
                else:
                    MTScanType['H_avg (Oe)'] = H_avg
                    MTScanType['field'] = 'F'
                    MTScanType['labelAddition'] = ', H = {} Oe'.format(H_avg)
                    if AnalysisModeMT == 1:
                        MTScanType['bgMode'] = ', bg subtracted'
                    else:
                        MTScanType['bgMode'] = ''
        
                MTScanType['descr'] = MTScanType['field']+MTScanType['direction']+MTScanType['labelAddition']+MTScanType['bgMode']
                
                if plot_type == 'errorbar':
                    mt_plt.errorbar(T, M, label=MTScanType['descr'])
                elif plot_type == 'scatter':
                    mt_plt.scatter(T, M, label=MTScanType['descr'])
                else:
                    raise ValueError('Not a valid plot_type')

                pltName = FileAna.file.fileNameWOExt + f'_plt_{savelabel}'
                outputs.append(GenPlotOutput(mt_plt, OPFolder, pltName, 
                                                saveData=True, fig_ext=PlotExt))

        # _________________________________________________________________________
        # Analsis of M vs. H loops
        elif FileAna.file.MeasType == 'MH': 
            extracted_params = {}
            
            H = FileAna.file.H
            M = FileAna.file.M
            M_err = FileAna.file.dM
            
            if plt_error_bar == False:
                M_err = None
                
            title = '{}: {}\n $M$($H$), {}'.format(FileAna.Sample.SampleID,
                                                FileAna.Sample.Stack,
                                                MeasModeOrient)            
            hyst_init = GenHyst(H, M, yerr=M_err)
            
            
            hyst_init.define_high_x_lim(HFLimit, mode=HFLimitMode)
            
            if xaxis_in_Tesla is True:
                hyst_init = hyst_init.scale_axis('x', 1e-4, old_unit='Oe', new_unit='T')
                MHInsetLimit *= 1e-4 # to T
                xunit = 'T'
            else:
                xunit = 'Oe'
                
            hyst_lin_sub_init, hyst_substr_init = hyst_init.subtract_lin(HFQuadrants)
            hyst_lin_sub_init.get_full_loop_chars()
            
            for m_unit in moment_units:
                if m_unit == 0:
                    scaling_factor = 1
                    ylabel = '$m$ (emu)'
                    yunit = 'emu'
                    m_unit_verb = 'emu'
                    new_unit = 'emu'
                elif m_unit == 1:
                    scaling_factor = conv_fact_emu_to_emucc(FileAna.Sample.SampleDim)
                    ylabel = '$M$ ($emu/cm^3$)'
                    yunit = 'emu/cm$^3$'
                    m_unit_verb = 'emucc'
                    new_unit = 'emu/cm3'
                elif m_unit == 2:
                    scaling_factor = conv_fact_emu_to_muB_per_fu(FileAna.Sample.SampleDim,
                                                                    FileAna.Sample.rho, FileAna.Sample.M_uc)
                    ylabel = '$M$ ($\mu_B/f.u.$)'
                    yunit = '$\mu_B$/f.u.'
                    m_unit_verb = 'muBfu'
                    new_unit = 'muB/f.u.'
                    
                # Scale hysteresis based on magnetization unit
                old_unit = 'emu'
                hyst = hyst_init.scale_axis('y', scaling_factor, 
                                            old_unit=old_unit, new_unit=new_unit)
                hyst_lin_sub = hyst_lin_sub_init.scale_axis('y', scaling_factor, 
                                                            old_unit=old_unit, new_unit=new_unit)  
                hyst_substr = hyst_substr_init.scale_axis('y', scaling_factor,
                                                        old_unit=old_unit, new_unit=new_unit)

                xlabel = hyst.xlabel
                fig, ax = plt.subplots(1, 3,
                                    figsize=(3*FigBaseSizeMH[0], FigBaseSizeMH[1]),
                                    dpi=FigBaseDPI)
                plt.subplots_adjust(wspace=.2)
                plt.subplots_adjust(top=0.9)
                ax[0].errorbar(hyst.x, hyst.y, yerr=hyst.yerr, label='Raw data')
                ax[0].errorbar(hyst_substr.x, hyst_substr.y, yerr=hyst_substr.yerr, label='Substrate contribution')
                ax[0].legend()

                for i in [1,2]:
                    if plot_type == 'errorbar':
                        ax[i].errorbar(hyst_lin_sub.x, hyst_lin_sub.y, yerr=hyst_lin_sub.yerr, color='g', label='Film contribution')
                    elif plot_type == 'scatter':
                        ax[i].scatter(hyst_lin_sub.x, hyst_lin_sub.y, color='g', label='Film contribution')
                    else:
                        raise ValueError('Not a valid plot_type')
                    if show_interp is True:
                        hyst_lin_sub.get_loop_interp(interp_density)
                        ax[i].scatter(hyst_lin_sub.data_interp[0]['x'], hyst_lin_sub.data_interp[0]['y'], color='c', s=5, label='Interpolation')
                        ax[i].scatter(hyst_lin_sub.data_interp[1]['x'], hyst_lin_sub.data_interp[1]['y'], color='c', s=5)
                    
                    for c, char_key in enumerate(['saturation', 'coercivity', 'remanence']):
                        color = ['b', 'r', 'y']
                        char = getattr(hyst_lin_sub, char_key)
                        if char_key == 'saturation':
                            label = '$M_s$='+'{:.2e} {}'.format(char.avg_abs_point[1], yunit)
                            if i == 1:
                                extracted_params[f'M_s ({m_unit})'] = char.avg_abs_point[1]
                        elif char_key == 'coercivity':
                            label = '$H_c$='+'{:.2e} {}'.format(char.avg_abs_point[0], xunit)
                            if i == 1:
                                extracted_params[f'H_c ({xunit})'] = char.avg_abs_point[0]
                        if char_key == 'remanence':
                            label = '$M_r$='+'{:.2e} {}'.format(char.avg_abs_point[1], yunit)
                            if i == 1:
                                extracted_params[f'M_r ({m_unit})'] = char.avg_abs_point[1]
                            
                        for p, point in enumerate(char.points):
                            x, y = point
                            if p == 0 and i == 1:
                                ax[i].scatter(x, y, label=label, color=color[c])
                            else:
                                ax[i].scatter(x, y, color=color[c])



                                
                    if show_H_offset is True:
                        x, y = getattr(hyst_lin_sub, 'coercivity').cntr_point
                        label = '$H_{off}$='+'{:.2e} {}'.format(x, xunit)
                        ax[i].scatter(x, y, label=label, color='m')
                        if i == 1:
                            extracted_params[f'M_off ({m_unit})'] = x
                
                ax[1].legend()
                ax[2].set_xlim(-MHInsetLimit, MHInsetLimit)
        
                for i in range(3):
                    ax[i].set_xlabel(xlabel)
                    ax[i].set_ylabel(ylabel)
                    ax[i].tick_params(direction='in',top=True,right=True)
                    ax[i].ticklabel_format(axis='y', style='sci', scilimits=(-4, 4), useOffset=False)
                    
                PlotTitle = '{}: {}: $M$($H$) at $T$={} K, {}'.format(FileAna.Sample.SampleID,
                                                            FileAna.Sample.Stack,
                                                            FileAna.file.FixedT,
                                                            MeasModeOrient)
                fig.suptitle(PlotTitle)
                
                # Data for output
                mhOutputData = pd.DataFrame()
                for df in [hyst.data, hyst_substr.data, hyst_lin_sub.data]:
                    for columnName, columnData in df.iteritems(): 
                        # print(type(columnData))
                        if columnName not in mhOutputData.columns:
                            mhOutputData = pd.concat([mhOutputData, columnData], axis=1)

                # Extracted parameters summary output


                # Output
                pltName = FileAna.file.fileNameWOExt + f'_plt_{m_unit_verb}{PlotExt}'
                outputs.append(PlotOutput(fig, OPFolder, pltName, 
                                            saveDataFrame=mhOutputData))



        
    # Saving outputs
    for output in outputs:
        output.save()
