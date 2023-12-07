#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 11:50:21 2023

@author: tavo
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy import interpolate

###############################################################################
# Loading packages 
###############################################################################

def GetDayLenght(J,lat):
    #CERES model  Ecological Modelling 80 (1995) 87-95
    phi = 0.4093*np.sin(0.0172*(J-82.2))
    coef = (-np.sin(np.pi*lat/180)*np.sin(phi)-0.1047)/(np.cos(np.pi*lat/180)*np.cos(phi))
    ha =7.639*np.arccos(np.max([-0.87,coef]))
    return ha

def DayLengthGradient(J,lat):
    if J in [365,366]:
        return GetDayLenght(J,lat) - GetDayLenght(0,lat)
    else:
        return GetDayLenght(J,lat) - GetDayLenght(J+1,lat)

def SolarFluxCoefs(J,lat):
    
    I0 = 1367
    fact = np.pi/180
    
    delta = 23.45*np.sin(0.986*(J+284))
    a = np.sin(lat*fact)*np.sin(delta*fact)
    b0 = np.cos(lat*fact)*np.cos(delta*fact)
    Ct = 1+0.034*np.cos((J-2)*fact)
    Gamma = 0.796-0.01*np.sin((0.986*(J+284))*fact)
    
    return [a,b0,Ct*I0*Gamma,120*Gamma]

def SolarFlux(T,coefs):
    #New model to estimate and evaluate the solar radiation
    #Y.El Mghouchi A.El BouardiZ.ChoulliT.Ajzoul
    #ETEE, Faculty of Sciences, Abdelmalek Essaadi University, Tetouan, Morocco
    
    fact = np.pi/180
    w = 15*(12-T)
    
    a,b0,A0,A1 = coefs
    
    b = b0*np.cos(w*fact)
    h = np.arcsin((a+b))
    sinh = np.sin(h)
    
    I = A0*sinh*np.e**(-0.13/sinh)
    coeff = 0.4511+sinh
    Dh = A1*np.e**(coeff)
    
    return I+Dh

def GetFluxByDay(J,lat):
    
    if lat>65:
        localLat = 65
    else:
        localLat = lat
    
    coefs = SolarFluxCoefs(J,localLat)
    
    def LocalFlux(T):
        return SolarFlux(T,coefs)
    
    vflux = np.vectorize(LocalFlux)
    flux = vflux(np.linspace(0,24,num=500))
    flux[flux<0] = 0
    
    return np.linspace(0,24,num=500),flux

def MakeInterpolatingFunction(J,lat):    
    x,y = GetFluxByDay(J, lat)
    f = interpolate.interp1d(x, y)
    return f

###############################################################################
# Loading packages 
###############################################################################

locationsdata = pd.read_csv('/media/tavo/storage/deathsmx/AGEEML_20231130145158.csv')
minidata = locationsdata.groupby(['CVE_ENT','CVE_MUN'])[['LAT_DECIMAL','LON_DECIMAL','ALTITUD']].mean().reset_index()

dtacont = []
for j in range(1,367):
    localdata = minidata.copy()
    
    localdl = lambda x : GetDayLenght(j,x)
    localgdl = lambda x : DayLengthGradient(j,x)
    localflux = lambda x : MakeInterpolatingFunction(j,x)
    
    localdata['dayofyear'] = [j for _ in range(localdata.shape[0])]
    localdata['daylength'] = localdata['LAT_DECIMAL'].apply(localdl)
    localdata['gdaylength'] = localdata['LAT_DECIMAL'].apply(localgdl)
    localdata['flux'] = localdata['LAT_DECIMAL'].apply(localflux)
    
    dtacont.append(localdata)

dtacont = pd.concat(dtacont)
dtacont = dtacont.set_index(['CVE_ENT', 'CVE_MUN','dayofyear'])

###############################################################################
# Loading packages 
###############################################################################

def FormatIndex(Index):
    cin  = str(Index).strip()
    if len(cin)==1:
        out = '00'+str(cin)
    elif len(cin)==2:
        out = '0'+str(cin)
    else:
        out = str(cin)
    return out

def FormatHour(hour):
    if hour>24:
        return hour-np.floor(hour)
    else:
        return hour

def IsNight(val):
    if val<10:
        return True
    else:
        return False

def RemoveMissing(df):
    
    df = df[df['dia_ocurr']!=99]
    df = df[df['mes_ocurr']!=99]
    df = df[df['anio_ocur']!=9999]
    
    df = df[df['dia_nacim']!=99]
    df = df[df['mes_nacim']!=99]
    df = df[df['anio_nacim']!=9999]
    
    df = df[df['horas']!=99]
    df = df[df['minutos']!=99]
    
    df = df[df['ent_resid']!=99]
    df = df[df['mun_resid']!=999]
    
    df = df[df['sexo']!=9]
    
    return df
    
def ProcessDates(df):
    
    df['decease_date'] = pd.to_datetime([str(val)+'-'+str(sal)+'-'+str(jal) for val,sal,jal in zip(df['mes_ocurr'],df['dia_ocurr'],df['anio_ocur'])],errors='coerce')
    df['birth_date'] = pd.to_datetime([str(val)+'-'+str(sal)+'-'+str(jal) for val,sal,jal in zip(df['mes_nacim'],df['dia_nacim'],df['anio_nacim'])],errors='coerce')
    df['tod'] = df['horas']+df['minutos']/60
    
    df = df.dropna(subset=['decease_date'])
    df = df.dropna(subset=['birth_date'])
    
    return df

def ProcessDescriptions(df,dta=None):
    df['gr_lismex'] = df['gr_lismex'].apply(FormatIndex)
    df['desc'] = dta['desc'].loc[df['gr_lismex']].values
    return df

def ProcessSolar(df,data=dtacont):
    
    df['dayofyear'] = df['decease_date'].dt.dayofyear
    dtatuple = [tuple(val) for val in df[['ent_resid','mun_resid','dayofyear']].to_records(index=False)]
    df['daylength'] = data['daylength'].loc[dtatuple].values
    df['gdaylength'] = data['gdaylength'].loc[dtatuple].values
    df['fluxF'] = data['flux'].loc[dtatuple].values
    df['flux'] = [val(sal) for val,sal in zip(df['fluxF'],df['tod'])]
    df['gflux'] = [val(sal) - val(FormatHour(sal+1)) for val,sal in zip(df['fluxF'],df['tod'])]
    
    df['lat'] = data['LAT_DECIMAL'].loc[dtatuple].values
    df['long'] = data['LON_DECIMAL'].loc[dtatuple].values
    
    df['flux'] = df['flux'].astype(np.float32)
    df['gflux'] = df['gflux'].astype(np.float32)
    df['night'] = df['flux'].apply(IsNight)
    
    return df

def ProcessData(df,dtac=None):
    
    df = RemoveMissing(df)
    df = ProcessDates(df)
    df = ProcessSolar(df)
    df = ProcessDescriptions(df,dta=dtac)
    
    return df

###############################################################################
# Loading packages 
###############################################################################

def ProcessListDB(df):
    
    colnames = df.columns
    
    df['CVE'] = df[colnames[0]].apply(FormatIndex)
    df['desc'] = df[colnames[1]]
    df = df.set_index('CVE')
    
    return df

dtalist = []
dtalist.append('/media/tavo/storage/deathsmx/general/defunciones_base_datos_2012_csv/catalogos/degpolisme.csv')
dtalist.append('/media/tavo/storage/deathsmx/general/defunciones_base_datos_2013_csv/catalogos/degpolisme.csv')
dtalist.append('/media/tavo/storage/deathsmx/general/defunciones_base_datos_2014_csv/catalogos/degpolisme.csv')
dtalist.append('/media/tavo/storage/deathsmx/general/defunciones_base_datos_2015_csv/catalogos/degpolisme.csv')
dtalist.append('/media/tavo/storage/deathsmx/general/defunciones_base_datos_2016_csv/catalogos/degpolisme.csv')
dtalist.append('/media/tavo/storage/deathsmx/general/conjunto_de_datos_defunciones_generales_2017_csv/catalogos/degpolisme.csv')
dtalist.append('/media/tavo/storage/deathsmx/general/conjunto_de_datos_defunciones_registradas_2018_csv/catalogos/grupo_lista_mexicana.csv')
dtalist.append('/media/tavo/storage/deathsmx/general/conjunto_de_datos_defunciones_registradas_2019_csv/catalogos/grupo_lista_mexicana.csv')
dtalist.append('/media/tavo/storage/deathsmx/general/conjunto_de_datos_defunciones_registradas_2020_csv/catalogos/grupo_lista_mexicana.csv')
dtalist.append('/media/tavo/storage/deathsmx/general/conjunto_de_datos_defunciones_registradas_2021_csv/catalogos/grupo_lista_mexicana.csv')
dtalist.append('/media/tavo/storage/deathsmx/general/conjunto_de_datos_defunciones_registradas_2022_csv/catalogos/grupo_lista_mexicana.csv')

###############################################################################
# Loading packages 
###############################################################################

paths = []
paths.append('/media/tavo/storage/deathsmx/general/defunciones_base_datos_2012_csv/conjunto_de_datos/defunciones_generales_2012.csv')
paths.append('/media/tavo/storage/deathsmx/general/defunciones_base_datos_2013_csv/conjunto_de_datos/defunciones_generales_2013.csv')
paths.append('/media/tavo/storage/deathsmx/general/defunciones_base_datos_2014_csv/conjunto_de_datos/defunciones_generales_2014.csv')
paths.append('/media/tavo/storage/deathsmx/general/defunciones_base_datos_2015_csv/conjunto_de_datos/defunciones_generales_2015.csv')
paths.append('/media/tavo/storage/deathsmx/general/defunciones_base_datos_2016_csv/conjunto_de_datos/defunciones_generales_2016.csv')
paths.append('/media/tavo/storage/deathsmx/general/conjunto_de_datos_defunciones_generales_2017_csv/conjunto_de_datos/conjunto_de_datos_defunciones_generales_2017.CSV')
paths.append('/media/tavo/storage/deathsmx/general/conjunto_de_datos_defunciones_registradas_2018_csv/conjunto_de_datos/conjunto_de_datos_defunciones_registradas_2018.csv')
paths.append('/media/tavo/storage/deathsmx/general/conjunto_de_datos_defunciones_registradas_2019_csv/conjunto_de_datos/conjunto_de_datos_defunciones_registradas_2019.CSV')
paths.append('/media/tavo/storage/deathsmx/general/conjunto_de_datos_defunciones_registradas_2020_csv/conjunto_de_datos/conjunto_de_datos_defunciones_registrados_2020.csv')
paths.append('/media/tavo/storage/deathsmx/general/conjunto_de_datos_defunciones_registradas_2021_csv/conjunto_de_datos/conjunto_de_datos_defunciones_registradas_2021.csv')
paths.append('/media/tavo/storage/deathsmx/general/conjunto_de_datos_defunciones_registradas_2022_csv/conjunto_de_datos/conjunto_de_datos_defunciones_registradas_2022.CSV')

datacont = []
for pth,lst in zip(paths,dtalist):
    
    localdta = pd.read_csv(pth,encoding='latin-1')
    
    listmx = pd.read_csv(lst,encoding='latin1')
    listmx = ProcessListDB(listmx)
    
    newdata = ProcessData(localdta,dtac=listmx)
    datacont.append(newdata)
    
datacont = pd.concat(datacont)

###############################################################################
# Loading packages 
###############################################################################

term= ['Enfermedades isquÃ©micas del corazÃ³n',
       'Enfermedades cerebrovasculares',
       'Otras enfermedades del aparato respiratorio',
       'Tumor maligno de Ã³rganos respiratorios e intratorÃ¡cicos',
       'Tumores malignos de los Ã³rganos genitourinarios',
       'Enfermedades de otras partes del aparato digestivo',
       'Tumores malignos de los Ã³rganos digestivos',
       'Malformaciones congÃ©nitas, deformidades y anomalÃ\xadas cromosÃ³micas',
       'Enfermedades endocrinas y metabÃ³licas',
       'Ciertas afecciones originadas en el periodo perinatal',
       'Enfermedades del sistema nervioso',
       'Tumores malignos de otros sitios y de los no especificados',
       'SÃ\xadntomas, signos y hallazgos anormales clÃ\xadnicos y de laboratorio, no clasificados en otra parte',
       'Enfermedades hipertensivas',
       'Enfermedades de la sangre y de los Ã³rganos hematopoyÃ©ticos, y ciertos trastornos que afectan el mecanismo de la inmunidad',
       'Otros accidentes, incluso los efectos tardÃ\xados',
       'Enfermedades de la circulaciÃ³n pulmonar y otras enfermedades del corazÃ³n',
       'Otras enfermedades bacterianas', 'Enfermedades vÃ\xadricas',
       'Enfermedades infecciosas intestinales',
       'Tumores malignos de los huesos, de los cartÃ\xadlagos articulares, del tejido conjuntivo, de la piel y de la mama',
       'DesnutriciÃ³n y otras deficiencias nutricionales',
       'Enfermedades del aparato urinario',
       'Enfermedades de la piel y del tejido  subcutÃ¡neo',
       'Tumores malignos del tejido linfÃ¡tico, de los Ã³rganos hematopoyÃ©ticos y tejidos afines',
       'Fiebre reumÃ¡tica aguda y enfermedades cardiacas reumÃ¡ticas crÃ³nicas',
       'Enfermedades del sistema osteomuscular y del tejido conjuntivo',
       'Tumores malignos del labio, de la cavidad bucal y de la faringe',
       'Trastornos mentales y del comportamiento',
       'Tumores de comportamiento incierto o desconocido',
       'Otras enfermedades del aparato circulatorio',
       'Tumores malignos (primarios) de sitios mÃºltiples independientes',
       'Causas obstÃ©tricas indirectas', 'Tumores benignos',
       'Tuberculosis', 'Enfermedades del ojo y sus anexos',
       'Causas obstÃ©tricas directas',
       'Enfermedades de la cavidad bucal, de las glÃ¡ndulas salivales y de los maxilares',
       'Trastornos de la mama',
       'Otras enfermedades infecciosas y parasitarias y efectos tardÃ\xados de las enfermedades infecciosas y parasitarias',
       'Enfermedades de los Ã³rganos genitales masculinos',
       'Infecciones y otras enfermedades de las vÃ\xadas respiratorias superiores',
       'Secuelas de lesiones autoinfligidas, agresiones y eventos de intenciÃ³n no determinada, de atenciÃ³n medica y quirÃºrgica y de',
       'Accidentes de transporte', 'CaÃ\xaddas',
       'Lesiones autoinfligidas intencionalmente', 'Agresiones',
       'Otra violencia',
       'Contratiempos durante la atenciÃ³n medica, reacciones anormales y complicaciones ulteriores',
       'Envenenamiento accidental por, y exposiciÃ³n a sustancias nocivas',
       'ExposiciÃ³n al humo, fuego y llamas',
       'Infecciones con modo de transmisiÃ³n predominantemente sexual',
       'Rickettsiosis y otras enfermedades debidas a protozoarios',
       'Enfermedades del oÃ\xaddo y de la apÃ³fisis mastoides',
       'Drogas, medicamentos y sustancias biolÃ³gicas causantes de efectos adversos en su uso terapÃ©utico',
       'Enfermedades de los Ã³rganos genitales femeninos',
       'Enfermedades endocrinas y metabólicas',
       'Otros accidentes, incluso los efectos tardíos',
       'Enfermedades isquémicas del corazón',
       'Tumores malignos de los órganos digestivos',
       'Tumores malignos de los órganos genitourinarios',
       'Enfermedades de la circulación pulmonar y otras enfermedades del corazón',
       'Tumores malignos de los huesos, de los cartílagos articulares, del tejido conjuntivo, de la piel y de la mama',
       'Enfermedades víricas',
       'Tumores malignos del tejido linfático, de los órganos hematopoyéticos y tejidos afines',
       'Fiebre reumática aguda y enfermedades cardiacas reumáticas crónicas',
       'Desnutrición y otras deficiencias nutricionales',
       'Malformaciones congénitas, deformidades y anomalías cromosómicas',
       'Enfermedades de la sangre y de los órganos hematopoyéticos, y ciertos trastornos que afectan el mecanismo de la inmunidad',
       'Tumor maligno de órganos respiratorios e intratorácicos',
       'Enfermedades de los órganos genitales masculinos', 'Caídas',
       'Síntomas, signos y hallazgos anormales clínicos y de laboratorio, no clasificados en otra parte',
       'Enfermedades del oído y de la apófisis mastoides',
       'Enfermedades de la piel y del tejido  subcutáneo',
       'Enfermedades de los órganos genitales femeninos',
       'Contratiempos durante la atención medica, reacciones anormales y complicaciones ulteriores',
       'Otras enfermedades infecciosas y parasitarias y efectos tardíos de las enfermedades infecciosas y parasitarias',
       'Causas obstétricas directas',
       'Infecciones y otras enfermedades de las vías respiratorias superiores',
       'Causas obstétricas indirectas',
       'Exposición al humo, fuego y llamas',
       'Envenenamiento accidental por, y exposición a sustancias nocivas',
       'Infecciones con modo de transmisión predominantemente sexual',
       'Enfermedades de la cavidad bucal, de las glándulas salivales y de los maxilares',
       'Drogas, medicamentos y sustancias biológicas causantes de efectos adversos en su uso terapéutico',
       'Secuelas de lesiones autoinfligidas, agresiones y eventos de intención no determinada, de atención medica y quirúrgica y de',
       'Tumores in situ']

corr= ['Enfermedades isquémicas del corazón',
       'Enfermedades cerebrovasculares',
       'Otras enfermedades del aparato respiratorio',
       'Tumor maligno de órganos respiratorios e intratorácicos',
       'Tumores malignos de los Ã³rganos genitourinarios',
       'Enfermedades de otras partes del aparato digestivo',
       'Tumores malignos de los órganos genitourinarios',
       'Malformaciones congénitas, deformidades y anomalías cromosómicas',
       'Enfermedades endocrinas y metabólicas',
       'Ciertas afecciones originadas en el periodo perinatal',
       'Enfermedades del sistema nervioso',
       'Tumores malignos de otros sitios y de los no especificados',
       'Síntomas, signos y hallazgos anormales clínicos y de laboratorio, no clasificados en otra parte',
       'Enfermedades hipertensivas',
       'Enfermedades de la sangre y de los órganos hematopoyéticos, y ciertos trastornos que afectan el mecanismo de la inmunidad',
       'Otros accidentes, incluso los efectos tardíos',
       'Enfermedades de la circulación pulmonar y otras enfermedades del corazón',
       'Otras enfermedades bacterianas', 'Enfermedades víricas',
       'Enfermedades infecciosas intestinales',
       'Tumores malignos de los huesos, de los cartílagos articulares, del tejido conjuntivo, de la piel y de la mama',
       'Desnutrición y otras deficiencias nutricionales',
       'Enfermedades del aparato urinario',
       'Enfermedades de la piel y del tejido  subcutáneo',
       'Tumores malignos del tejido linfático, de los órganos hematopoyéticos y tejidos afines',
       'Fiebre reumática aguda y enfermedades cardiacas reumáticas crónicas',
       'Enfermedades del sistema osteomuscular y del tejido conjuntivo',
       'Tumores malignos del labio, de la cavidad bucal y de la faringe',
       'Trastornos mentales y del comportamiento',
       'Tumores de comportamiento incierto o desconocido',
       'Otras enfermedades del aparato circulatorio',
       'Tumores malignos (primarios) de sitios multiples independientes',
       'Causas obstétricas indirectas', 'Tumores benignos',
       'Tuberculosis', 'Enfermedades del ojo y sus anexos',
       'Causas obstétricas directas',
       'Enfermedades de la cavidad bucal, de las glÃ¡ndulas salivales y de los maxilares',
       'Trastornos de la mama',
       'Otras enfermedades infecciosas y parasitarias y efectos tardíos de las enfermedades infecciosas y parasitarias',
       'Enfermedades de los órganos genitales masculinos',
       'Infecciones y otras enfermedades de las vías respiratorias superiores',
       'Secuelas de lesiones autoinfligidas, agresiones y eventos de intención no determinada, de atención medica y quirúrgica y de',
       'Accidentes de transporte', 'Caídas',
       'Lesiones autoinfligidas intencionalmente', 'Agresiones',
       'Otra violencia',
       'Contratiempos durante la atención medica, reacciones anormales y complicaciones ulteriores',
       'Envenenamiento accidental por, y exposición a sustancias nocivas',
       'Exposición al humo, fuego y llamas',
       'Infecciones con modo de transmisión predominantemente sexual',
       'Rickettsiosis y otras enfermedades debidas a protozoarios',
       'Enfermedades del oído y de la apófisis mastoides',
       'Drogas, medicamentos y sustancias biológicas causantes de efectos adversos en su uso terapéutico',
       'Enfermedades de los órganos genitales femeninos',
       'Enfermedades endocrinas y metabólicas',
       'Otros accidentes, incluso los efectos tardíos',
       'Enfermedades isquémicas del corazón',
       'Tumores malignos de los órganos digestivos',
       'Tumores malignos de los órganos genitourinarios',
       'Enfermedades de la circulación pulmonar y otras enfermedades del corazón',
       'Tumores malignos de los huesos, de los cartílagos articulares, del tejido conjuntivo, de la piel y de la mama',
       'Enfermedades víricas',
       'Tumores malignos del tejido linfático, de los órganos hematopoyéticos y tejidos afines',
       'Fiebre reumática aguda y enfermedades cardiacas reumáticas crónicas',
       'Desnutrición y otras deficiencias nutricionales',
       'Malformaciones congénitas, deformidades y anomalías cromosómicas',
       'Enfermedades de la sangre y de los órganos hematopoyéticos, y ciertos trastornos que afectan el mecanismo de la inmunidad',
       'Tumor maligno de órganos respiratorios e intratorácicos',
       'Enfermedades de los órganos genitales masculinos', 'Caídas',
       'Síntomas, signos y hallazgos anormales clínicos y de laboratorio, no clasificados en otra parte',
       'Enfermedades del oído y de la apófisis mastoides',
       'Enfermedades de la piel y del tejido  subcutáneo',
       'Enfermedades de los órganos genitales femeninos',
       'Contratiempos durante la atención medica, reacciones anormales y complicaciones ulteriores',
       'Otras enfermedades infecciosas y parasitarias y efectos tardíos de las enfermedades infecciosas y parasitarias',
       'Causas obstétricas directas',
       'Infecciones y otras enfermedades de las vías respiratorias superiores',
       'Causas obstétricas indirectas',
       'Exposición al humo, fuego y llamas',
       'Envenenamiento accidental por, y exposición a sustancias nocivas',
       'Infecciones con modo de transmisión predominantemente sexual',
       'Enfermedades de la cavidad bucal, de las glándulas salivales y de los maxilares',
       'Drogas, medicamentos y sustancias biológicas causantes de efectos adversos en su uso terapéutico',
       'Secuelas de lesiones autoinfligidas, agresiones y eventos de intención no determinada, de atención medica y quirúrgica y de',
       'Tumores in situ']

toCorrect = {}

for val,sal in zip(term,corr):
    toCorrect[val] = sal
    
datacont['desc'] = [toCorrect[val] for val in datacont['desc']]

###############################################################################
# Loading packages 
###############################################################################

import datetime
import chaosmagpy as cp

model = cp.load_CHAOS_matfile('/media/tavo/storage/deathsmx/CHAOS-7.16.mat')

datelist = datacont[['anio_ocur','mes_ocurr','dia_ocurr','horas','minutos']].values
dates0 = [datetime.datetime(*list(val)) for val in datelist]
dates1 = [val+datetime.timedelta(hours=1) for val in dates0]

dates = cp.data_utils.mjd2000(dates0)
datesg = cp.data_utils.mjd2000(dates1)

coords = datacont[['lat','long']].values

Br = []
Bt = []
Bp = []
gBr = []
gBt = []
gBp = []

for val,mal,sal in zip(dates,datesg,coords):
    br, bt, bp = model.synth_values_tdep(val, 6371.2, sal[0], sal[1])
    brd, btd, bpd = model.synth_values_tdep(mal, 6371.2, sal[0], sal[1])
    Br.append(br)
    Bt.append(bt)
    Bp.append(bp)
    gBr.append(br-brd)
    gBt.append(bt-btd)
    gBp.append(bp-bpd)

datacont['Br'] = Br
datacont['Bt'] = Bt
datacont['Bp'] = Bp
datacont['gBr'] = gBr
datacont['gBt'] = gBt
datacont['gBp'] = gBp

###############################################################################
# Loading packages 
###############################################################################

columns = ['decease_date', 'birth_date', 'tod','daylength', 'gdaylength', 
           'flux', 'gflux', 'lat', 'long','night','gr_lismex','desc','sexo',
           'causa_def', 'Br', 'Bt', 'Bp', 'gBr', 'gBt', 'gBp']

datacont = datacont[columns]

datacont.to_csv('/media/tavo/storage/deathsmx/mxmortality.csv',index=False)
