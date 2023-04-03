# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 15:41:32 2023

@author: pratama
"""

import pandas as pd
import ixmp
import message_ix
import os
from message_ix.utils import make_df

def include_tech(
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
        path = os.path.join(package_path, 'genie_tech/tech_data.xlsx')          # join the current working directory with a filename
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

def include_learning(
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
    parameter = ['learning_rate','eos_rate']
    # Reading new technology database
    if not filepath:
        module_path = os.path.abspath(__file__) # get the module path
        package_path = os.path.dirname(os.path.dirname(module_path)) # get the package path
        path = os.path.join(package_path, 'genie_tech/tech_data.xlsx') # join the current working directory with a filename
        df = pd.read_excel(path,index_col=0)
    else:
        df = pd.read_excel(filepath,index_col=0)

    for tech in technology:
        if tech not in set(scenario.set("technology")):
            scenario.add_set("technology", tech)
        
        df_in = df[tech]
            
    for par in parameter:
        par_data = make_df(
            par,
            technology=tech,
            value=df_in[par],
            )
        scenario.add_par(par, par_data)
