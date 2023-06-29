#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 00:00:25 2023

@author: tavo
"""

import os 
import numpy as np
import prody as pro 
import matplotlib.pyplot as plt

import Bio.PDB as pdb
from Bio.SVDSuperimposer import SVDSuperimposer

from numpy.random import Generator, PCG64

basepath = '/media/tavo/storage/spikes/final_pdbs'
filenames = os.listdir(basepath)

filepaths = np.array([basepath + '/' + val  for val in filenames])

spikes_m = []

cont = []

for k in range(len(filepaths)):
    
    parser = pdb.PDBParser()
    structure = parser.get_structure('test',filepaths[k])
    mod = structure[0]
    chain = mod['A']
    
    spikes_m.append(chain)

rng = Generator(PCG64(seed=1983))
index_choice = rng.choice(np.arange(len(spikes_m)))

fixed = np.array([val.get_coord() for val in spikes_m[index_choice].get_atoms()])

maxfrag = 6050

normed = []

for spk in spikes_m:
    
    atomdata = np.array([val.get_coord() for val in spk.get_atoms()])
    sup = SVDSuperimposer()
    sup.set(fixed[0:maxfrag], atomdata[0:maxfrag])
    
    sup.run()
    
    rot, tran = sup.get_rotran()
    atomdata = np.dot(atomdata, rot) + tran
    
    atomdata = atomdata - atomdata.mean(axis=0)
    atomdata = (atomdata-atomdata.min())/(atomdata.max()-atomdata.min())
    
    normed.append(atomdata)

finalsize = 24*24*16
main_container = []

for atd in normed:
    
    cshape = atd.shape[0]
    toAdd = finalsize-cshape
    
    add = np.array([[0,0,0] for k in range(toAdd)])
    new = np.vstack((atd,add))
    new = new.reshape((24,24,16,3))
    main_container.append(new)
    
main_container = np.stack(main_container)
np.save('/media/tavo/storage/spikes/reshaped',main_container)
