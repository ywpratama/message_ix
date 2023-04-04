# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 15:36:19 2023

@author: pratama
"""

import yaml

with open('tech_data.yml','r') as stream:
    tech_data = yaml.safe_load(stream)

print(tech_data)