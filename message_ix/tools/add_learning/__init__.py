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


def create_learning_data(
        filepath=""
        ):
    if not filepath:
        module_path = os.path.abspath(__file__)                                     # get the module path
        package_path = os.path.dirname(os.path.dirname(module_path))                # get the package path
        path = os.path.join(package_path, 'add_learning/learning_data.yaml')        # join the current working directory with a filename
        with open(path,'r') as stream:
            learning_data = yaml.safe_load(stream)
    else:
        with open(filepath,'r') as stream:
            learning_data = yaml.safe_load(stream)
    
    parameters = {}
    for tech in list(learning_data.keys()):
        parameters.update({par: list(MESSAGE_ITEMS[par]['idx_sets']) for par in list(learning_data[tech])})
    data = {par: [] for par in list(parameters.keys())}

    # Creating The Individual DataFrame
    for tech, par_dict in learning_data.items():
        for par, par_data in par_dict.items():
            if not isinstance(par_data, Mapping):
                par_data = {'value': par_data, 'unit': '-'}
            if 'size' in parameters[par]:
                value = list(par_data['value'].values())
                kwargs = {'size': list(par_data['value'].keys())}
            else:
                value = par_data['value']
                kwargs = {}
            data[par].append(
                    make_df(
                        par,
                        technology=tech,
                        value=value,
                        unit=par_data['unit'],
                        **kwargs
                    ))

    data = {k: pd.concat(v).reset_index(drop=True) for k, v in data.items()}

    return data
    
def print_learning_par(
        filepath=""
        ):
    if not filepath:
        module_path = os.path.abspath(__file__)                                     # get the module path
        package_path = os.path.dirname(os.path.dirname(module_path))                # get the package path
        path = os.path.join(package_path, 'add_learning/learning_data.yaml')        # join the current working directory with a filename
        data = create_learning_data(path)
        with pd.ExcelWriter('printed_data.xlsx', engine='xlsxwriter', mode='w') as writer:
            for sheet_name, sheet_data in data.items():
                sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        data = create_learning_data(filepath)
        with pd.ExcelWriter('printed_data.xlsx', engine='xlsxwriter', mode='w') as writer:
            for sheet_name, sheet_data in data.items():
                sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)

def add_learning(
    scenario,
    technology=[],
    parameter=[],
    filepath=""
    ):
    
    """
    Parameters
    ----------
    scenario    : message_ix.Scenario()
        MESSAGEix Scenario where the data will be included
    technology  : list, optional 
        additional technologies that will be included in the model
        the default is all technologies in the input file
    filepath    : string, path of the input file
        the default is in the module's folder
    """
    
    # Reading new technology database
    if not filepath:
        module_path = os.path.abspath(__file__) # get the module path
        package_path = os.path.dirname(os.path.dirname(module_path)) # get the package path
        path = os.path.join(package_path, 'add_learning/learning_data.yaml') # join the current working directory with a filename
        data = create_learning_data(path)
    else:
        data = create_learning_data(filepath)
    
    if not parameter:
        parameter = list(data.keys())
    for par in parameter:
        if not technology:
            technology = list(set(data[par]['technology']))
        for tech in technology:
            if tech not in set(scenario.set("technology")):
                scenario.add_set("technology", tech)
            
            if tech not in set(scenario.set("learning_tec")):
                scenario.add_set("learning_tec", tech)
            selected_data = data[par][data[par]['technology'] == tech]

            if 'size' in list(selected_data.columns):            
                size = list(set(selected_data['size']))
                for z in size:
                    if z not in set(scenario.set("size")):
                        scenario.add_set("size", z)
            scenario.add_par(par, selected_data)
    
    # importing initial investment cost as reference and intially-assumed costs in technology learning module
    inv_base_data = scenario.par('inv_cost')
    for tech in technology:
        if tech in set(inv_base_data['technology']):
            hist_year = 2020
            first_vtg_year = scenario.par('inv_cost', filters={'technology':tech})['year_vtg'].iloc[0]

            ref_year = first_vtg_year if first_vtg_year > hist_year else hist_year

            inv_ref_data = scenario.par('inv_cost',filters={'year_vtg':ref_year,'technology':tech}).drop(columns='year_vtg')
            scenario.add_par('inv_cost_ref', inv_ref_data)

            inv_data = scenario.par('inv_cost',filters={'technology':tech})

            for reg in list(set(inv_data['node_loc'])):
                selected_data = inv_data[(inv_data['node_loc'] == reg) & (inv_data['year_vtg'] >= ref_year)]
                selected_data['value'] = selected_data[selected_data['year_vtg'] == ref_year]['value'].iloc[0]
                # adding new data to the data input
                scenario.add_par('inv_cost', selected_data)

        else:
            print('\'inv_cost_ref\' data for',tech,'is not available.\n',
                  tech,'will not be considered in technology cost learning')
            