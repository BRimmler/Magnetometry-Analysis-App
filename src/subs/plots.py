# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 11:15:55 2021

@author: Berthold Rimmler
"""

''' IMPORTS '''
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from .files import File
from .plots_settings import plots_settings as st

''' CLASSES '''
class GenPlot:
    """ Generic plot class """
    def __init__(self,
                 mode='basic',xlabel='',ylabel='',title='', save_label=None,
                 **kwargs):
        self._get_mode(mode)
        self.ax_running_nb = 0

        if mode == 'basic':
            fig, ax = plt.subplots(**kwargs)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.tick_params(direction='in',top=True,right=True)
            ax.ticklabel_format(axis='both', style='sci', scilimits=st.scilimits, useOffset=False)
        elif mode == 'vstack-share-x':
            fig, ax = plt.subplots(2, 1, **kwargs)
            for axi in ax:
                axi.set_xlabel(xlabel)
                axi.tick_params(direction='in',top=True,right=True)
                axi.ticklabel_format(axis='both', style='sci', useOffset=False)
        elif mode == 'hstack-share-x':
            fig, ax = plt.subplots(1, 2, **kwargs)
            for axi in ax:
                axi.set_xlabel(xlabel)
                axi.tick_params(direction='in',top=True,right=True)
                axi.ticklabel_format(axis='both', style='sci', useOffset=False)
                
        elif mode == 'pass-axes':
            fig = plt.figure()
            try:
                ax = []
                for axis in kwargs['axes']:
                    ax.append(axis)
            except:
                raise ValueError('Define axes')

        fig.suptitle(title, fontsize=st.suptitle_fontsize)
        
        if save_label is None:
            self.save_label = title
        else:
            self.save_label = save_label

        self.fig = fig
        self.ax = ax
        self.data = pd.DataFrame()


    def _get_mode(self, mode):
        modes = ['basic', 'vstack-share-x', 'hstack-share-x', 'pass-axes']
        if type(mode) is str and mode in modes:
            self.mode = mode
        elif type(mode) is int:
            self.mode = modes[mode]

    def _append_data(self, x, y, label):
        x = pd.Series(x, name=label+'_x').reset_index(drop=True)
        y = pd.Series(y, name=label+'_y').reset_index(drop=True)
        
        # self.data.merge(x, left_index=True, right_index=True)
        # self.data.merge(y, left_index=True, right_index=True)
        self.data = pd.concat([self.data, x],axis=1)
        self.data = pd.concat([self.data, y], axis=1)

    def _pass_plot(self, mode, x, y, axis, xerr=None, yerr=None, **kwargs):
        # print(kwargs)
        if self.mode == 'basic':
            ax = self.ax
        elif self.mode in ['vstack-share-x', 'hstack-share-x']:
            ax = self.ax[axis]
        else:
            raise
            

        if 'label' in kwargs:
            label = kwargs['label']
        else:
            label = str(self.ax_running_nb)
            self.ax_running_nb += 1

        if mode == 'plot':
            ax.plot(x, y, **kwargs)
        elif mode == 'scatter':
            ax.scatter(x, y, **kwargs)
        elif mode == 'bar':
            x_ticks = np.arange(len(x))
            ax.bar(x_ticks, y, **kwargs)
            ax.set_xticks(x_ticks)
            ax.set_xticklabels(x)

        # Error bar plots
        if mode in ['errorbar', 'errorbar_scatter']:
            if not 'capsize' in kwargs:
                capsize = st.errorbar_cap_size # If capsize not defined take from settings file
                kwargs['capsize'] = capsize
            if mode == 'errorbar':
                ax.errorbar(x, y, xerr=xerr, yerr=yerr, **kwargs)
            elif mode == 'errorbar_scatter':
                ax.errorbar(x, y, xerr=xerr, yerr=yerr, fmt="o", **kwargs)
            else:
                raise

        ax.legend()
        self._append_data(x, y, label)


    def plot(self, x, y, axis=0, **kwargs):
        self._pass_plot('plot', x, y, axis, **kwargs)

    def scatter(self, x, y, axis=0, **kwargs):
        self._pass_plot('scatter', x, y, axis, **kwargs)

    def errorbar(self, x, y, xerr=None, yerr=None, axis=0, **kwargs):
        self._pass_plot('errorbar', x, y, axis, xerr, yerr, **kwargs)

    def errorbar_scatter(self, x, y, xerr=None, yerr=None, axis=0, **kwargs):
        self._pass_plot('errorbar_scatter', x, y, axis, xerr, yerr, **kwargs)
        
    def bar(self, x, y, axis=0, xerr=None, yerr=None, **kwargs):
        self._pass_plot('bar', x, y, xerr, yerr, axis, **kwargs)

    def make_nonsci_axis(self, axis='both'):
        self.ax.ticklabel_format(axis=axis, style='plain', useOffset=False)

    def make_boxtext(self, boxtext, axis=0):
        if self.mode == 'basic':
            ax = self.ax
        elif self.mode == 'vstack-share-x':
            ax = self.ax[axis]
        else:
            raise

        bt = boxtext
        ax.text(bt.pos_x, bt.pos_y, boxtext.full_text, verticalalignment=bt.verticalalignment,
                transform=ax.transAxes, bbox=bt.props, fontsize=bt.fontsize)
        
    def report(self, opDir, opName=None, SI=(), saveData=False, fig_ext='.png', dat_ext='.csv'):
        if opName is None:
            opName = self.save_label
        if opName.split('.')[-1] in ['png', 'csv']:
            opName = opName[:-4]
        for ext in [fig_ext, dat_ext]:
            if ext[0] != '.':
                raise

        fileFig = File(opDir, opName+fig_ext)
        fileDat = File(opDir+'/plot_data', opName+'_dat'+dat_ext)
        fileFig.makeDirIfNotExist()
        if saveData is True:
            fileDat.makeDirIfNotExist()

        self.fig.savefig(fileFig.fileDirName, bbox_inches='tight')

        if saveData is True:
            self.data.to_csv(fileDat.fileDirName, index=False)
            # print(SI)
            if not len(SI) == 0:
                self.SI = SI
                fileSI = File(opDir+'/plot_data', opName+'_SI'+dat_ext)
                fileSI.makeDirIfNotExist()
                SI.to_csv(fileSI.fileDirName, header=False)


class BoxText:
    ''' Generic boxtext for plots '''
    def __init__(self, pos_x, pos_y, verticalalignment='top',
                 fontsize=10, props=dict(boxstyle='round', facecolor='white', alpha=0.5)):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.verticalalignment = verticalalignment
        self.fontsize = fontsize
        self.props = props
        self.full_text = ''

    def add_text(self, text):
        if not self.full_text == '':
            self.full_text += '\n'
        self.full_text += text

    def add_param(self, label, value, verb_name=None, unit='', rep='f', dec=2, error=None):
        form = f'{dec}{rep}'
        if error is None:
            val_str = f'{value:.{form}}'
        else:
            err_dec = dec
            err_form = f'{err_dec}{rep}'
            val_str = f'({value:.{form}}' + '$\pm$' + f'{error:.{err_form}})'

        if verb_name is not None:
            param_str = f'{verb_name}: '
        else:
            param_str = ''

        param_str += f'{label}=' + val_str + f'{unit}'
        self.add_text(param_str)
        
    def add_empty_line(self):
        self.add_text('')


