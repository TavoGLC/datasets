#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 00:39:05 2023

@author: tavo
"""

import numpy as np
import pandas as pd
import multiprocessing as mp

###############################################################################

data = pd.read_csv('/media/tavo/storage/sunspots/SN_d_tot_V2.0.csv',delimiter=';',header=None)

newData = pd.DataFrame()

newData['date'] = pd.to_datetime(data[0].astype(str)+'/'+data[1].astype(str)+'/'+data[2].astype(str),format='%Y/%m/%d')
newData['year'] = data[0]
newData['dayofyear'] = newData['date'].dt.dayofyear
newData['dayofweek'] = newData['date'].dt.dayofweek
newData['week'] = newData['date'].dt.isocalendar().week
newData['dailysunspots'] = data[4]
newData['standarddeviation'] = data[5]
newData['observations'] = data[6]
newData['provisional'] = data[7]

newData.to_csv('/media/tavo/storage/sunspots/sunspots.csv')
