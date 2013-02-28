
import os
import csv

def read_Sutherland_coeffs():
    LJcoeffFile = 'SutherlandCoeffs.csv'

    with open(LJcoeffFile,'r') as LJfile:
        LJreader = csv.reader(LJfile)
        coeffs = {}
        for row in LJreader:
            try:
                name = row[0]
                As = float(row[1])
                Ts = float(row[2])
                coeffs[name] = (As, Ts)
            except ValueError:
                pass
            
    return coeffs

