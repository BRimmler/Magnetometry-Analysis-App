# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 08:37:55 2022

@author: rimmler
"""

class mhSystemSettings:
    def __init__(self, system_name, attr_dict):
        self.system_name = system_name
        self.attr_dict = attr_dict
        self.attr_from_dict()
        
    def attr_from_dict(self):
        for key, value in self.attr_dict.items():
            setattr(self, key, value)
            
# Quantum Design MPMS3 SQUID-VSM
qd_attr = {
        'IPFileFormat': '.dat',
        'IPFileDelimiter': ',',
        'infoStopKey': '[Data]',
        'Tlabel': 'Temperature (K)',
        'Hlabel': 'Magnetic Field (Oe)',
        'Mlabel': 'Moment (emu)',
        'Merrlabel': 'M. Std. Err. (emu)',
        'DC_fixed_Mlabel': 'DC Moment Fixed Ctr (emu)',
        'DC_fixed_Merrlabel': 'DC Moment Err Fixed Ctr (emu)',
        'DC_free_Mlabel': 'DC Moment Free Ctr (emu)',
        'DC_free_Merrlabel': 'DC Moment Err Free Ctr (emu)',
        'NoiseT': 1, # K
        'NoiseH': 1 # Oe
        }

squidSystemSettings = mhSystemSettings('Quantum Design MPMS3 SQUID-VSM', qd_attr)


# Lakeshore VSM
ls_attr = {
        'IPFileFormat': '.csv',
        'IPFileDelimiter': ',',
        'infoStopKey': '##DATA TABLE',
        # 'Tlabel': 'Temperature (K)', # !!!
        'Hlabel': 'Field [Oe]',
        'Mlabel': 'Moment (m) [emu]',
        # 'Merrlabel': 'M. Std. Err. (emu)', # !!!
        'NoiseT': 1, # K
        'NoiseH': 1 # Oe
        }

vsmSystemSettings = mhSystemSettings('Lakeshore VSM', ls_attr)



