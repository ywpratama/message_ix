# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 15:41:32 2023

@author: pratama
"""

import ixmp
import message_ix
import numpy as np
import os
import pandas as pd
import yaml
from collections.abc import Mapping
from itertools import repeat
from message_ix.models import MESSAGE_ITEMS
from message_ix.utils import make_df


def get_values(scenario,
               variable = '', valuetype = 'lvl',
               #filters = {}
              ): 
    # filters must use 'cat_tec' to aggregate technology
    # don't forget to include check unit
    """
    Parameters
    ----------
    scenario    : message_ix.Scenario()
        MESSAGEix Scenario where the data will be included
    variable    : string
        name of variable to report
    valuetype   : string, 'lvl' or 'mrg'
        type of values reported to report,
        either level or marginal.
        default is 'lvl'
    """
    
    if isinstance(scenario.var(variable), pd.DataFrame): # this is specific for technology, hence all should be dataframe already
        df = scenario.var(variable)
        dimensions = [col for col in df.columns if col not in ['lvl','mrg']]
        return df.set_index(dimensions)[[valuetype]]
    else:
        return scenario.var(variable)[valuetype]

groups = {'DACs': ['LT_DAC','HT_DAC']}

def get_report(scenario,
               grouptec = '',
              ): 
    """
    Parameters
    ----------
    scenario    : message_ix.Scenario()
        MESSAGEix Scenario where the data will be included
    grouptec    : string
        type of values reported to report,
        either level or marginal.
        default is 'lvl'
    variable    : string
        name of variable to report
    """
    var_dict = {var: [] for var in ['CAP','CAP_NEW']}
    
    for var in var_dict.keys():
        df = (get_values(scenario,var)['lvl'].unstack()
              .loc[:,groups.get(grouptec),:]
              .groupby(['node_loc']).sum()
             )
        df.loc['World'] = df.sum(axis=0)
        
        var_dict[var] = df
        
        return print(df) # TODO: This need to be printing to excel
    