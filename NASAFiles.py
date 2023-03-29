#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 17:49:31 2023

@author: tavo
"""

import time 
import requests

# Set the URL string to point to a specific data URL. Some generic examples are:
#   https://servername/data/path/file
#   https://servername/opendap/path/file[.format[?subset]]
#   https://servername/daac-bin/OTF/HTTP_services.cgi?KEYWORD=value[&KEYWORD=value]

urls_file = '/media/tavo/storage/urls.txt'

with open(urls_file) as f:
    urls = f.readlines()


for ur in urls:
    time.sleep(2)
    URL = ur
    # Set the FILENAME string to the data file name, the LABEL keyword value, or any customized name. 
    FILENAME ='/media/tavo/storage/dta/' + URL[82:100] + '.hdf.nc4'
          
    result = requests.get(URL)
    try:
        result.raise_for_status()
        f = open(FILENAME,'wb')
        f.write(result.content)
        f.close()
        print('contents of URL written to '+FILENAME)
    except:
        print('requests.get() returned an error code '+str(result.status_code))
