import numpy as np
import pandas as pd

with open('/home/tavo/Documentos/tsis_ssi_L3_c24h_v09_20180314_20230129.txt') as f:
    lines = f.readlines()
    
datalines = lines[91::]    

datasplited = [val.split() for val in datalines]
datasplited = np.array(datasplited)

dataFrame = pd.DataFrame()


dataFrame['date'] = [val[0:-3] for val in datasplited[:,0]]
dataFrame['date'] = pd.to_datetime(dataFrame['date'])

dataFrame['wavelength'] = datasplited[:,2].astype(np.float32)
dataFrame['instrument_mode_id'] = datasplited[:,3].astype(np.int16)
dataFrame['data_version'] = datasplited[:,4].astype(np.int16)
dataFrame['irradiance'] = datasplited[:,5].astype(np.float64)
dataFrame['instrument_uncertainty'] = datasplited[:,6].astype(np.float64)
dataFrame['measurement_precision'] = datasplited[:,7].astype(np.float64)
dataFrame['measurement_stability'] = datasplited[:,8].astype(np.float64)
dataFrame['quality'] = datasplited[:,9].astype(np.float64)

wavelengths = dataFrame['wavelength'].unique()
wbins = [wavelengths[0],wavelengths[485],wavelengths[680],wavelengths[710],wavelengths[820],wavelengths[950],wavelengths[1049],wavelengths[1172],wavelengths[-1]]

dataFrame.to_csv('/home/tavo/Documentos/solarcurrent.csv',index=False)
