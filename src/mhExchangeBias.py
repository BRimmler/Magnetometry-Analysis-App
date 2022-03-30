# # -*- coding: utf-8 -*-
# """
# Analysis module for exchange bias experiments with MPMS3

# @author: 
#     Berthold Rimmler, 
#     Max Planck Institute of Microstructure Physics, Halle
#     Weinberg 2
#     06120 Halle
#     berthold.rimmler@mpi-halle.mpg.de
# """

# # ____________________________________________________________________________
# # Data
# selectUI = False        # Select input folder from UI
# IPFolder = r'D:\owncloud\0_Personal\ANALYSIS\Mn3SnN\SQUID\00Code\Magnetometry-Analysis-code\demonstration_data\squid' # Ignore if selectUI == True

# # ____________________________________________________________________________
# # Sample
# SampleID = 'MA2960-3'

# IPSampleParamDBFileFolder = r'D:\owncloud\0_Personal\ANALYSIS\Mn3SnN\SQUID'
# IPSampleParamDBFileFile = 'squid_samples_sampleparameters.csv'

# ''' units: SampelDim (mm, mm, nm), Vuc (nm3 / f.u.). If sample dimensions
# were not measured, the data will not be normalised. '''

# # ____________________________________________________________________________
# # Measurements
# MeasModeOrient = 'IP'   # "IP" or "OP"
                
# # Additional settings for Quantum Design MPMS3:
# MeasModeScanMPMS = 0    # 0 = VSM
#                         # 1 = DC (Fixed Ctr)
#                         # 2 = DC (Free Ctr)

# # ____________________________________________________________________________
# # Data processing
# moment_units = [0, 1, 2]      # 0 = raw, 1 = emu/cm3, 2 = muB/f.u.

# subtract_lin = True
# HFQuadrants = [0,1,2,3] # quadrants used for substrate subtraction
# HFLimit = 36000         # High-field limit for substrate subtraction
# HFLimitMode = 'abs'     # Mode of high field limit: absolute ("abs") values or
#                         # relative to maximum value ("rel")

# # ____________________________________________________________________________
# # Plotting
# plot_type = 'errorbar'  # 'errorbar' or 'scatter'
# show_H_offset = True    # Shows offset field based on coercive fields (exchange bias)
# show_interp = False
# interp_density = 5     # Nb. of interp. points = length(data) * interp_density
# xaxis_in_Tesla = True   # Defines whether field should be displayed in Tesla or Oerstedt
# plt_error_bar = True    
# FigBaseSizeMH = (6,5)   # Better not to change
# FigBaseSizeMT = (5,3)   # Same

# MHInsetLimit = 500     # Oe
# FigBaseDPI = 300

# # ____________________________________________________________________________
# # Saving analysis
# fileSystem = 'Berthold'     # Set '' if unsure
# OPFolder = r'D:\owncloud\0_Personal\ANALYSIS\Mn3SnN\SQUID\00Code\Magnetometry-Analysis-code\demonstration_data\vsm'

# SaveOutput = True
# PlotExt = '.png'

# # ____________________________________________________________________________
# # Other settings (work in progress)
# AnalysisModeMT = 0      # 0 = M vs. T curves are plotted
# tempFileDirName = r'D:\ANALYSIS\Mn3SnN\SQUID\00Code\MHAnaTemp.txt'



#     AllFileAnalysis = []
#     T_list = []
#     Heb_list = []
#     Meb_list = []
#     for File in IP.AllAnaFiles:
#         AllFileAnalysis.append(hlp.FileAnalysis(File, Sample))

#     for i in range(2):
#         ''' first loop only to get same axis limits for all figures '''
#         FileIndex = -1
#         for FileAna in AllFileAnalysis:
#             FileIndex += 1
#             t = FileAna.file.FixedT
#             Hraw = FileAna.file.CrucData['Magnetic Field (Oe)']
#             H = Hraw * 1e-1 # conversion to mT
#             xlabel = '$H$ (mT)'
#             Mraw = FileAna.file.CrucData['Moment (emu)']
#             M = Mraw / MomOOM # conversion to muemu
#             ylabel = '$M$ ({} emu)'.format(MomOOM)

#             if i == 0:
#                 if eb_force_xlim is True:
#                     fig, ax = plt.subplots(figsize=FigBaseSizeMH, dpi=FigBaseDPI)
#                     ax.plot(H, M, label='$T$={} K'.format(FileAna.file.FixedT))
#                     ax.set_xlabel(xlabel)
#                     ax.set_ylabel(ylabel)
#                     ax.tick_params(direction='in',top=True,right=True)
#                     PlotTitle = 'EB ($H$ IP), T={} K'.format(FileAna.file.FixedT)
#                     ax.set_title(PlotTitle, fontsize=10)
#                     xlim = list(ax.get_xlim())
#                     ylim = list(ax.get_ylim())
#                     if FileIndex == 0:
#                         xlim_max = xlim
#                         ylim_max = ylim
#                     elif FileIndex > 0:
#                         for j in range(2):
#                             if abs(xlim[j]) > abs(xlim_max[j]):
#                                 xlim_max[j] = xlim[j]
#                             if abs(ylim[j]) > abs(ylim_max[j]):
#                                 ylim_max[j] = ylim[j]

#             elif i == 1:
#                 # try:
#                 Mint, Hc1, Hc2, Heb = hlp.extract_loop_chars(H, M, MeasMode, Hc_comp_mode=1)
#                 # print(Mint, Hc1, Hc2, Heb, Mr1_s, Mr2_s, Meb)

#                 ''' extract and plot Heb and Meb '''
#                 fig, ax = plt.subplots(figsize=FigBaseSizeMH, dpi=FigBaseDPI)
#                 ax.plot(H, M, label='$T$={} K'.format(FileAna.file.FixedT), zorder=-1)
#                 ax.set_xlabel(xlabel)
#                 ax.set_ylabel(ylabel)
#                 ax.tick_params(direction='in',top=True,right=True)
#                 PlotTitle = 'EB ($H$ {}), T={} K'.format(MeasModeOrient, FileAna.file.FixedT)
#                 ax.set_title(PlotTitle, fontsize=10)

#                 ax.scatter(Hc1, 0, c='g', marker='.', s=10)
#                 ax.scatter(Hc2, 0, c='g', marker='.', s=10)
#                 ax.scatter(Heb, 0, c='g', marker='.')
#                 # ax.annotate('$H_{EB}$', (Heb, 0))
#                 # ax.scatter(Heb, Mr1_s, c='r', marker='.', s=10)
#                 # ax.scatter(Heb, Mr2_s, c='r', marker='.', s=10)
#                 # ax.scatter(Heb, Meb, c='r', marker='.')
#                 try:
#                     ax.set_xlim(xlim_max)
#                     ax.set_ylim(ylim_max)
#                 except:
#                     pass
#                 # ax.annotate('$M_{EB}$', (Heb, Meb))
#                 boxtext = r'$H_{eb}=$'+'${:.2f}$ mT'.format(Heb)
#                         # r'$M_{eb}=$'+'${:.2f}$ {} emu'.format(Meb, MomOOM)))
#                 props = dict(boxstyle='round', facecolor='white', alpha=0.5)
#                 ax.text(0.05, 0.95, boxtext, verticalalignment='top',
#                         transform=ax.transAxes, bbox=props, fontsize=7)

#                 ''' safe for summary plot Heb vs. T and Meb vs. T '''
#                 Heb_list.append(Heb)
#                 # Meb_list.append(Meb)
#                 T_list.append(t)

#                 # Save Plot Data
#                 if SavePlot == True:
#                     if os.path.isdir(OPFolder) == False:
#                         os.makedirs(OPFolder)
#                     OPPlotFileName = FileAna.file.FileName.strip(IP.IPFileFormat)+'_plot'
#                     plt.savefig(OPFolder+r'/'+OPPlotFileName+PlotExt, bbox_inches = 'tight')
#                 # except:
#                 #     pass

#     # Plot EB vs. T
#     fig, ax = plt.subplots(2,1, dpi=FigBaseDPI)
#     ax0 = ax[0]
#     ax1 = ax[1]
#     ax0.scatter(T_list, np.array(Heb_list), color='tab:blue', label='$H_{EB}$')
#     # ax0.set_xlabel('$T$ (K)')
#     ax0.set_ylabel('$H_{EB}$ (mT)')
#     ax0.tick_params(direction='in',top=True,right=True)
#     ax0.get_xaxis().set_ticks([])
#     ax0.axhline(0, color='tab:gray', ls=':')

#     ax1.set_xlabel('$T$ (K)')
#     ax1.scatter(T_list, Meb_list, color='tab:orange', label='$M_{EB}$')
#     ax1.set_ylabel('$M_{EB}$'+' ({}emu)'.format(MomOOM))
#     ax1.tick_params(direction='in',top=True,right=True)
#     ax1.axhline(0, color='tab:gray', ls=':')

#     PlotTitle = '{}: {}\n Exchange bias {}'.format(AllFileAnalysis[0].Sample.SampleID,
#                                                     AllFileAnalysis[0].Sample.Stack,
#                                                     MeasModeOrient)
#     fig.suptitle(PlotTitle)

#     if SavePlot == True:
#         if os.path.isdir(OPFolder) == False:
#             os.makedirs(OPFolder)
#         OPPlotFileName = '_EB_vs_T'
#         plt.savefig(OPFolder+r'/'+OPPlotFileName+PlotExt, bbox_inches = 'tight')


# hlp.saveIPparams(Sample, IP,
#                  AutoParamSearch, MeasModeOrient, MeasModeMT, ModeMT, ModeMH,
#                  MeasModeScan, HFLimit, MomOOM, FigBaseSizeMH, FigBaseSizeMT, FigBaseDPI,
#                  OPFolder, SavePlot, PlotExt, SavePlotData)

