
import os
import gzip
import string
import csv
import re

def get_proc_dirs():
    """
    Returns a list of all processor directories. For example:
     ['processor0','processor1','processor2']
    """
    proc_dirs = []

    dirs = [ d for d in os.listdir(os.getcwd()) 
             if os.path.isdir(os.path.join(os.getcwd(), d)) ]

    for dirname in dirs:
        if re.match('processor[0-9]+',dirname):
            proc_dirs.append(dirname)
    
    return proc_dirs
    
    
def get_times(proc_path=None):
    """
    Returns a sorted list of the time folders
    """
    
    if proc_path is None:
        proc_path = os.getcwd()

    if os.path.isdir(proc_path):

        proc_dirs = [ d for d in os.listdir(proc_path) 
                      if os.path.isdir(os.path.join(proc_path, d)) ]

        time_dirs = []

        for dirname in proc_dirs:
            try:
                t = float(dirname)
                time_dirs.append(dirname)
            except ValueError:
                pass

        time_dirs.sort(key=float)
        time_dirs.pop(0) #remove zero time folder

        return time_dirs

    else:
        return None
        
def get_fields(folder):
    """
    Get a list of the field names from the first populated folder
    """
    time_path = os.path.join(os.getcwd(), folder)
    
    if os.path.isdir(time_path):
        gzFiles = [f for f in os.listdir(time_path)
                   if f.endswith('.gz')]
        
        fields = ['Time']
        for f in gzFiles:
            n,e = os.path.splitext(f)
            fields.append(n)
            
        return fields
    
    else:
        return None


def get_field_max(proc,time,fieldName):
    """
    Unzip and read the data from all the specified fields in a given folder
    """
    time_path = os.path.join(proc, time)
    
    if os.path.isdir(time_path):
        filePath = os.path.join(time_path,fieldName+'.gz')
        fz = gzip.open(filePath,'rb')
        content = fz.read()
        fz.close()
        
        loc1 = string.find(content,'internalField')
        chop1 = content[loc1:]
        loc2 = string.find(chop1,';')
        chop2 = chop1[13:loc2]
        
        if "nonuniform" not in chop2:
            maxVal = float(string.split(chop2)[1])
        else:
            lines = chop2.split('\n')
            lines = lines[3:-2]
            
            maxVal = max([float(x) for x in lines])

        return maxVal
    
    else:
        return None




if __name__ == "__main__":
    proc_dirs = get_proc_dirs()
    times = get_times(proc_dirs[0])
    
    data = []
    
    for i,t in enumerate(times):
        print "Reading time %d of %d" % (i+1,len(times))
        
        maxT = 0.
        
        for p in proc_dirs:
            maxT = max(maxT, get_field_max(p,t,"T"))
            
        data.append([float(t), maxT])
    
    with open('MaxTemp_Gels.csv','w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['Time (s)','Max Temp (K)'])
        for row in data:
            writer.writerow(row)
            
            
    
