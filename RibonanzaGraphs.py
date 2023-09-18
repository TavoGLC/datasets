#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 20:36:12 2023

@author: tavo
"""
import numpy as np 
import pandas as pd

from numpy import linalg as LA

from itertools import product
from collections import Counter

###############################################################################
# Loading packages 
###############################################################################

Alphabet = ['A','C','G','U']

Blocks = []

maxSize = 5
for k in range(1,maxSize):    
    Blocks.append([''.join(i) for i in product(Alphabet, repeat = k)])

###############################################################################
# Loading packages 
###############################################################################

def SplitString(String,ChunkSize):
    return [String[k:k+ChunkSize] for k in range(len(String)-ChunkSize+1)]

def DictionaryLibrary(ElementsBlocks):
    
    maindict = {}
    
    for k,val in enumerate(ElementsBlocks):
        innerDict = {}
        for kk,sal in enumerate(val):
            innerDict[sal] = kk
        
        maindict[k+1] = innerDict
    
    return maindict

Dicts = DictionaryLibrary(Blocks)

def MakeAdjacencyList(ProcessedSequence,Dictionary):
    
    sfSize = len(list(Dictionary.keys())[0])
    container = []
    
    for val in ProcessedSequence:
        subfrags =  [val[k:k+sfSize] for k in range(0,len(val),sfSize)]
        inner = []
        for sb in subfrags:
            if sb in Dictionary.keys():
                inner.append(Dictionary[sb])
        container.append(inner)
        
    return container

def MakeIndexs(Shape):
    
    ndims = len(Shape)
    indexs = []
    
    for k in range(ndims-1):
        for ki in range(Shape[0]):
            if ndims>2:
                if ki<Shape[0]/2:
                    start = 0
                    end = ki
                else:
                    start = int(np.floor(Shape[0]/2))
                    end = ki
                    
                
                for kki in range(start,end):    
                    indexs.append(tuple([kki]+[ki for kj in range(ndims-1)]))
                
                indexs.append(tuple([ki for kj in range(ndims)]))
                    
                for kki in range(start,end):    
                    indexs.append(tuple([ki for kj in range(ndims-1)]+[kki]))
            else:
                indexs.append(tuple([ki for kj in range(ndims)]))
    
    return indexs

def MakeAdjacencyMatrix(ProcessedSequence,Dictionary):
    
    adjList = MakeAdjacencyList(ProcessedSequence,Dictionary)
    indexs = [tuple(val) for val in adjList]
    counts = Counter(indexs)
    
    mainShape = tuple([len(Dictionary) for k in range(len(indexs[0]))])
    currentMatrix = np.zeros(mainShape)
    D12 = np.zeros(mainShape)
    
    for ky in counts.keys():
        currentMatrix[ky] = counts[ky]
        
    currentMatrix = currentMatrix + currentMatrix.T
    
    diag = currentMatrix.sum(axis=0).ravel()
    Indexs = MakeIndexs(mainShape)
    
    for inx,val in zip(Indexs,diag):
        D12[inx] = 1/np.sqrt(2*(val+1))
        
    currentMatrix = np.matmul(D12,currentMatrix)
    currentMatrix = np.matmul(currentMatrix,D12)
    w,v = LA.eig(currentMatrix)
    norm = LA.norm(w)
    
    normed = currentMatrix/norm
    normed = (normed - normed.min())/(normed.max() - normed.min())
    
    return D12

###############################################################################
# Loading packages 
###############################################################################

data = pd.read_csv('/media/tavo/storage/kaggle/train_data.csv')
uniquedata = data.groupby('sequence_id')['sequence'].value_counts().index

outdir = '/media/tavo/storage/kaggle/graphs/4mer/train/'

for val,sal in uniquedata:    
    dta = MakeAdjacencyMatrix(SplitString(sal,4), Dicts[2])
    np.save(outdir+val,dta)

###############################################################################
# Loading packages 
###############################################################################

data = pd.read_csv('/media/tavo/storage/kaggle/test_sequences.csv')
uniquedata = data.groupby('sequence_id')['sequence'].value_counts().index

outdir = '/media/tavo/storage/kaggle/graphs/4mer/test/'

for val,sal in uniquedata[0:10]:    
    dta = MakeAdjacencyMatrix(SplitString(sal,4), Dicts[2])
    np.save(outdir+val,dta)
