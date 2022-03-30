"""
Module to split file into MH curves at different temperatures

@author: 
    Berthold Rimmler, 
    Max Planck Institute of Microstructure Physics, Halle
    Weinberg 2
    06120 Halle
    berthold.rimmler@mpi-halle.mpg.de
"""

selectUI = True    # To open UI to select file to split. Alterantively, give path
path = r'D:\owncloud\0_Personal\DATA\Mn3SnN\SQUID\MA3407\220329\002_MA3407-2_220328_Qrod_IP_VSM_Hstable_EBloop_T_5-400K_fast.dat'

system = 0          # 0: MPMS3 SQUID-VSM
write_info = True
zfill_nb = 3        # Default: 3
decimals = 0        # Default: 0

# ____________________________________________________________________________
# CODE
import tkinter as tk
from tkinter import filedialog
from subs.mhSystemSettings import squidSystemSettings, vsmSystemSettings
from subs.files import File

def main(selectUI, path, system=0, write_info=True, zfill_nb=3, decimals=0):

    if system == 0:
        systemSettings = squidSystemSettings
    elif system == 1:
        systemSettings = vsmSystemSettings
    else:
        raise

    if selectUI is True:
        root = tk.Tk()
        path = filedialog.askopenfilename(parent=root, title='Choose directory with input data.')

    ipFile = File(path)

    ipFile.read(sep=systemSettings.IPFileDelimiter, info_stop_key=systemSettings.infoStopKey, dropna=False)
    split_data = ipFile.split_by_const_col(systemSettings.Tlabel, systemSettings.NoiseT)

    for data in split_data:
        T_fix = round(data[systemSettings.Tlabel].iloc[0], decimals)
        T_fix_str = str(T_fix).zfill(zfill_nb)
        
        opFileName = ipFile.fileNameWOExt + f'_{T_fix_str}' + ipFile.fileExt
        opFile = File(ipFile.fileDir+'/split', opFileName)
        opFile.makeDirIfNotExist()
        
        with open(opFile.fileDirName, 'w') as f:
            if write_info is True:
                for line in ipFile.info:
                    f.write(line)
            
        data.to_csv(opFile.fileDirName, index=False, mode='a')
                    
if __name__ == "__main__":
    main(selectUI, path, system, write_info, zfill_nb, decimals)




















