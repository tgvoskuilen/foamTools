from paraview.simple import *
import os

source = FindSource('hypergol.foam')
times = source.TimestepValues
view = GetActiveView()
exporters = servermanager.createModule("exporters")
render=Render()
for s in GetSources().values():
    r = GetDisplayProperties(s)
    if not r.Visibility: GetActiveView().Representations.remove(r)
basePath = os.path.normpath("D:/tmp")

for i,time in enumerate(times):
    if i > 1:
        view.ViewTime = time
        render=Render()
        filename = "POVexport%s.pov" % str(time)
        filepath = os.path.join(basePath,filename)
        print "Exporting to %s" % filepath
        povExp = exporters.POVExporter(FileName=filepath)
        povExp.SetView(view)
        povExp.Write()
        
        #Remove POV duplicate meshes and set format before proceeding

