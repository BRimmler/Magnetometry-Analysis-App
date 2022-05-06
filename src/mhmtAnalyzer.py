# -*- coding: utf-8 -*-
"""
Analysis module for magnetometry data

@author: 
    Berthold Rimmler, 
    Max Planck Institute of Microstructure Physics, Halle
    Weinberg 2
    06120 Halle, Germany
    berthold.rimmler@mpi-halle.mpg.de
"""

# ____________________________________________________________________________
# Data
selectUI = False        # Select input folder from UI
IPFolder = r'D:\owncloud\0_Personal\DATA\NIZAF\NIZAF0004\220504' # Ignore if selectUI == True


# ____________________________________________________________________________
# Sample
SampleID = 'NIZAF0004'

IPSampleParamDBFileFolder = r'D:\owncloud\0_Personal\ANALYSIS\Mn3SnN\SQUID'
IPSampleParamDBFileFile = 'squid_samples_sampleparameters.csv'

''' units: SampelDim (mm, mm, nm), Vuc (nm3 / f.u.). If sample dimensions
were not measured, the data will not be normalised. '''

# ____________________________________________________________________________
# Measurements
system = 0              # 0: Quantum Design MPMS3 SQUID-VSM
                        # 1: Lakeshore VSM 
                        
MeasModeOrient = 'IP'   # "IP" or "OP"
                
# Additional settings for Quantum Design MPMS3:
MeasModeScanMPMS = 0    # 0 = VSM
                        # 1 = DC (Fixed Ctr)
                        # 2 = DC (Free Ctr)

# Additional settings for Lakeshore VSM:
MeasModeLS = 0          # 0 = at RT

# ____________________________________________________________________________
# Data processing
AutoParamSearch = True  # automatic recognition of constant parameter
moment_units = [0, 1, 2]      # 0 = raw, 1 = emu/cm3, 2 = muB/f.u.

HFQuadrants = [0,1,2,3] # quadrants used for substrate subtraction
HFLimit = 40000         # High-field limit for substrate subtraction
HFLimitMode = 'abs'     # Mode of high field limit: absolute ("abs") values or
                        # relative to maximum value ("rel")

# ____________________________________________________________________________
# Plotting
plot_type = 'errorbar'  # 'errorbar' or 'scatter'
show_H_offset = False    # Shows offset field based on coercive fields (exchange bias)
show_interp = False
interp_density = 5     # Nb. of interp. points = length(data) * interp_density
xaxis_in_Tesla = True   # Defines whether field should be displayed in Tesla or Oerstedt
plt_error_bar = True    
FigBaseSizeMH = (6,5)   # Better not to change
FigBaseSizeMT = (5,3)   # Same

MHInsetLimit = 2000     # Oe
FigBaseDPI = 300

# ____________________________________________________________________________
# Saving analysis
fileSystem = 'Berthold'     # Set '' if unsure
OPFolder = r'D:\owncloud\0_Personal\ANALYSIS\Mn3SnN\SQUID\00Code\Magnetometry-Analysis-code\demonstration_data\vsm'

SaveOutput = True
PlotExt = '.png'

# ____________________________________________________________________________
# Other settings (work in progress)
AnalysisModeMT = 0      # 0 = M vs. T curves are plotted
tempFileDirName = r'D:\ANALYSIS\Mn3SnN\SQUID\00Code\MHAnaTemp.txt'


# ____________________________________________________________________________
# Code
from subs.mhmtAnalyzerMain import main

if __name__ == "__main__":
    main(selectUI, IPFolder, SampleID, IPSampleParamDBFileFolder, IPSampleParamDBFileFile,
        system, MeasModeOrient, MeasModeScanMPMS, MeasModeLS, AutoParamSearch, moment_units,
        HFQuadrants, HFLimit, HFLimitMode, plot_type, show_H_offset, show_interp, interp_density,
        xaxis_in_Tesla, plt_error_bar, FigBaseSizeMH, FigBaseSizeMT, MHInsetLimit, FigBaseDPI, 
        fileSystem, OPFolder, SaveOutput, PlotExt, AnalysisModeMT, tempFileDirName)



















