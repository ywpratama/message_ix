#!/usr/bin/env python
# coding: utf-8

# In[1]:


import yaml
import pandas as pd
from message_ix.utils import make_df
from collections.abc import Mapping


# In[2]:


with open('learning_data.yaml','r') as stream:
    learning_data = yaml.safe_load(stream)


# In[3]:


par_list = ['learning_par','eos_par','nbr_unit_ref','u_ref','u']

data = {par: [] for par in par_list}


# In[4]:


for tech, par_dict in learning_data.items():
    for par, par_data in par_dict.items():
        if not isinstance(par_data, Mapping):
            par_data = {'value': par_data, 'unit': '-'}
        if par != 'u':
            data[par].append(
                make_df(
                    par,
                    technology=tech,
                    value=par_data['value'],
                    unit=par_data['unit'],
                )
            )
        else:
            for size, value in par_data['sizes'].items():
                data[par].append(
                    make_df(
                        par,
                        technology=tech,
                        value=value,
                        unit=par_data['unit'],
                        size=size,
                    )
                )


# In[5]:


data = {k: pd.concat(v) for k, v in data.items()}


# In[7]:


with pd.ExcelWriter('learning_data.xlsx', engine='xlsxwriter', mode='w') as writer:
    for sheet_name, sheet_data in data.items():
        sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)


# In[ ]:




