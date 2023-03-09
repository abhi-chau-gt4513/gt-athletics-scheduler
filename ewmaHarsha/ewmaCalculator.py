# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 18:39:32 2023

@author: hgadd
"""
import pandas as pd
df = pd.read_csv('RankingsTransposed.csv', index_col='Year', parse_dates=True)
#2020,2021,2022 For Testing

def ewma(df, span, alpha):
    predictions = []
    startIndex = 0
    end = span
    while(len(df) > end):
        dataSet = df[startIndex:end]
        movingAverage = 0
        for n in range(span):
            movingAverage += (alpha) * ((1-alpha) ** (span - n - 1))*df[n + startIndex]
          
        
        if (movingAverage + 1) > 0:
            predictions.append(df[end] - movingAverage)
        startIndex += 1
        
        end += 1
    return predictions
        