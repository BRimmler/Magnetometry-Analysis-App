# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 22:50:12 2022

@author: Berthold Rimmler
"""

# _____________________________________________________________________________
# Modules
import numpy as np
import pandas as pd
from scipy.stats import linregress
from .plots import GenPlot
from .hysteresis_helpers import get_enum_indices, hyst_interp, scale_tuple
from .pandas_helpers import pd_find_closest
import inspect
import copy as c

# _____________________________________________________________________________
# Hysteresis class
class GenHyst:
    # _________________________________________________________________________
    # Init
    def __init__(self, x, y, xerr=None, yerr=None, name=None, history=None):
        '''
        Parameters
        ----------
        x : pd.Series
            x values as pandas Series.
        y : pd.Series
            y values as pandas Series..
        xerr : pd.Series, optional
            x error values as pandas Series.. The default is None.
        yerr : pd.Series, optional
            x error values as pandas Series.. The default is None.
        name : str, optional
            Name of the hysteresis. By default, will be constructed.
        history : History, optional
            History instance of the hysteresis. The default is None.

        Returns
        -------
        General Hysteresis object.
        '''
        
        # Check if pd.Series
        if not isinstance(x, pd.Series):
            raise ValueError('x is not a pd.Series.')
        if not isinstance(y, pd.Series):
            raise ValueError('y is not a pd.Series.')
            
        if xerr is not None and not isinstance(xerr, pd.Series):
            raise ValueError('xerr is not a pd.Series.')
          
        if yerr is not None and not isinstance(yerr, pd.Series):
            raise ValueError('yerr is not a pd.Series.')
      
        # Add to self
        self.x = x
        self.y = y
        self.xerr = xerr
        self.yerr = yerr
        
        self.data = pd.DataFrame()
        self.data = pd.concat([self.data, x],axis=1)
        self.data = pd.concat([self.data, y],axis=1)
        
        if xerr is not None:
            self.data = pd.concat([self.data, xerr],axis=1)
        if yerr is not None:
            self.data = pd.concat([self.data, yerr],axis=1)
         
        # Data labels
        self.xlabel = x.name
        self.ylabel = y.name
        if xerr is not None:
            self.xerrlabel = xerr.name
        if yerr is not None:
            self.yerrlabel = yerr.name
        
        # Name
        if name is None:
            self.name = f'{self.ylabel} vs. {self.xlabel}'
        else:
            self.name = name
            
        # History
        if history is None:
            self.history = History()
        else:
            self.history = history
           
        self._get_lims()
        self._get_looptype()
        self.plots = [] # List compiling all plots
        
    # _________________________________________________________________________
    # Analysis
    def _get_lims(self):
        def _get_lim(i):
            pos_high = max(i)
            neg_high = min(i)
            return pos_high, neg_high

        pos_high, neg_high = _get_lim(self.data[self.xlabel])
        self.xlims = {'+x': pos_high, '-x': neg_high}
        pos_high, neg_high = _get_lim(self.data[self.ylabel])
        self.ylims = {'+y': pos_high, '-y': neg_high}

    def _is_halfloop(self):
        X = self.data[self.xlabel].to_numpy()
        increasing = []
        for i, x in enumerate(X):
            if i > 0:
                if x > X[i-1]:
                    increasing.append(True)
                else:
                    increasing.append(False)
        increasing = np.array(increasing)
        if np.all(increasing==True):
            out = (True, 'increasing')
        elif np.all(increasing==False):
            out = (True, 'decreasing')
        else:
            out = (False, 'non-uniform')
        return out
    
    def _get_looptype(self):
        looptype = None
        is_halfloop, direction = self._is_halfloop()
        if is_halfloop:
            looptype = f'half_{direction}'
        else:
            looptype = 'full'
        self.looptype = looptype
        
                
    def split_half(self, find_half=True, ignore_edge_data=True, n_ignore=5):
        if not self.looptype == 'full':
            raise ValueError('Not a valid method if looptype is not "full"')
            
        if find_half is False:
            half_length = len(self.data[self.xlabel]) // 2
            split_index = half_length
            
        else:
            X = self.data[self.xlabel].to_numpy()
            start_enum_index, stop_enum_index = get_enum_indices(X, ignore_edge_data, n_ignore)
            
            for i, x in enumerate(X):
                if i > start_enum_index and i < stop_enum_index:
                    if np.sign(X[i]-X[i-1]) != np.sign(X[i-1]-X[i-2]):
                        '''
                        x values start to go in another direction as before.
                        This is considered the point where the data changes
                        direction. 
                        '''
                        break
            split_index = i
            
        self.data_split_half = [self.data.iloc[:split_index], self.data.iloc[split_index-1:]]
        self.half_split_index = split_index
        
        
        
    def split_quarter(self, find_quarter=True, ignore_edge_data=True, n_ignore=5):
        if self.looptype == 'full':
            if find_quarter is False:
                quarter_length = len(self.data[self.xlabel]) // 4
                split_indices = [quarter_length, 2*quarter_length, 3*quarter_length]
                
            else:
                X = self.data[self.xlabel].to_numpy()
                start_enum_index, stop_enum_index = get_enum_indices(X, ignore_edge_data, n_ignore)
                    
                split_indices = []
                for i, x in enumerate(X):
                    if i > start_enum_index and i < stop_enum_index:
                        conditions = [
                            np.sign(X[i]) != np.sign(X[i-1]), # Going through zero
                            np.sign(X[i]-X[i-1]) != np.sign(X[i-1]-X[i-2]) # Changing direction
                            ]
                        if any(conditions):
                            split_indices.append(i)
                            
                # print(split_indices)
                if not len(split_indices) == 3:
                    raise ValueError('Problem while quarter splitting. Not correct number of split indices')    
            
            self.data_split_quarter = [self.data.iloc[:split_indices[0]], 
                                       self.data.iloc[split_indices[0]:split_indices[1]],
                                       self.data.iloc[split_indices[1]-1:split_indices[2]],
                                       self.data.iloc[split_indices[2]:]
                                       ]
            self.quarter_split_indices = split_indices
            
        elif self.looptype.split('_')[0] == 'half':
            if find_quarter is False:
                quarter_length = len(self.data[self.xlabel]) // 2
                split_index = quarter_length
            else:
                X = self.data[self.xlabel].to_numpy()
                start_enum_index, stop_enum_index = get_enum_indices(X, ignore_edge_data, n_ignore)
                
                for i, x in enumerate(X):
                    if i > start_enum_index and i < stop_enum_index:
                        if np.sign(X[i]-X[i-1]) != np.sign(X[i-1]-X[i-2]):
                            break
                split_index = i
            
            self.data_split_quarter = [self.data.iloc[:split_index], self.data.iloc[split_index:]]
            self.quarter_split_indix = split_index
            
    
    def define_high_x_lim(self, limit, mode='rel'):
        ''' Define high x limit as relative (mode="rel") or absolute (mode="abs"). 
            Relative means relative to the larger max x limit '''
        if mode == 'rel':
            max_abs_xlim = np.max(np.abs(np.array(list(self.xlims.values()))))
            self.high_x_lim = limit * max_abs_xlim
        elif mode == 'abs':
            self.high_x_lim = limit
        else:
            raise ValueError('mode not defined')
      
    # _________________________________________________________________________            
    # Data manipulation    
    def shift_data_y(self, criterion='remanence'):
        if not self.looptype == 'full':
            raise ValueError('currently, only full loops can be analyzed.')
        
        if not hasattr(self, 'data_split_half'):
            self.split_half(find_half=True)
            
        if criterion == 'remanence':
            y0s = []
            for data in self.data_split_half:
                f_interp, y_interp = hyst_interp(data, self.xlabel, self.ylabel)
                y0 = f_interp(0)
                y0s.append(y0)
            y_offset = np.mean(y0s)
            
        new_data_y_array = self.data[self.ylabel] - y_offset
        
        new_ylabel = self.ylabel+'_y-shifted',
        new_data_y = pd.Series(new_data_y_array)
        new_data_y.name = new_ylabel
        
        frame = inspect.currentframe()
        new_history = c.deepcopy(self.history)
        new_history.add_step_from_frame(frame)
        
        overwrite = {
            'y': new_data_y,
            'name': None,
            'history': new_history
            }
        
        copy = ['high_x_lim']
        new_hyst = self.gen_hyst_from_self(overwrite=overwrite, copy=copy)
        
        return new_hyst
        
            
    def subtract_lin(self, quadrants=[0, 1, 2, 3]):
        if not hasattr(self, 'high_x_lim'):
            raise ValueError('high_x_lim not defined')
            
        if not hasattr(self, 'data_split_quarter'):
            self.split_quarter()
        
        if self.looptype == 'full':
            nb_q = 4
        else:
            nb_q = 2
            
        slopes_in_qs = []
        for q in quadrants:
            if q-1 > nb_q:
                raise ValueError(f'Quadrant {q} > total number of quadrants of {nb_q}')
            
            data = self.data_split_quarter[q]
            data_high_x = data[data[self.xlabel].abs() > self.high_x_lim]
            try:
                slope, intercept, r, p, se  = linregress(data_high_x[self.xlabel], data_high_x[self.ylabel])
            except:
                raise ValueError('Failed lin regress. High field limit too high?')
            slopes_in_qs.append(slope)
        
        lin_slopes_in_quadrants_avg = np.average(slopes_in_qs)
        
        lin_part_array = lin_slopes_in_quadrants_avg * self.data[self.xlabel].to_numpy()
        new_data_y_array = self.data[self.ylabel].to_numpy() - lin_part_array
        
        new_ylabel = self.ylabel+'_y-lin-subtract'
        new_data_y = pd.Series(new_data_y_array, name=new_ylabel)
        
        lin_part_label = self.ylabel+'_lin-part'
        lin_part = pd.Series(lin_part_array, name=lin_part_label)
        
        
        frame = inspect.currentframe()
        new_history = c.deepcopy(self.history)
        new_history.add_step_from_frame(frame)

        overwrite = {
            'y': new_data_y,
            'name': None,
            'history': new_history
            }
        
        overwrite_lin = {
            'y': lin_part,
            'name': None,
            'history': new_history
            }
        
        copy = ['high_x_lim']
        new_hyst = self.gen_hyst_from_self(overwrite=overwrite, copy=copy)
        
        lin_hyst = self.gen_hyst_from_self(overwrite=overwrite_lin, copy=copy)
        lin_hyst.lin_slopes_in_quadrants_avg = lin_slopes_in_quadrants_avg
        
        return new_hyst, lin_hyst
            
    def scale_axis(self, axis, factor, old_unit=None, new_unit=None, new_label=None, new_errlabel=None):
        if axis not in [self.xlabel, self.ylabel, 'x', 'y']:
            raise ValueError('Not a valid axis label')
            
        if old_unit is not None and new_unit is not None:
            replace_unit = True
        else:
            replace_unit = False
            
        # Scale Data
        if axis == 'x':
            axis_int = 0
            # Axis values
            new_x = self.x * factor
            new_y = self.y
            
            # Error
            if self.xerr is not None:
                new_xerr = self.xerr * factor
            else:
                new_xerr = None
            new_yerr = self.yerr
            
            # Labels
            if new_label is not None:
                new_x.name = new_label
            if new_errlabel is not None:
                new_xerr.name = new_errlabel
                
            # Unit
            if replace_unit is True:
                new_x.name = new_x.name.replace(old_unit, new_unit)
                if new_xerr is not None:
                    new_xerr = new_xerr.name.replace(old_unit, new_unit)
                
        elif axis == 'y':
            axis_int = 1
            # Axis values
            new_y = self.y * factor
            new_x = self.x
            
            # Error
            if self.yerr is not None:
                new_yerr = self.yerr * factor
            else:
                new_yerr = None
            new_xerr = self.xerr
            
            # Labels
            if new_label is not None:
                new_y.name = new_label
            if new_errlabel is not None:
                new_yerr.name = new_errlabel
            
            # Unit
            if replace_unit is True:
                new_y.name = new_y.name.replace(old_unit, new_unit)
                if new_yerr is not None:
                    new_yerr.name = new_yerr.name.replace(old_unit, new_unit)

        frame = inspect.currentframe()
        new_history = c.deepcopy(self.history)
        new_history.add_step_from_frame(frame)
        
        overwrite = {
            'x': new_x,
            'y': new_y,
            'xerr': new_xerr,
            'yerr': new_yerr,
            'name': None,
            'history': new_history
            }
        new_hyst = self.gen_hyst_from_self(overwrite=overwrite)
        
        
        # Update units
        if new_unit is not None:
            if axis == 'x':
                new_hyst.xunit = new_unit
            elif axis == 'y':
                new_hyst.yunit = new_unit
        
        # Scale other attributes and add to new hyst
        poss_attr_keys = ['high_x_lim', 'remanence', 'coercivity', 'saturation', 'saturation_zero_extrapol']
        for attr_key in poss_attr_keys:
            if hasattr(self, attr_key):
                old_attr = getattr(self, attr_key)
                if isinstance(old_attr, (float, int)):
                    new_attr = old_attr * factor
                elif isinstance(old_attr, LoopChar):
                    new_attr = old_attr.scale(axis_int, factor)
                else:
                    raise ValueError(f'Attribute {attr_key} of type {type(old_attr)} could not be scaled')
                
                setattr(new_hyst, attr_key, new_attr)
        
        return new_hyst
        
            
          
    # _________________________________________________________________________            
    # Extraction of loop characteristics    
    def get_full_loop_chars(self, interp_density=100):
        self.get_loop_interp(interp_density)
        self.get_remanence()
        self.get_coercivity()
        self.get_saturation()
        self.get_saturation_zero_extrapol()
        
    # def report_loop_chars(self, chars='full'):
    #     if chars == 'full':
    #         chars = ['remanence', 'coercivity', 'saturation', 'saturation_zero_extrapol']
        
    #     for char in chars:
            
    def get_data_to_process(self):
        if not self.looptype == 'full':
            print('WARNING: Only full loops have been tested.')
        
        if not self.looptype == 'full':
            self.data_to_process = [self.data]
        else:
            if not hasattr(self, 'data_split_half'):
                self.split_half(find_half=True)
            self.data_to_process = self.data_split_half
            
    def get_loop_interp(self, interp_density, check_if_exists=True):
        if check_if_exists is True:
            if not hasattr(self, 'data_interp'):
                if not hasattr(self, 'data_to_process'):
                    self.get_data_to_process()
                    
                self.data_interp = []
                for data in self.data_to_process:
                    loop_interp_f, loop_interp_y = hyst_interp(data, self.xlabel, self.ylabel)
                    n = len(data) * interp_density 
                    x_test = np.linspace(.95*data[self.xlabel].min(), .95*data[self.xlabel].max(), n)
                    y_test = loop_interp_f(x_test)
                    self.data_interp.append({
                        'f': loop_interp_f, # The interpolation function
                        'x': x_test, # A test x range
                        'y': y_test # interpoalted y values on the test x range
                        })
            
    def get_remanence(self):
        self.remanence = LoopChar('remanence')
        for interp in self.data_interp:
            rem = float(interp['f'](0))
            self.remanence.append_point((0, rem))
        self.remanence.calc_center()  
        self.remanence.calc_average_abs()
      
            
    def get_coercivity(self):
        self.coercivity = LoopChar('coercivity')
        for interp in self.data_interp:
            test_x = pd.Series(interp['x'])
            test_y = pd.Series(interp['y'])
            index, val = pd_find_closest(test_y, 0)
            coerc = test_x.iloc[index]
            
            self.coercivity.append_point((coerc, 0.))
        self.coercivity.calc_center()
        self.coercivity.calc_average_abs()
            
    def get_saturation(self, data_range='above_high_x_lim'):
        '''
        Parameters
        ----------
        data_range : str, optional
            Defines the range of data used when mode=="high_x". There are two modes:
                "at_first_x": Will take the values at the positive and negative 
                maximum x value. In case of full loop, it will average the 
                two points from the two halfloops at these points.
                "above_high_x_lim": Averages over all values above the high x
                limit defined before. Again will average halfloops.
                The default is "at_first_x".
        '''
            
        self.saturation = LoopChar('saturation')
        self.saturation.data_range = data_range
        
        sat_min = []
        sat_max = []
        for data in self.data_to_process:
            if data_range == 'at_first_x':
                sat_min.append(data.sort_values(by=self.xlabel).to_numpy()[0])
                sat_max.append(data.sort_values(by=self.xlabel).to_numpy()[-1])
            elif data_range == 'above_high_x_lim':
                if not hasattr(self, 'high_x_lim'):
                    raise ValueError('high_x_lim not defined')
                sat_min_range = data[data[self.xlabel] < -self.high_x_lim]
                sat_max_range = data[data[self.xlabel] > self.high_x_lim]
                sat_min.append(sat_min_range.mean().to_numpy())
                sat_max.append(sat_max_range.mean().to_numpy())
            else:
                raise
                    
        self.saturation.sat_min = sat_min
        self.saturation.sat_max = sat_max   
        for i in range(len(self.saturation.sat_min)):
            sat_min_avg_x = np.average([self.saturation.sat_min[0][0], self.saturation.sat_min[1][0]])
            sat_min_avg_y = np.average([self.saturation.sat_min[0][1], self.saturation.sat_min[1][1]])
            sat_max_avg_x = np.average([self.saturation.sat_max[0][0], self.saturation.sat_max[1][0]])
            sat_max_avg_y = np.average([self.saturation.sat_max[0][1], self.saturation.sat_max[1][1]])
        self.saturation.append_point((sat_min_avg_x, sat_min_avg_y))
        self.saturation.append_point((sat_max_avg_x, sat_max_avg_y))
        self.saturation.calc_center()
        self.saturation.calc_average_abs()
        
            
    def get_saturation_zero_extrapol(self):
        self.saturation_zero_extrapol = LoopChar('saturation-zero-extrapol')
        
        self.saturation_zero_extrapol.extrapols = []
        for data in self.data_to_process:
            if not hasattr(self, 'high_x_lim'):
                raise ValueError('high_x_lim not defined')
            if data[self.xlabel].iloc[0] > 0: # Data must be decreasing in x
                sat_range = data[data[self.xlabel] > self.high_x_lim]
            else: # Data must be increasing in x
                sat_range = data[data[self.xlabel] < -self.high_x_lim]
                
            x = sat_range[self.xlabel].to_numpy()
            y = sat_range[self.ylabel].to_numpy()
            slope, intercept, r, p, se  = linregress(x, y)
            self.saturation_zero_extrapol.append_point((0, intercept))
            self.saturation_zero_extrapol.extrapols.append({'slope': slope, 'intercept': intercept})
            
        self.saturation_zero_extrapol.calc_center()
        self.saturation_zero_extrapol.calc_average_abs()
        
        
    def gen_hyst_from_self(self, overwrite={}, copy=[]):
        init_keys = ['x', 'y', 'xerr', 'yerr', 'name', 'history']
        new_vals = {}
        for key in init_keys:
            old_val = getattr(self, key)
            if key in overwrite.keys():
                new_val = overwrite[key]
            else:
                new_val = old_val
            new_vals[key] = new_val
            
        new_hyst = GenHyst(new_vals['x'], new_vals['y'], new_vals['xerr'], new_vals['yerr'],
                           new_vals['name'], new_vals['history'])
        
        for key in copy:
            if hasattr(self, key):
                setattr(new_hyst, key, getattr(self, key))
        return new_hyst             
        
        
        
    # _________________________________________________________________________
    # Loop plotting
    def _pass_plot(self, x, y, plt, style, label, **kwargs):        
        if style == 'plot':
            plt.plot(x, y, label=label, **kwargs)
        elif style == 'scatter':
            plt.scatter(x, y, label=label, **kwargs)
        else:
            raise
        
    def plot(self, data_type='full', style='plot', plt=None, **kwargs):
        if data_type == 'full':
            mode = 'basic'
            xlabel = self.xlabel
            ylabel = self.ylabel
            title = self.name
            x = self.data[self.xlabel]
            y = self.data[self.ylabel]
            label = 'full data'
        
        elif data_type.split('-')[0] == 'halfloop': 
            loop_index = int(data_type.split('-')[1])
            mode = 'basic'
            xlabel = self.xlabel
            ylabel = self.ylabel
            title = f'{self.name}, half loop(s)'
            x = self.data_split_half[loop_index][self.xlabel]
            y = self.data_split_half[loop_index][self.ylabel]
            label = f'half loop {loop_index}'
            
        if plt is None:
            ''' A already existing plot may be passed. If not, create a new plot '''
            plt = GenPlot(mode=mode, xlabel=xlabel, ylabel=ylabel, title=title)
        self._pass_plot(x, y, plt, style, label, **kwargs)
        self.plots.append(plt)

            
    def plot_raw(self, style='plot', plt=None, **kwargs):
        self.plot(style=style, plt=plt, **kwargs)
        
    def plot_halfloop(self, nb, style='plot', plt=None, **kwargs):
        self.plot(data_type=f'halfloop-{nb}', plt=plt, **kwargs)
        
    def plot_halfloops(self, in_one=True, style='plot', **kwargs):
        if in_one is True:
            self.plot_halfloop(0, **kwargs)
            plt = self.plots[-1]
            self.plot_halfloop(1, plt=plt)
        else:
            for i in range(2):
                self.plot(data_type=f'halfloop-{i}')
                
    # _________________________________________________________________________
    # Dunders
    def __str__(self):
        return f'hysteresis "{self.name}"'

# _____________________________________________________________________________
# _____________________________________________________________________________
''' Loop characteristic class used in GenHyst class '''
class LoopChar:
    def __init__(self, char_type):
        if char_type in ['remanence', 'coercivity', 'saturation', 'saturation-zero-extrapol']:
            self.char_type = char_type
        else:
            raise ValueError('Not a valid characteristic')
            
        self.points = []
        
        
    def append_point(self, point):
        if isinstance(point, tuple):
            self.points.append(point)
        else:
            raise
            
    def _calc_average(self, mode):
        def _average(mode, i0, i1):
            if mode == 'abs':
                i = np.mean([abs(i0), abs(i1)])
            elif mode == 'cntr':
                i = np.mean([i0, i1])
            else:
                raise
            return i
        
        if self.char_type in ['coercivity', 'saturation']:
            x0 = self.points[0][0]
            x1 = self.points[1][0]
            x = _average(mode, x0, x1)
        else:
            x = 0.
            
        if self.char_type in ['remanence', 'saturation', 'saturation-zero-extrapol']:
            y0 = self.points[0][1]
            y1 = self.points[1][1]
            y = _average(mode, y0, y1)
        else:
            y = 0.
        
        return x, y
    
    def calc_average_abs(self):
        ''' Calculates the average of the absolute values '''
        self.avg_abs_point = self._calc_average(mode='abs')
        
        
    def calc_center(self):
        ''' Calculates the center position of the absolute values '''
        self.cntr_point = self._calc_average(mode='cntr')
        
    def scale(self, axis, factor):
        ''' Scales LoopChar by factor '''
        if axis in ['x', 'y']:
            if axis == 'x':
                axis = 0
            elif axis == 'y':
                axis = 1
            else:
                raise
        
        
        new_loopchar = c.deepcopy(self)
        
        new_points = []
        for point in self.points:
            new_point = scale_tuple(point, factor, axis)
            new_points.append(new_point)

        new_loopchar.points = new_points
        
        for key in  ['avg_abs_point', 'cntr_point']:
            point = getattr(self, key)
            new_point = scale_tuple(point, factor, axis)
            
            setattr(new_loopchar, key, new_point)
        
        return new_loopchar
        
        
# _____________________________________________________________________________
# _____________________________________________________________________________
''' History class used in GenHyst class '''       
class History:
    def __init__(self):
        self.full_hist = []
        
    def add_step(self, name, params):
        self.full_hist.append({'step': name, 'parameters': params})
        
    def add_step_from_frame(self, frame):
        func_name =  inspect.getframeinfo(frame).function
        args,_,_,values = inspect.getargvalues(frame)
        # args = args.remove('self')
        params = {}
        for arg in args:
            params[arg] = values[arg]
        params.pop('self')
        self.add_step(func_name, params)



# _____________________________________________________________________________
# _____________________________________________________________________________
# Testing
# from files import File

# testDataDir = r'D:\owncloud\0_Personal\ANALYSIS\python\analysis-modules\testdata'

# # # PPMS test data
# # # testDataName = r'Mn3SnN_ppms_testdata.dat'
# # # testDataFile = File(testDataDir, testDataName)
# # # testData = pd.read_csv(testDataFile.fileDirName, sep='\t')
# # # x_test = testData['Field (Oe)']
# # # y_test = testData['Rxy1 (Ohm)']
# # # hyst = GenHyst(x_test, y_test, xlabel='Field (Oe)', ylabel='Rxy (Ohm)')
# # # hyst.plot()
# # # hyst_shift = hyst.shift_data_y()
# # # hyst_shift.plot()

# # SQUID test data
# testDataNames = [
#     r'Mn3SnN_squid_testdata.dat', 
#     # r'MA2959-3_210809_Qrod_IP_MH_7T_stableH_VSM_300K.dat'
#     ]
# for testDataName in testDataNames:
#     testDataFile = File(testDataDir, testDataName)
#     testData = pd.read_csv(testDataFile.fileDirName, sep=',')
#     x_test = testData['Magnetic Field (Oe)']
#     y_test = testData['Moment (emu)']
    
#     hyst = GenHyst(x_test, y_test)
    
#     hyst.plot()
#     hyst.define_high_x_lim(3.5e4, mode='abs')
#     # hyst_linsub = hyst.subtract_lin()
#     # hyst_linsub.plot()
#     # hyst_linsub.get_full_loop_chars()
    
#     hyst_T = hyst.scale_axis('x', 1e-4, new_label='Field (T)')
#     # hyst_T = hyst_linsub.scale_axis('y', 100, new_label='test')
#     # hyst_T.get_full_loop_chars()
#     hyst_T.plot()
    

# from files import File

# testDataDir = r'D:\owncloud\0_Personal\ANALYSIS\python\analysis-modules\testdata'
# testDataName = r'Mn3SnN_squid_testdata.dat', 
# testDataFile = File(testDataDir, testDataName)
# testData = pd.read_csv(testDataFile.fileDirName, sep=',')
# x_test = testData['Magnetic Field (Oe)']
# y_test = testData['Moment (emu)']

# hyst = GenHyst(x_test, y_test)

# hyst.plot()
# hyst.define_high_x_lim(3.5e4, mode='abs')
# # hyst_linsub = hyst.subtract_lin()
# # hyst_linsub.plot()
# # hyst_linsub.get_full_loop_chars()

# hyst_T = hyst.scale_axis('x', 1e-4, new_label='Field (T)')
# # hyst_T = hyst_linsub.scale_axis('y', 100, new_label='test')
# # hyst_T.get_full_loop_chars()
# hyst_T.plot()
    



        
 
    
 
    
 
    
 
    
 
    
 
    
 
    
 
    
 
    
 
  
  
  
  
  
  