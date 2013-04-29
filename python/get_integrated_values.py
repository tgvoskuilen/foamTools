try: paraview.simple
except: from paraview.simple import *

import os
import csv

source = FindSource('evaporation.foam')
times = source.TimestepValues
iv = IntegrateVariables()

rv1 = GetRenderView()
as1 = GetAnimationScene()
spreadsheet = CreateRenderView()
spreadsheet.ViewTime = times[0]
dr = Show()
as1.ViewModules = spreadsheet

vol = []
frac = []

for n,time in enumerate(times):
    print "Capturing time %d of %d" % (n+1, len(times))
    spreadsheet.ViewTime = time
    Render()
    Vrange = iv.CellData.GetArray("alphaLiquid").GetRange()
    volRange = iv.CellData.GetArray("Volume").GetRange()
    vol.append(volRange[0])
    frac.append(Vrange[0]/volRange[0])
    

# Write point data to a csv file
with open('totalVol.csv','w') as csvfile:
    pointwriter = csv.writer(csvfile)
    header_row = ["Time", "Volume Fraction", "Domain Volume"]
    pointwriter.writerow(header_row)

    for i,t in enumerate(times):
        row = [t, frac[i], vol[i]]
        pointwriter.writerow(row)

