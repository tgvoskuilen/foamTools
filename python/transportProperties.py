
import os
import csv


LJcoeffFile = 'LJ_Coeffs.csv'

with open(LJcoeffFile,'r') as LJfile:
    LJreader = csv.reader(LJfile)
    coeffs = {}
    for row in LJreader:
        try:
            sigma = round(float(row[1]),4)
            T = round(float(row[2]),4)
            name = row[0]
            coeffs[name] = (sigma, T)
        except ValueError:
            pass
        

for element in coeffs:
    print '%10s: %7.3f %8.2f' % (element, coeffs[element][0], coeffs[element][1])

# get sutherland coefficients from LJ
#
#   mu = 26.69*sqrt(M*T)/(sigma^2*Omega)
#    Omega = A/T'^B + C*exp(-DT') + E*exp(-F*T')
#    T' = kT/e
# 
#    A = 1.16145 B = 0.14874 C = 0.52487 D = 0.77320 E = 2.16178 F = 2.43787
#    mu in microPoise, sigma in Angstroms
#
#  Fit this to the Sutherland model of
#    mu = As * sqrt(T) / (1 + Ts/T)
#  to get As and Ts
#
#


