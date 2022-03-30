# -*- coding: utf-8 -*-
"""
Unit conversion module.
"""

def do_conv(val, factor, backwards=False):
    '''
    Conversion based on given conversion factor and direction of conversion

    Parameters
    ----------
    val : float or array type
        Value in input units.
    factor : float
        Conversion factor.
    backwards : bool, optional
        Backward conversion from out to in. The default is False.

    Returns
    -------
    new_val : float or array type
        Value after unit conversion.

    '''
    
    if backwards is False:
        new_val = val * factor
    else:
        new_val = val / factor
    return new_val

def conv(val, unit_in, unit_out):
    '''
    Conversion based on given input and output units, assuming the conversion
    factor is listed in conversion_factors.py

    Parameters
    ----------
    val : float or array type
        Value in input units.
    unit_in : str
        Units of input value.
    unit_out : str
        Wanted units of output value.

    Raises
    ------
    ValueError
        If cannot find conversion factor in database.

    Returns
    -------
    out : float or array type
        Value after unit conversion..

    '''
    conv_key = f'{unit_in}_{unit_out}'
    conv_key_backward = f'{unit_out}_{unit_in}'
    if conv_key in C.keys():
        out = do_conv(val, C[conv_key])
    elif conv_key_backward in C.keys():
        out = do_conv(val, C[conv_key_backward], backwards=True)
    else:
        raise ValueError('conversion coefficient not defined')
    return out
        
# _____________________________________________________________________________
# Special cases
      
def deg2rad(val):
    ''' Angle in degree to radian '''
    return deg_to_rad(val)

def rad2deg(val):
    ''' Angle in radian to degree '''
    return rad_to_deg(val)








