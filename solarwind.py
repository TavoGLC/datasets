#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 22:45:33 2023

@author: tavo
"""

import os
import gzip
import numpy as np
import pandas as pd
from netCDF4 import Dataset
import matplotlib.pyplot as plt

from datetime import timedelta
from sklearn.ensemble import RandomForestRegressor

###############################################################################
# Loading packages 
###############################################################################

def ProcessSingleId(singledata):
    dta = np.array(singledata)
    dta[dta == -99999.0] = np.nan
    dta = np.nanmean(dta.reshape(24,60),axis=1)
    return dta

def ProcessByLabels(data,labels):
    
    container = []
    for lab in labels:
        container.append(ProcessSingleId(data.variables[lab]))
    
    return container

###############################################################################
# Loading packages 
###############################################################################

path = '/media/tavo/storage/solarwind'
files = os.listdir(path)

paths = [os.path.join(path, val) for val in files]

###############################################################################
# Loading packages 
###############################################################################

frdy = ['proton_speed','proton_density','proton_temperature']
mg = ['bt','theta_gse','phi_gse','theta_gsm','phi_gsm']
faraday = []
magn = []

for pth in paths:
    
    point = pth.find('_dscovr_') + len('_dscovr_')
    currentdate = pth[point+1:point+9]
    formateddate = currentdate[4:6]+'/'+currentdate[6:8]+'/'+currentdate[0:4]
    timerange = pd.date_range(start=pd.to_datetime(formateddate), end=pd.to_datetime(formateddate)+timedelta(days=1),freq='H')
    localdf = pd.DataFrame()
    localdf['date'] = timerange[0:-1]
    
    with gzip.open(pth) as gz:
        with Dataset('dummy', mode='r', memory=gz.read()) as nc:            
            if pth.find('oe_f1m')!=-1:
                loopdata = ProcessByLabels(nc, frdy)
                for lab,prd in zip(frdy,loopdata):
                    localdf[lab] = prd
                faraday.append(localdf)
                
            elif pth.find('oe_m1m')!=-1:
                loopdata = ProcessByLabels(nc, mg)
                for lab,prd in zip(mg,loopdata):
                    localdf[lab] = prd
                magn.append(localdf)            

###############################################################################
# Loading packages 
###############################################################################

faradaydf = pd.concat(faraday)
magdf = pd.concat(magn)

faradaydf = faradaydf.dropna()
magdf = magdf.dropna()

###############################################################################
# Loading packages 
###############################################################################

faradaydf['year'] = faradaydf['date'].dt.year
faradaydf['dayofyear'] = faradaydf['date'].dt.dayofyear
faradaydf['dayofweek'] = faradaydf['date'].dt.dayofweek
faradaydf['week'] = faradaydf['date'].dt.isocalendar().week
faradaydf['hour'] = faradaydf['date'].dt.hour
faradaydf['month'] = faradaydf['date'].dt.month
faradaydf['quarter'] = faradaydf['date'].dt.quarter
faradaydf['trimester'] = np.ceil((faradaydf['month']-1)//4)
faradaydf['semester'] = np.ceil((faradaydf['month']-1)//6)

###############################################################################
# Loading packages 
###############################################################################

feats = ['year','dayofyear','dayofweek','week','hour','month','quarter','trimester','semester']

xdata = faradaydf[feats].values
ydata = faradaydf[frdy].values

regr = RandomForestRegressor(n_estimators=500,random_state=0)
regr.fit(xdata, ydata)

###############################################################################
# Loading packages 
###############################################################################

newfar = pd.DataFrame()
newfar['date'] = pd.date_range(start=faradaydf['date'].min(), end=faradaydf['date'].max(),freq='H')

newfar['year'] = newfar['date'].dt.year
newfar['dayofyear'] = newfar['date'].dt.dayofyear
newfar['dayofweek'] = newfar['date'].dt.dayofweek
newfar['week'] = newfar['date'].dt.isocalendar().week
newfar['hour'] = newfar['date'].dt.hour
newfar['month'] = newfar['date'].dt.month
newfar['quarter'] = newfar['date'].dt.quarter
newfar['trimester'] = np.ceil((newfar['month']-1)//4)
newfar['semester'] = np.ceil((newfar['month']-1)//6)

newx = newfar[feats].values
preds = regr.predict(newx)

for k,val in enumerate(frdy):
    newfar[val] = preds[:,k]    

faradaydf = faradaydf[['date']+frdy]
newfar = newfar[['date']+frdy]

faradaydf.to_csv('/media/tavo/storage/faraday_org.csv',index=False)
newfar.to_csv('/media/tavo/storage/faraday_rec.csv',index=False)

###############################################################################
# Loading packages 
###############################################################################

magdf['year'] = magdf['date'].dt.year
magdf['dayofyear'] = magdf['date'].dt.dayofyear
magdf['dayofweek'] = magdf['date'].dt.dayofweek
magdf['week'] = magdf['date'].dt.isocalendar().week
magdf['hour'] = magdf['date'].dt.hour
magdf['month'] = magdf['date'].dt.month
magdf['quarter'] = magdf['date'].dt.quarter
magdf['trimester'] = np.ceil((magdf['month']-1)//4)
magdf['semester'] = np.ceil((magdf['month']-1)//6)

###############################################################################
# Loading packages 
###############################################################################

xdata = magdf[feats].values
ydata = magdf[mg].values

regr = RandomForestRegressor(n_estimators=500,random_state=0)
regr.fit(xdata, ydata)

###############################################################################
# Loading packages 
###############################################################################

newmag = pd.DataFrame()
newmag['date'] = pd.date_range(start=magdf['date'].min(), end=magdf['date'].max(),freq='H')

newmag['year'] = newmag['date'].dt.year
newmag['dayofyear'] = newmag['date'].dt.dayofyear
newmag['dayofweek'] = newmag['date'].dt.dayofweek
newmag['week'] = newmag['date'].dt.isocalendar().week
newmag['hour'] = newmag['date'].dt.hour
newmag['month'] = newmag['date'].dt.month
newmag['quarter'] = newmag['date'].dt.quarter
newmag['trimester'] = np.ceil((newmag['month']-1)//4)
newmag['semester'] = np.ceil((newmag['month']-1)//6)

newx = newmag[feats].values
preds = regr.predict(newx)

for k,val in enumerate(mg):
    newmag[val] = preds[:,k]   

magdf = magdf[['date']+mg]
newmag = newmag[['date']+mg]

magdf.to_csv('/media/tavo/storage/mag_org.csv',index=False)
newmag.to_csv('/media/tavo/storage/mag_rec.csv',index=False)
