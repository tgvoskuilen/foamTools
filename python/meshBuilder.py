
import math

class Face(object):
    def __init__(self, localPoints, localIDs, globalPoints, name, patchType):
        self.pointIDs = []
        self.name = name
        self.patchType = patchType
        
        for p in localIDs:
            pt = localPoints[p]
            self.pointIDs.append( globalPoints.index(pt) )
        
    def __eq__(self,other):
        return all([i==j for i,j in zip(sorted(self.pointIDs), sorted(other.pointIDs))])

    def __neq__(self, other):
        return not self.__eq__(other)
        
    def __str__(self):
        return "(" + " ".join([str(p) for p in self.pointIDs]) + ")"
    
    def haspts(self,p,pts):
        """
        Checks if all three points in "p" are in the face's points
        """
        hasAll = True
        
        for i in p:
            hasPti = False
            for pid in self.pointIDs:
                if i == pts[pid]:
                    hasPti = True
                    break
                    
            if not hasPti:
                hasAll = False
                break
                
        return hasAll
        
    
    def coplanar(self,p,n,pts):
        for pid in self.pointIDs:
            v = pts[pid] - Point(p[0],p[1],p[2])
            d = v.dot(Point(n[0],n[1],n[2]))
            if abs(d) > 1e-6:
                return False
                
        return True
        
    def getEdges(self):
        return [(self.pointIDs[0], self.pointIDs[1]), \
                (self.pointIDs[1], self.pointIDs[2]), \
                (self.pointIDs[2], self.pointIDs[3]), \
                (self.pointIDs[3], self.pointIDs[0]) ]
        
        
class Point(object):
    def __init__(self, x, y, z):
        self.coords = [x,y,z]
    
    def x(self):
        return self.coords[0]
        
    def y(self):
        return self.coords[1]
        
    def z(self):
        return self.coords[2]
        
    def mag(self):
        return math.sqrt(self.x()**2. + self.y()**2. + self.z()**2.)
        
    def __eq__(self,other):
        return abs(self.coords[0] - other.coords[0]) < 1e-5 and \
               abs(self.coords[1] - other.coords[1]) < 1e-5 and \
               abs(self.coords[2] - other.coords[2]) < 1e-5
    
    def __neq__(self, other):
        return not self.__eq__(other)
        
    def __str__(self):
        return "(%6.5f %6.5f %6.5f)" % (self.coords[0], self.coords[1], self.coords[2])
        
    def __add__(self, other):
        return Point(self.coords[0]+other.coords[0], \
                     self.coords[1]+other.coords[1], \
                     self.coords[2]+other.coords[2])
                     
    def __sub__(self, other):
        return Point(self.coords[0]-other.coords[0], \
                     self.coords[1]-other.coords[1], \
                     self.coords[2]-other.coords[2])
    
    def __mul__(self, s):
        return Point(self.x()*s, self.y()*s, self.z()*s)
                     
    def inPlane(self, p, n):
        v = self - Point(p[0],p[1],p[2])
        d = v.dot(Point(n[0],n[1],n[2]))
        if abs(d) > 1e-3:
            return False
        else:
            return True
                     
    def dot(self, other):
        return self.coords[0]*other.coords[0] + \
               self.coords[1]*other.coords[1] + \
               self.coords[2]*other.coords[2]
    
class Block(object):
    def __init__(self, c1, c2, refdir, size=None):
        self.faces = []
        self.fixedSize = size
        
        if len(c1) != 3 or len(c2) != 3:
            raise ValueError("Input points must have 3 components each")
        
        if len(refdir) == 3:
            self.refdir = [refdir[0], refdir[0], refdir[0], refdir[0], \
                           refdir[1], refdir[1], refdir[1], refdir[1], \
                           refdir[2], refdir[2], refdir[2], refdir[2]]
        else:
            self.refdir = refdir
        
        vx = Point(c2[0] - c1[0], 0, 0)
        vy = Point(0, c2[1] - c1[1], 0)
        vz = Point(0, 0, c2[2] - c1[2])
        
        o = Point(c1[0], c1[1], c1[2])
        
        #points
        self.points = [o, o+vx, o+vx+vy, o+vy, o+vz, o+vx+vz, \
                       o+vx+vy+vz, o+vy+vz]
        
        self.size = [vx.mag(), vy.mag(), vz.mag()]
        
        #faces in local point IDs
        self.faces = [(2,1,0,3), (4,5,6,7), (6,5,1,2), (7,6,2,3), \
                      (4,7,3,0), (5,4,0,1)]
        
            
    def globalPoints(self, points):
        gpts = []
        for p in self.points:
            gpts.append( points.index(p) )
            
        return (gpts, self.size)
        
    
    def getFaces(self, points, defPatchType, defPatchName):
        """ All faces default to walls """
        faces = []
        for f in self.faces:
            faces.append( Face(self.points, f, points, defPatchName, defPatchType) )
            
        return faces
        
        
class Arc(object):
    def __init__(self,p1,p2,pt):
        self.p1 = p1
        self.p2 = p2
        self.pt = pt
        
    def scale(self,s):
        self.pt = self.pt*s
        
    def __str__(self):
        return "arc %d %d %s" % (self.p1, self.p2, str(self.pt))
    
    def __eq__(self,other):
        return (self.p1 == other.p1 and self.p2 == other.p2) or (self.p1 == other.p2 and self.p2 == other.p1)

    def __neq__(self, other):
        return not self.__eq__(other)
        
    def inPlane(self, point, normal, ptList):
        """
        Check if the arc's end points lies in a given plane
        """
        pA = ptList[self.p1]
        pB = ptList[self.p2]
        
        if pA.inPlane(point,normal) and pB.inPlane(point,normal):
            return True
        else:
            return False
        
    
class NonIsoBlock(Block):
    def __init__(self, p0,p1,p2,p3,p4,p5,p6,p7, refdir, size=None):
        self.faces = []
        self.fixedSize = size
        
        if len(refdir) == 3:
            self.refdir = [refdir[0], refdir[0], refdir[0], refdir[0], \
                           refdir[1], refdir[1], refdir[1], refdir[1], \
                           refdir[2], refdir[2], refdir[2], refdir[2]]
        else:
            self.refdir = refdir
        
        vxA = p1 - p0
        vxB = p7 - p6
        vyA = p3 - p0
        vyB = p6 - p5
        vzA = p4 - p0
        vzB = p6 - p2
        
        self.points = [p0,p1,p2,p3,p4,p5,p6,p7]
        self.size = [min(vxA.mag(),vxB.mag()), min(vyA.mag(),vyB.mag()), min(vzA.mag(),vzB.mag())]
        
        #faces in local point IDs
        self.faces = [(2,1,0,3), (4,5,6,7), (6,5,1,2), (7,6,2,3), \
                      (4,7,3,0), (5,4,0,1)]
        
class BlockMesh(object):
    def __init__(self, blocks, defPatchType="wall", defPatchName="walls"):
        self.blocks = []
        self.gradings = []
        self.points = []
        self.faces = []
        self.scale = 1
        self.baseUnit = 0.001 #mm
        self.arcs = []
        self.blockSrc = blocks
        
        # Gather unique list of points from blocks
        # points are just tuples?
        for block in blocks:
            for p in block.points:
                if p not in self.points:
                    self.points.append(p)
        
        # Build blocks from global points
        for block in blocks:
            self.blocks.append( block.globalPoints(self.points) )
            self.gradings.append( block.refdir )
        
        # Build faces from global points, remove exact duplicates
        tmpFaces = []
        for i,block in enumerate(blocks):
            for face in block.getFaces(self.points, defPatchType, defPatchName):
                if face not in tmpFaces:
                    # Face has not been added yet, add it to both
                    tmpFaces.append(face) #all the faces we've seen
                    self.faces.append(face) #only non-duplicate faces
                    #print "adding face %s from block %d" % (str(face), i)
                else:
                    # Face is in tmpFaces, so it is a duplicate internal
                    # face and should be removed
                    try:
                        #print "removing face %s from block %d" % (str(face), i)
                        idx = self.faces.index(face)
                        self.faces.pop(idx)
                    except ValueError:
                        print "tmpFaces = ", [str(x) for x in tmpFaces]
                        print "faces = ", [str(x) for x in self.faces]
                        print "face = ", face
                        
                        raise ValueError
         
                    
    def tagFaces(self,p,n,name,patchType=None):
        if patchType is None:
            patchType = 'patch'
            
        if len(p) != 3 or len(n) != 3:
            raise ValueError("Input points must have 3 components each") 
            
        for f in self.faces:
            if n is not None:
                if f.coplanar(p,n,self.points):
                    f.name = name
                    f.patchType = patchType
            else:
                if f.haspts(p,self.points): #p is a list or tuple of 3 points
                    f.name = name
                    f.patchType = patchType
        
    def removeArcsOnPlane(self, point, normal):
        if len(point) != 3 or len(normal) != 3:
            raise ValueError("Input points must have 3 components each") 
            
        newArcs = [a for a in self.arcs if not a.inPlane(point, normal, self.points)]
        self.arcs = newArcs
            
    
    def makeArcs(self,base,radius,direction):
    
        if len(base) != 3 or len(direction) != 3:
            raise ValueError("Input points must have 3 components each") 
            
        b = Point(base[0],base[1],base[2])
        n = Point(direction[0],direction[1],direction[2])
        tol = 1e-2
        
        for f in self.faces:
            # check if a face has an edge with both points on the cylinder
             
            for e in f.getEdges():
                p1 = self.points[e[0]]
                p2 = self.points[e[1]]
                
                rP1 = n*(n.dot(b-p1)) - (b-p1)
                rP2 = n*(n.dot(b-p2)) - (b-p2)
                dP = p2 - p1
                
                # skew criteria is to catch a pair of points on the cylinder surface aligned with the normal direction
                skew = abs(n.dot(p2 - p1)/dP.mag())
                    
                    
                if abs(rP1.mag() - radius) < tol and \
                   abs(rP2.mag() - radius) < tol and \
                   abs(skew - 1.0) > tol:
                    
                    height = 0.5*(n.dot(p1-b) + n.dot(p2-b))
                    
                    pA = rP1 + rP2
                    pA = pA*(radius/pA.mag()) + b + n*height
                    
                    #print "  pa", pA
                    aTmp = Arc(e[0],e[1],pA)
                    if aTmp not in self.arcs:
                        self.arcs.append(aTmp)
                        #print "matched ", p1, p2
                        
                #elif abs(p1.x()) < tol or abs(p2.x()) < tol:
                #    print "  almost with ", p1, p2, rP1.mag()-radius, rP2.mag()-radius, skew, radius
                        
            
        
        
    def __str__(self):
        s = r"""/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2.1.0                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //"""

        s = s + "\n\nconvertToMeters "+str(self.baseUnit)+";\n\nvertices\n(\n"
        
        for i,p in enumerate(self.points):
            s = s + " "*4 + str(p) + """ //"""+str(i)+"\n"
            
        s = s + ");\n\nblocks\n(\n"
        
        for i,b in enumerate(self.blocks):
            bpts = b[0]
            bsize = b[1]
            pts = " ".join([str(x) for x in bpts])
            if self.blockSrc[i].fixedSize is None:
                sz = " ".join([str(int(x*self.scale)) for x in bsize])
            else:
                sz = " ".join([str(int(x)) for x in self.blockSrc[i].fixedSize])
            
            ref = " ".join([str(x) for x in self.gradings[i]])
            s = s + "    hex (" + pts + ") ("+sz+") edgeGrading ("+ref+")\n"
            
            
        # a patch is a list of tuples of face names and types, for example:
        #  patches = [('walls','wall'), ('inlet','patch'), ('outlet','patch)]
        # if you make two faces of the same name and different type, it will
        # result in unexpected behavior
        patches = []
        for f in self.faces:
            if f.name not in [x[0] for x in patches]:
                patches.append((f.name,f.patchType))
                
            
        s = s + ");\n\n"
        
        if self.arcs:
            s = s + "edges\n(\n"
            for a in self.arcs:
                s = s + " "*4 + str(a) + "\n"
            s = s + ");\n\n"
        
        s = s + "boundary\n(\n"
        
        for p in patches:
            
            s = s + "    "+p[0]+"\n    {\n        type "+p[1]+";\n        faces\n"

            s = s + "        (\n"
        
            i = 0
            for f in self.faces:
                if f.name == p[0]:
                    s = s + " "*12 + str(f) + """ //"""+str(i)+"\n"
                    i = i + 1
        
            s = s + " "*8+");\n    }\n\n"
        
        s = s + ");\n"
        
        s = s + """mergePatchPairs
(
);

// ************************************************************************* //"""

        return s
        
            
