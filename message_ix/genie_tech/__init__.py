# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 15:41:32 2023

@author: pratama
"""

import pandas as pd
import ixmp
import message_ix
from message_ix.utils import make_df

def include_tech(
    scenario,
    technology=None,
    parameter=[],
    node="all",
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
    """

    # Reading new technology database
    df = pd.read_excel("C:/Users/pratama/Documents/GitHub/MESSAGEix/message_ix/message_ix/genie_tech/tech_data.xlsx",index_col=0)

    year_df = scenario.vintage_and_active_years()
    vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]
    
    if df.isna()[technology]['year_vtg']:
        yv = vintage_years
    else:
        yv = df[technology]['year_vtg']
    
    if df.isna()[technology]['year_act']:
        ya = act_years
    else:
        ya = df[technology]['year_act']
    
    if df.isna()['unit']['time']:
        t_unit = '-'
    else:
        t_unit = df['unit']['time']
    
    
    if technology not in set(scenario.set("technology")):
        scenario.add_set("technology", technology)
    
    if not parameter:
        df_param = df.apply(pd.to_numeric, errors='coerce')
        parameter = df_param['DACCS'].dropna().index
    
    df_in = df[technology]
            
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
            technology=technology,
            value=df_in[par],
            )
        scenario.add_par(par, par_data)
