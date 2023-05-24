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


def generate_df(
        filepath=""
        ):
    if not filepath:
        module_path = os.path.abspath(__file__)                                 # get the module path
        package_path = os.path.dirname(os.path.dirname(module_path))            # get the package path
        path = os.path.join(package_path, 'add_tech/tech_data.yaml')          # join the current working directory with a filename
        with open(path,'r') as stream:
            tech_data = yaml.safe_load(stream)
    else:
        with open(filepath,'r') as stream:
            tech_data = yaml.safe_load(stream)
    
    years = [*range(700,730,10)]
    regions = ['Westeros', 'Westerlands']
    modes = ['standard']
    emissions = ['CO2','CH4']
    time = ['year']
    first_active_year = tech_data['model_data'].get('first_active_year')

    years_dict = {yv:[ya for ya in years if ya >= yv] for yv in years if yv >= first_active_year}

    vtg = [yv for ya in list(years_dict.keys()) for yv in repeat(ya,len(years_dict[ya]))]
    
    act = [yv for ya in list(years_dict.keys()) for yv in repeat(ya,len(years_dict[ya]))]
    
    years_vtg_act = pd.DataFrame(
        {
        'year_vtg':[k for k, v in years_dict.items() for i in range(len(v))],
        'year_act':[ya for value in years_dict.values() for ya in value]
        }
    )
    
    parameters = {}
    for tech in set(tech_data) - set(['model_data']):
        parameters.update({par: list(MESSAGE_ITEMS[par]['idx_names']) for par in set(tech_data[tech])})
    data = {par: [] for par in list(parameters.keys())}

    # Basic DataFrame
    for tech, par_dict in tech_data.items():
        if tech != 'model_data':
            for par, par_data in par_dict.items():
                if not isinstance(par_data, Mapping):
                    par_data = {'value': par_data, 'unit': '-'}
                if parameters[par] == ['node_loc', 'technology', 'year_vtg']:
                    kwargs = {'year_vtg': sorted(list(set(years_vtg_act['year_vtg'])))}
                elif all(e in ['node_loc', 'technology', 'year_vtg', 'year_act'] for e in parameters[par]):
                    kwargs = {'year_vtg': years_vtg_act['year_vtg'],
                              'year_act': years_vtg_act['year_act']}
                data[par].append(
                    make_df(
                        par,
                        technology=tech,
                        value=par_data['value'],
                        unit=par_data['unit'],
                        **kwargs,
                    ))
                if 'emission' in parameters[par]:
                    data[par] = data[par]*len(emissions)
                    for e in range(len(emissions)):
                        data[par][e] = data[par][e].assign(emission=emissions[e])
                if 'mode' in parameters[par]:
                    data[par] = data[par]*len(modes)
                    for m in range(len(modes)):
                        for e in range(len(data[par])):
                            data[par][e] = data[par][e].assign(mode=modes[m])
                if 'time' in parameters[par]:
                    data[par] = data[par]*len(time)
                    for t in range(len(time)):
                        for e in range(len(data[par])):
                            data[par][e] = data[par][e].assign(time=time[t])
    data = {k: pd.concat(v).reset_index(drop=True) for k, v in data.items()}
    
    # Expanded DataFrame
    data_expand ={par: [] for par in list(parameters.keys())} 
    for par in list(parameters.keys()):
        for tech, diffs in tech_data['model_data'].items():
            if tech != 'first_active_year':
                for reg in regions:
                    print(par,tech,reg)
                    multiplier = []
                    for i in range(len(data[par])):
                        multiplier.append(
                            np.prod([diffs.get(par,{}).get('node_loc',{}).get(reg,1), # by region 
                                     ((1+diffs.get(par,{}).get('year_vtg',{}).get('rate',0))
                                      **(data[par]['year_vtg'][i]-first_active_year)), # by year_vtg
                                     ((1+diffs.get(par,{}).get('year_act',{}).get('rate',0))
                                      **(data.get(par,{}).get('year_act',{}) # by year_act
                                         .get(i,data[par]['year_vtg'][i])-data[par]['year_vtg'][i])),
                                     diffs.get(par,{}).get('mode',{}).get(data.get(par,{}).get('mode',{}).get(i),1), # by mode
                                     diffs.get(par,{}).get('emission',{}).get(data.get(par,{}).get('emission',{}).get(i),1), # by emission
                            ])
                        )
    
                    value = data[par]['value']*multiplier
                    data_expand[par].append(
                        data[par].assign(node_loc=reg,value=value)
                       )
    
    data_expand = {k: pd.concat(v) for k, v in data_expand.items() 
               if k in parameters.keys()}
    return data_expand
    
def print_df(
        filepath=""
        ):
    if not filepath:
        module_path = os.path.abspath(__file__)                                 # get the module path
        package_path = os.path.dirname(os.path.dirname(module_path))            # get the package path
        path = os.path.join(package_path, 'add_tech/tech_data.yaml')          # join the current working directory with a filename
        data = generate_df(path)
        with pd.ExcelWriter('printed_data.xlsx', engine='xlsxwriter', mode='w') as writer:
            for sheet_name, sheet_data in data.items():
                sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        data = generate_df(filepath)
        with pd.ExcelWriter('printed_data.xlsx', engine='xlsxwriter', mode='w') as writer:
            for sheet_name, sheet_data in data.items():
                sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)

#%% now modify everything below using data from the functions above    
def add_tech(
    scenario,
    technology=[],
    parameter=[],
    node="all",
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
    parameter   : list, optional
        list of parameters to be included 
        the default is all parameters
    node        : list, optional
        list of nodes in which the technology is included
        the default is all nodes
    file        : string, path of the input file
        the default is in the module's folder
    """

    # Reading new technology database
    if not filepath:
        module_path = os.path.abspath(__file__)                                 # get the module path
        package_path = os.path.dirname(os.path.dirname(module_path))            # get the package path
        path = os.path.join(package_path, 'add_tech/tech_data.xlsx')          # join the current working directory with a filename
        df = pd.read_excel(path,index_col=0)
    else:
        df = pd.read_excel(filepath,index_col=0)

    year_df = scenario.vintage_and_active_years()
    vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]
    
    for tech in technology:
        if df.isna()[tech]['year_vtg']:                                         # check, technology somehow cannot be a list
            yv = vintage_years
        else:
            yv = df[tech]['year_vtg']
        
        if df.isna()[tech]['year_act']:
            ya = act_years
        else:
            ya = df[tech]['year_act']
        
        if df.isna()['unit']['time']:
            t_unit = '-'
        else:
            t_unit = df['unit']['time']
        
        
        if tech not in set(scenario.set("technology")):
            scenario.add_set("technology", tech)
        
        if not parameter:
            df_param = df.apply(pd.to_numeric, errors='coerce')
            parameter = df_param[tech].dropna().index
        
        df_in = df[tech]
                
        for par in parameter:
            if par == 'input':
                par_data = make_df(
                    par,
                    node_loc=df_in['node_loc'],
                    year_vtg=yv,
                    year_act=ya,
                    mode=df_in['mode'],
                    emission=df_in['emission'],
                    time=df_in['time'],
                    unit=t_unit,
                    technology=tech,
                    commodity=df_in['commodity_in'],
                    level=df_in['level_in'],
                    value=df_in[par],
                    node_origin=df_in['node_loc'], 
                    time_origin=df_in['time'],
                    )
                scenario.add_par(par, par_data)
            elif par == 'output':
                par_data = make_df(
                    par,
                    node_loc=df_in['node_loc'],
                    year_vtg=yv,
                    year_act=ya,
                    mode=df_in['mode'],
                    emission=df_in['emission'],
                    time=df_in['time'],
                    unit=t_unit,
                    technology=tech,
                    commodity=df_in['commodity_out'],
                    level=df_in['level_out'],
                    value=df_in[par],
                    node_dest=df_in['node_loc'], 
                    time_dest=df_in['time'],
                    )
                scenario.add_par(par, par_data)
            else:
                par_data = make_df(
                    par,
                    node_loc=df_in['node_loc'],
                    year_vtg=yv,
                    year_act=ya,
                    mode=df_in['mode'],
                    emission=df_in['emission'],
                    time=df_in['time'],
                    unit=t_unit,
                    technology=tech,
                    value=df_in[par],
                    )
                scenario.add_par(par, par_data)

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
    
    parameter = ['learning_par','eos_par','nbr_unit_ref','u_ref','u']
    # Reading new technology database
    if not filepath:
        module_path = os.path.abspath(__file__) # get the module path
        package_path = os.path.dirname(os.path.dirname(module_path)) # get the package path
        path = os.path.join(package_path, 'add_tech/tech_data.xlsx') # join the current working directory with a filename
        df = pd.read_excel(path,index_col=0)
    else:
        df = pd.read_excel(filepath,index_col=0)

    for tech in technology:
        if tech not in set(scenario.set("technology")):
            scenario.add_set("technology", tech)
        
        df_in = df[tech]
    
        size = df_in['size'].split(',')
        
        
        for z in size:
            if z not in set(scenario.set("size")):
                scenario.add_set("size", z)

        
        for par in parameter:
            if par == 'u':
                val = [float(i) for i in df_in['u'].split(',')]
                for v in range(len(val)):
                    par_data = make_df(
                        par,
                        technology=tech,
                        value=val[v],
                        unit='-',
                        size=size[v])
                    scenario.add_par(par, par_data)
            else:
                val = df_in[par]
                par_data = make_df(
                    par,
                    technology=tech,
                    value=val,
                    unit='-',
                    size=z)
                scenario.add_par(par, par_data)
