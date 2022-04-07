# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 11:03:33 2022

@author: rimmler
"""
import math
from .units import do_conv

def conv_fact_emu_to_emucc(SampleDim):
    '''
    Parameters
    ----------
    SampleDim : array
        Sampel dimensions as array with units (mm, mm, mm2, nm) 

    Returns
    -------
    c : float
        Conversion factor from emu to emu/cm3
    '''
    
    if math.isnan(SampleDim[2]): 
        # Area not defined, Sample dimensions given in L1 and L2
        V_film = SampleDim[0]*1e-1 * SampleDim[1]*1e-1 * SampleDim[3]*1e-7 # cm3
    elif math.isnan(SampleDim[0]) and math.isnan(SampleDim[1]): 
        # L1 and L2 not defined, Sample dimensions given in Area
        V_film = SampleDim[2]*1e-2 * SampleDim[3]*1e-7 # cm3
    else:
        raise ValueError('Could not calculate film volume.')
    c = 1. / V_film
    return c
    
def conv_fact_emu_to_muB_per_fu(SampleDim, rho, W):
    '''
    Parameters
    ----------
    SampleDim : array
        Sampel dimensions as array with units (mm, mm, mm2, nm).
    rho : float
        Film material density in g/cm3,.
    W : float
        Film material molar mass in g/mol.

    Returns
    -------
    c : float
        Conversion factor from emu to emu/cm3
    '''
    
    c1 =  conv_fact_emu_to_emucc(SampleDim) # Conversion factor from emu to emu/cm3
    c2 = 5584.93 # conversion factor in f.u./mol * emu/muB
    c = c1 * W / rho / c2
    
    return c

def conv_emu_to_emucc(mu_in_emu, SampleDim):
    '''
    Parameters
    ----------
    mu_in_emu : float or array
        Moment in emu.
    SampleDim : array
        Sampel dimensions as array with units (mm, mm, mm2, nm).

    Returns
    -------
    mu_in_emucc : float or array
        Moment in emu/cm3.
    '''
    c = conv_fact_emu_to_emucc(SampleDim)
    mu_in_emucc = do_conv(mu_in_emu, c)
    return mu_in_emucc

def conv_emu_to_muB_per_fu(mu_in_emu, SampleDim, rho, W):
    '''
    Parameters
    ----------
    mu_in_emu : float or array
        Moment in emu.
    SampleDim : array
        Sampel dimensions as array with units (mm, mm, mm2, nm).
    rho : float
        Film material density in g/cm3.
    W : float
        Film material molar mass in g/mol.

    Returns
    -------
    mu_in_muB_per_fu : float or array
        Moment in muB/f.u.
    '''
    c = conv_fact_emu_to_muB_per_fu(SampleDim, rho, W)
    mu_in_muB_per_fu = do_conv(mu_in_emu, c)
    return mu_in_muB_per_fu













