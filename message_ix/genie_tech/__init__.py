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
    
#    if df[technology]['year_vtg'] is None:
    yv = vintage_years
#    else:
#        yv = df[technology]['year_vtg']
#    
#    if df[technology]['year_act'] is None:
    ya = act_years
#    else:
#       ya = df[technology]['year_act']
#        
#    
    if technology not in set(scenario.set("technology")):
        scenario.add_set("technology", technology)
            
    for par in parameter:
        par_data = make_df(
            par,
            node_loc=df[technology]['node_loc'],
            year_vtg=yv,
            year_act=ya,
            time=df[technology]['time'],
            unit="-",
            technology=technology,
            value=df[technology][par],
        )
        scenario.add_par(par, par_data)
