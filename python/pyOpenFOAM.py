
import os
import re
import string
import ast


def max_refinement_levels():
    """
    Reads and returns the max refinement setting from constant/dynamicMeshDict
    """
    meshdict = open('constant/dynamicMeshDict','r').readlines()
    mr = -1
    
    for line in meshdict:
        if "maxRefinement" in line:
            try:
                mr = int(string.split(line)[1][:-1])
                break
            except ValueError:
                pass

    return mr+1


def add_species_to_thermo_dict(species):
    """
    Takes the list of species and adds all non liquid ones (no "L") to the
    "Vapor" subspecies list
    """
    f_thermoDict = open('constant/thermophysicalProperties','r')
    thermo_lines = f_thermoDict.readlines()
    f_thermoDict.close()
    
    
    #read which species are liquid
    in_liquid = False
    in_subspecies = False
    bracket_count = 0
    liquid_species = []
    for i,line in enumerate(thermo_lines):
        if "Liquid" in line:
            in_liquid = True
            
        if "subspecies" in line and in_liquid:
            in_subspecies = True
            
        if ");" in line and in_liquid:
            in_subspecies = False
            
        if in_subspecies and in_liquid:
            if "{" in line:
                if bracket_count == 0:
                    nameline = thermo_lines[i-1]
                    liquid_species.append(nameline.strip())
                
                bracket_count = bracket_count + 1
            
            if "}" in line:
                bracket_count = bracket_count - 1
    
    #print "Liquid species:", liquid_species

    in_vapor = False
    in_subspecies = False
    ss_line_start = 0
    ss_line_end = 0

    for i,line in enumerate(thermo_lines):
        if "Vapor" in line:
            in_vapor = True

        if "subspecies" in line and in_vapor:
            in_subspecies = True
            ss_line_start = i+2

        if ");" in line and in_vapor and in_subspecies:
            ss_line_end = i
            break

    new_lines = []
    for specie in species:
        if specie not in liquid_species:
            n = 12 - len(specie)
            new_lines.append("        %s" % specie + n*" "+" {}\n")

    new_thermo = thermo_lines[:ss_line_start] + new_lines  \
                + thermo_lines[ss_line_end:]
    
    f_newDict = open('constant/thermophysicalProperties','w')
    f_newDict.writelines(new_thermo)
    f_newDict.close()
    



def load_thermo_db(dbpath):
    with open(dbpath,'r') as f:
        lines = f.readlines()
        
    db = {}
    
    for line in lines:
        d = ast.literal_eval(line.strip())
        db[d['Name']] = d
        
    return db


    
    
def thermo_string(data):
    """
    Takes a thermo dictionary entry and generates an OpenFOAM formatted
    dictionary entry string
    """
    tab = ' '*4
    endl = '\n'
    s = data['Name'] + endl + \
        '{' + endl + \
        tab + 'specie' + endl + \
        tab + '{' + endl + \
        2*tab + 'nMoles          1;' + endl + \
        2*tab + 'molWeight       %7.4f;' % data['W'] + endl + \
        tab + '}' + endl + \
        tab + 'thermodynamics' + endl + \
        tab + '{' + endl + \
        2*tab + 'Tlow            %6.1f;' % data['Tlow'] + endl + \
        2*tab + 'Thigh           %6.1f;' % data['Thigh'] + endl + \
        2*tab + 'Tcommon         %6.1f;' % data['Tmid'] + endl + \
        2*tab + 'highCpCoeffs    ( %s );' % " ".join(['%10.9e'%i for i in data['highCpCoeffs']]) + endl + \
        2*tab + 'lowCpCoeffs     ( %s );' % " ".join(['%10.9e'%i for i in data['lowCpCoeffs']]) + endl + \
        tab + '}' + endl + \
        tab + 'transport' + endl + \
        tab + '{' + endl + \
        2*tab + 'As              %10.9e;' % data['As'] + endl + \
        2*tab + 'Ts              %7.3f;' % data['Ts'] + endl + \
        tab + '}' + endl + \
        '}' + 2*endl;
    return s
        

def write_thermo(species, utilPath):
    """
    Takes a list of species and writes the thermo file using the database 
    entries. A fatal exception is raised if a specie is not found.
    """
    dbfile = os.path.join(utilPath,'props','thermo.pydb')
    db = load_thermo_db(dbfile)
    
    with open('constant/thermo','w') as thermoFile:
        for s in species:
            try:
                thermoFile.write(thermo_string(db[s.strip()]))
            except KeyError:
                print "\nERROR: Specie %s not found in database\n\n" % s
                raise

            
def load_chemistry(chemFile, utilFolder):
    chemPath = os.path.join(utilFolder, 'chem', chemFile)
    thermPath = os.path.join(utilFolder, 'props', 'thermo.dat')
    
    run('chemkinToFoam',args=chemPath+' '+thermPath+' constant/reactions constant/thermo');
    os.system('rm -f constant/thermo')
    

def read_species():
    """
    Reads the list of species from the "reactions" file
    """
    start = 0
    ns = 0
    lines = open('constant/reactions','r').readlines()
    for i,s in enumerate(lines):
        if "species" in s:
            ns = int(lines[i+1].rstrip())
            start = i+2
        lines[i] = s.rstrip()

    return lines[start+1:start+ns+1]
    


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



def touch_foam_files(name):
    """ Creates empty .foam files for paraview """
    foamname = name+'.foam'
    os.system('touch '+foamname)

    for dirname in get_proc_dirs():
        os.system('touch '+dirname+'/'+foamname)


def read_inputs(argv):
    """ Reads the command line input for np and whether this is a restart """
    if len(argv) > 1:
        try:
            return (int(argv[1]),False)
        except ValueError:
            if argv[1] == "resume":
                return (len(get_proc_dirs()),True)
            else:
                raise ValueError("Invalid argument")
    else:
        return (1,False)


def get_imbalance():
    """
    Gets the current parallel imbalance at the latest time.
    The imbalance is calculated from the filesize of each processor's
    most recent time step.
    """
    np = num_procs() 
    time_dirs = get_proc_times(0)

    if time_dirs is not None:
        time_values = [(float(td),td) for td in time_dirs]
        max_time_dir = max(time_values)[1]

        proc_sizes = []

        for p in range(0,np):
            dir_path = os.path.join(os.getcwd(),"processor"+str(p),max_time_dir)
            dir_size = get_dir_size(dir_path)
            proc_sizes.append(dir_size)

        proc_load = [abs(100.*np*s/float(sum(proc_sizes))-100.) for s in proc_sizes]

        return proc_load

    else:
        return None


def num_procs():
    """ Returns the number of processors used in this case """
    return length(get_proc_dirs())



def get_dir_size(start_path = '.'):
    """
    General function to recursively get the size of files in a directory
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def get_proc_times(proc=0, isParallel=True):
    """
    Returns a list of the time folders in a given processor
        (default folder: processor0). You can also get serial runs by setting
        isParallel to False (then proc argument is ignored)
    """
    if isParallel:
        proc_path = os.path.join(os.getcwd(), "processor"+str(proc))
    else:
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

        return time_dirs

    else:
        return None


def get_sorted_time_folders(isParallel=True):
    """
    Returns a sorted list of time folders with the lowest time folder
    omitted. This can be passed to the parallel reconstruction routines.
    """
    time_dirs = get_proc_times(proc=0,isParallel=isParallel)
    if time_dirs is not None:
        time_dirs.sort(key=float)
        time_dirs.pop(0)
        return time_dirs
    else:
        return None


def get_proc_pairing(np, ratio=1.0):
    """
    Get the pair of factors of np that most closely gives the desired aspect
    ratio (ratio = num1 / num2)
    """
    f = factors(np)
    fr = [abs(float(x[0])/float(x[1])-ratio) for x in f]
    return f[fr.index(min(fr))]


def get_proc_pairing3D(np):
    pairs = factors(np)
    triplets = []
    for pair in pairs:
        if pair[0] > 1:
            pf1 = factors(pair[0])
            for p in pf1:
                triplets.append((pair[1],p[0],p[1]))
            
        if pair[1] > 1:
            pf2 = factors(pair[1])
            for p in pf2:
                triplets.append((pair[0],p[0],p[1]))
            
    maxratios = []
    
    for t in triplets:
        r1 = t[0]/t[1] if t[0] > t[1] else t[1]/t[0]
        r2 = t[0]/t[2] if t[0] > t[2] else t[2]/t[0]
        r3 = t[1]/t[2] if t[1] > t[2] else t[2]/t[1]
            
        maxratios.append(max([r1,r2,r3]))
    
    return triplets[maxratios.index(min(maxratios))]


def set_balance_par(np):
    """
    Sets the balanceParDict file using the template .org file and np
    """
    os.system('rm -f system/balanceParDict')
    os.system("sed"+
              " -e s/NUMPROCS/"+str(np)+"/g"+
              " system/balanceParDict.org > system/balanceParDict")
             
              
def set_decompose_par(np, method="simple", ratio=1.0):
    """
    Sets the decomposeParDict file using the template .org file and two
    inputs (np and method).
    """
    pair = get_proc_pairing(np, ratio)
    os.system('rm -f system/decomposeParDict')
    os.system("sed"+
              " -e s/NUMPROCS/"+str(np)+"/g"+
              " -e s/DECOMPOSEPAR_METHOD/"+method+"/g"+
              " -e s/VALUE1/"+str(pair[0])+"/g"+
              " -e s/VALUE2/"+str(pair[1])+"/g"+
              " system/decomposeParDict.org > system/decomposeParDict")


def set_decompose_par3D(np, method="simple", ratio=1.0):
    """
    Sets the decomposeParDict file using the template .org file and two
    inputs (np and method).
    """
    pair = get_proc_pairing3D(np)
    
    os.system('rm -f system/decomposeParDict')
    os.system("sed"+
              " -e s/NUMPROCS/"+str(np)+"/g"+
              " -e s/DECOMPOSEPAR_METHOD/"+method+"/g"+
              " -e s/VALUE1/"+str(pair[0])+"/g"+
              " -e s/VALUE2/"+str(pair[1])+"/g"+
              " -e s/VALUE3/"+str(pair[2])+"/g"+
              " system/decomposeParDict.org > system/decomposeParDict")


def run(program, np=1, args="", hide=True):
    """
    General routine for running OpenFOAM programs, either in serial or parallel
    If np is set as 1, a serial run is used. Otherwise, mpirun is called.
    """ 
    if np > 1:
        cmd = "mpirun -np " + str(np) + " " + program + " -parallel " + args
    else:
        cmd = program + " " + args
        
    if hide:
        cmd = cmd + " > log." + program

    print " - Running Command: %s" % cmd
    os.system(cmd)


def factors(n):
    """ Return a list of factor pairs of the integer n"""
    fs = filter(lambda i: n % i == 0, range(1, n + 1))
    return [(x, n/x) for x in fs]



if __name__ == "__main__":
    print "This is pyOpenFOAM"




