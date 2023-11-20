#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 01:46:04 2023

@author: tavo
"""
import numpy as np
import pandas as pd

###############################################################################
# Loading packages 
###############################################################################

class7 = pd.read_csv('/media/tavo/storage/mortalitywho/diagnosis.csv')
class7 = class7.set_index('Code')

###############################################################################
# Loading packages 
###############################################################################

d0 = pd.read_csv('/media/tavo/storage/mortalitywho/mortality/MortIcd7.csv')

d0['cause_desc'] = [class7['LongDescription'].loc[val] if val in class7.index else np.nan for val in d0['Cause']]
d0['cause_cat'] = [class7['ShortDescription'].loc[val] if val in class7.index else np.nan for val in d0['Cause']]

d1 = pd.read_csv('/media/tavo/storage/mortalitywho/mortality/Morticd8')
d1['cause_desc'] = [class7['LongDescription'].loc[val] if val in class7.index else np.nan for val in d1['Cause']]
d1['cause_cat'] = [class7['ShortDescription'].loc[val] if val in class7.index else np.nan for val in d1['Cause']]

d2 = pd.read_csv('/media/tavo/storage/mortalitywho/mortality/Morticd9')
d2['cause_desc'] = [class7['LongDescription'].loc[val] if val in class7.index else np.nan for val in d2['Cause']]
d2['cause_cat'] = [class7['ShortDescription'].loc[val] if val in class7.index else np.nan for val in d2['Cause']]

d3 = pd.read_csv('/media/tavo/storage/mortalitywho/mortality/Morticd10_part1')
d3['cause_desc'] = [class7['LongDescription'].loc[val] if val in class7.index else np.nan for val in d3['Cause']]
d3['cause_cat'] = [class7['ShortDescription'].loc[val] if val in class7.index else np.nan for val in d3['Cause']]

d4 = pd.read_csv('/media/tavo/storage/mortalitywho/mortality/Morticd10_part2')
d4['cause_desc'] = [class7['LongDescription'].loc[val] if val in class7.index else np.nan for val in d4['Cause']]
d4['cause_cat'] = [class7['ShortDescription'].loc[val] if val in class7.index else np.nan for val in d4['Cause']]

d5 = pd.read_csv('/media/tavo/storage/mortalitywho/mortality/Morticd10_part3')
d5['cause_desc'] = [class7['LongDescription'].loc[val] if val in class7.index else np.nan for val in d5['Cause']]
d5['cause_cat'] = [class7['ShortDescription'].loc[val] if val in class7.index else np.nan for val in d5['Cause']]

d6 = pd.read_csv('/media/tavo/storage/mortalitywho/mortality/Morticd10_part4')
d6['cause_desc'] = [class7['LongDescription'].loc[val] if val in class7.index else np.nan for val in d6['Cause']]
d6['cause_cat'] = [class7['ShortDescription'].loc[val] if val in class7.index else np.nan for val in d6['Cause']]

d7 = pd.read_csv('/media/tavo/storage/mortalitywho/mortality/Morticd10_part5')
d7['cause_desc'] = [class7['LongDescription'].loc[val] if val in class7.index else np.nan for val in d7['Cause']]
d7['cause_cat'] = [class7['ShortDescription'].loc[val] if val in class7.index else np.nan for val in d7['Cause']]

dframes = [d0,d1,d2,d3,d4,d5,d6,d7]

data = pd.concat(dframes)

cnames = pd.read_csv('/media/tavo/storage/mortalitywho/mort_country_codes/country_codes')
cnames = cnames.set_index('country')

data['country_name'] = cnames['name'].loc[data['Country']].values

###############################################################################
# Loading packages 
###############################################################################

population = pd.read_csv('/media/tavo/storage/mortalitywho/mort_pop/pop')
population2 = pd.DataFrame(columns=population.columns, data=[[np.nan for val in population.columns]])

population = pd.concat([population,population2],axis=0)
population = population.set_index(['Country','Year','Sex'])

population = population[~population.index.duplicated(keep='first')]

dtuples = [tuple(val) for val in zip(data['Country'],data['Year'],data['Sex'])]

tcont = []
for val in dtuples:
    if val in population.index:
        tcont.append(val)
    else:
        tcont.append((np.nan,np.nan,np.nan))
    
###############################################################################
# Loading packages 
###############################################################################

popcols = ['Pop1', 'Pop2', 'Pop3', 'Pop4','Pop5', 'Pop6', 'Pop7', 'Pop8',
           'Pop9', 'Pop10', 'Pop11', 'Pop12','Pop13', 'Pop14', 'Pop15', 
           'Pop16', 'Pop17', 'Pop18', 'Pop19', 'Pop20','Pop21', 'Pop22', 
           'Pop23', 'Pop24', 'Pop25', 'Pop26', 'Lb']

for kal in popcols:    
    data[kal] = population[kal].loc[tcont].values

###############################################################################
# Loading packages 
###############################################################################

locationsc = pd.read_csv('/media/tavo/storage/mortalitywho/cities.csv')
locationsc = locationsc.set_index('name')

data['lat'] = locationsc['lat'].loc[data['country_name']].values
data['long'] = locationsc['long'].loc[data['country_name']].values

data.to_csv('/media/tavo/storage/mortalitywho/whodata.csv',index=False)

###############################################################################
# Loading packages 
###############################################################################
'''
geolocation was done with the following code
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

unlocs = data['country_name'].unique()

geolocator = Nominatim(user_agent="whocities")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=4)

container = []
for val in unlocs:    
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

locations.to_csv('/media/tavo/storage/mortalitywho/cities.csv')
'''
