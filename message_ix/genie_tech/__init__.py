# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 15:41:32 2023

@author: pratama
"""

import pandas as pd
import ixmp
import message_ix

# A utility for copying all parameters from one scenario to another
def add_tech( # base and scenario should be excluded, at the moment we can just read from MESSAGE initialization
    #base,
    #scenario=None,
    technology=None,
    parameter=None,
    node="all",
    ):
    """
    Parameters
    ----------
    sc_ref : message_ix.Scenario()
        MESSAGEix Scenario for copying data from.
    sc : message_ix.Scenario()
        MESSAGEix Scenario for copying the data to.
    tec_ref : string
        reference technology for copying parameters from.
    tec : string or None, optional
        technology for copying parameters to. if None: the same as tec_ref.
    node_ref : string
        reference node for copying parameters from.
    node : string
        node for copying parameters to.
    par_list : list, optional
        list of parameters to be copied. The default is 'all'.
    par_exclude : list, optional
        list of parameters to be excluded from being copied. The default is [].
    remove_old : bool, optional
        removing old data before copying new data. The default is True.
    """

    # Reading new technology database
    df = pd.read_excel("tech_data.xlsx",index_col=0)


    #if not scenario:
    #    scenario = base
    #scenario.check_out()
    
    if technology not in set(scenario.set("technology")):
        scenario.add_set("technology", technology)
   
