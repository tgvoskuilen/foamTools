foamTools
=========

Utilities and libraries for OpenFOAM. This has been tested with OpenFOAM-2.1.x and OpenFOAM-2.2.x


## geometryTools

A toolkit for creating 3D polyhedra and cutting them with planes, or finding
the plane in them that recreates a PLIC interface.

## initDynamicMesh

An executable for initializing a dynamically refined mesh. Loads alphaVapor
and refines at phase interfaces. The dictionary interface allows setting
subspecie concentrations, velocities, and vapor layers as well.

## VOFSetFields

A VOF version of setFields that uses the geometry toolkit to set shapes
like circles, spheres, and ellipses with their actual volume fraction.
This prevents the initial instability with a pixellated circle that
comes from using setFields.

