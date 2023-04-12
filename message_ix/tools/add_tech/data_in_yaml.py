# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 15:36:19 2023

@author: pratama
"""

import yaml
import pandas as pd
from message_ix.utils import make_df

#%%
def length(data):
    if isinstance(data, str):
        result = 1
    elif isinstance(data, list):
        result = len(data)
    return result


with open('learning_data.yaml','r') as stream:
    learning_data = yaml.safe_load(stream)

print(learning_data)

technology = list(set(list(learning_data.keys())).difference(['size','unit']))
print(technology)

par_list = ['learning_par','eos_par','nbr_unit_ref','u_ref','u']

data = {par: [] for par in par_list}


for tech in technology:
    data_in = learning_data.get(tech)
    parameter = list(data_in.keys())
    
    for par in parameter:
        if not learning_data.get('unit').get(par):
            unit = '-'
        else:
            unit = learning_data.get('unit').get(par)
        if par == 'u':
            value = list(data_in.get(par).values())
            size = list(data_in.get(par).keys())
            for v in range(len(value)):
                par_data = make_df(
                    par,
                    technology=tech,
                    value=value[v],
                    unit=unit,
                    size=size[v])
                data[par+'_data'].append(par_data)
        else:
            value = data_in.get(par)
            par_data = make_df(
                par,
                technology=tech,
                value=value,
                unit=unit)
            data[par+'_data'].append(par_data)
for e in range(len(par_list)):
    if data[par_list[e]+'_data'] != []:
        data[par_list[e]+'_data'] = pd.concat(data[par_list[e]+'_data']).reset_index(drop=True)
        
        