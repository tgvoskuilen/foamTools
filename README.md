foamTools
=========

Utilities and libraries for OpenFOAM


## geometryTools

A toolkit for creating 3D polyhedra and cutting them with planes, or finding
the plane in them that recreates a PLIC interface.

## initDynamicMesh

An executable for initializing a dynamically refined mesh. Loads alphaVapor
and refines at phase interfaces.

## VOFSetFields

A VOF version of setFields that uses the geometry toolkit to set shapes
like circles, spheres, and ellipses with their actual volume fraction.
This prevents the initial instability with a pixellated circle that
comes from using setFields.

## redistributeParPlus

Revised version of redistributePar that also distributes refinementHistory, so
you can use it with dynamicRefineFvMesh cases. Will be moved to the 
meshBalancing repo eventually and made public.
