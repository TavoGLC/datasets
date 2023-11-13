#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 20:00:45 2023

@author: tavo
"""

import os
import numpy as np
import pandas as pd

def ReadFile(path):    
    with open(path) as f:
        lines = f.readlines()
    return lines

path = '/media/tavo/storage/flares'
files = os.listdir(path)

paths = [os.path.join(path, val) for val in files]

cont = []
months = ['01','02','03','04','05','06','07','08','09','10','11','12']
months31 = ['01','03','05','07','08','10','12']

for pth in paths:
    
    fl = ReadFile(pth)
    year = pth[-8:-4]
    
    strt = [k for k,val in enumerate(fl) if val.find('Day')==0][0]
    end = [k for k,val in enumerate(fl) if val.find('Mean')==0][0]
    
    selectedlines = fl[strt+2:end-1]
    selectedlines = [val.split() for val in selectedlines]
    
    for vl in selectedlines[0:-1]:
        for sal,xal in zip(vl[1::],months):
            cont.append([vl[0]+'/'+xal+'/'+year,sal.replace(',','.')])
    
    for sal,xal in zip(selectedlines[-1][1::],months31):
        cont.append(['31'+'/'+xal+'/'+year,sal.replace(',','.')])
        

data = np.array(cont)
df = pd.DataFrame()

df['dt'] = data[:,0]
df['date'] = pd.to_datetime(df['dt'],format='%d/%m/%Y',errors='coerce')
df['sfindex'] = data[:,1].astype(np.float16)

df = df.dropna(subset=['date'])

df = df[['date','sfindex']]

df.to_csv('/media/tavo/storage/flaresdata.csv',index=False)

