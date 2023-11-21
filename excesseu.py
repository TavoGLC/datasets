#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 00:02:51 2023

@author: tavo
"""

import numpy as np
import pandas as pd

###############################################################################
# Loading packages 
###############################################################################

def GetDayLenght(J,lat):
    #CERES model  Ecological Modelling 80 (1995) 87-95
    phi = 0.4093*np.sin(0.0172*(J-82.2))
    coef = (-np.sin(np.pi*lat/180)*np.sin(phi)-0.1047)/(np.cos(np.pi*lat/180)*np.cos(phi))
    ha =7.639*np.arccos(np.max([-0.87,coef]))
    return ha

def LengthDifferentce(J,lat):
    return GetDayLenght(J,lat)-GetDayLenght(J+1,lat)

###############################################################################
# Loading packages 
###############################################################################

dta = pd.read_csv('/media/tavo/storage/excess/Sin título 2.csv')
dta['date'] = dta['TIME']
dta = dta.set_index('date')

cols = ['European Union - 27 countries (from 2020)', 'Belgium',
       'Bulgaria', 'Czechia', 'Denmark', 'Germany', 'Estonia', 'Ireland',
       'Greece', 'Spain', 'France', 'Croatia', 'Italy', 'Cyprus', 'Latvia',
       'Lithuania', 'Luxembourg', 'Hungary', 'Malta', 'Netherlands', 'Austria',
       'Poland', 'Portugal', 'Romania', 'Slovenia', 'Slovakia', 'Finland',
       'Sweden', 'Iceland', 'Liechtenstein', 'Norway', 'Switzerland']

ecities = pd.read_csv('/media/tavo/storage/excess/ecities.csv')
ecities = ecities.set_index('name')

cont = []
for cl in cols:
    minidta = dta[cl].copy().to_frame().reset_index()
    minidta = minidta.rename(columns={cl: 'excess_deaths'}) 
    minidta['country'] = [cl for _ in range(minidta.shape[0])]
    minidta['lat'] = ecities['lat'].loc[minidta['country']].values
    minidta['long'] = ecities['long'].loc[minidta['country']].values
    dl = []
    gdl = []
    for k in range(len(minidta)-1):
        drange = pd.date_range(minidta['date'].iloc[k],minidta['date'].iloc[k+1])
        dlm = np.mean([GetDayLenght(val, minidta['lat'].mean()) for val in drange.dayofyear])
        gdlm = np.mean([LengthDifferentce(val, minidta['lat'].mean()) for val in drange.dayofyear])
        dl.append(dlm)
        gdl.append(gdlm)
    drange = pd.date_range(minidta['date'].iloc[-1],'2023-10')
    dl.append(np.mean([GetDayLenght(val, minidta['lat'].mean()) for val in drange.dayofyear]))
    gdl.append(np.mean([LengthDifferentce(val, minidta['lat'].mean()) for val in drange.dayofyear]))
    
    minidta['daylength'] = dl
    minidta['gdaylength'] = gdl

    cont.append(minidta)

data = pd.concat(cont)

data.to_csv('/media/tavo/storage/excess/eudata.csv')

###############################################################################
# Loading packages 
###############################################################################

'''
import time
import numpy as np
import pandas as pd

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


cols = ['European Union - 27 countries (from 2020)', 'Belgium',
       'Bulgaria', 'Czechia', 'Denmark', 'Germany', 'Estonia', 'Ireland',
       'Greece', 'Spain', 'France', 'Croatia', 'Italy', 'Cyprus', 'Latvia',
       'Lithuania', 'Luxembourg', 'Hungary', 'Malta', 'Netherlands', 'Austria',
       'Poland', 'Portugal', 'Romania', 'Slovenia', 'Slovakia', 'Finland',
       'Sweden', 'Iceland', 'Liechtenstein', 'Norway', 'Switzerland']

geolocator = Nominatim(user_agent="whocities")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=4)

container = []
for val in cols:    
    location = geocode(val)
    try:
        container.append([val, location.latitude,location.longitude])
    except AttributeError:
        container.append([val, 0,0])
    time.sleep(2)

container = np.array(container)

locations = pd.DataFrame()
locations['name'] = container[:,0]
locations['lat'] = container[:,1]
locations['long'] = container[:,2]

locations.to_csv('/media/tavo/storage/excess/ecities.csv')
'''
