try: paraview.simple
except: from paraview.simple import *

import os
import csv

source = FindSource('hypergol.foam')
times = source.TimestepValues

PlotOverLine1 = PlotOverLine( Source="High Resolution Line Source" )

PlotOverLine1.Source.Point1 = [0, 0.0, 0.003]
PlotOverLine1.Source.Point2 = [0, 0.01, 0.003]


writer = CreateWriter('test.csv', PlotOverLine1)
writer.FieldAssociation = "Points"
writer.UpdatePipeline()
del writer
