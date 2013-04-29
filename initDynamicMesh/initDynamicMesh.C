/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 2011 OpenFOAM Foundation
     \\/     M anipulation  |
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

Application
    multiphaseInterFoam

Description
    Solver for n incompressible fluids which captures the interfaces and
    includes surface-tension and contact-angle effects for each phase.

    Turbulence modelling is generic, i.e. laminar, RAS or LES may be selected.

\*---------------------------------------------------------------------------*/

#include "argList.H"
#include "timeSelector.H"
#include "Time.H"
#include "fvMesh.H"
#include "fvCFD.H"
#include "dynamicFvMesh.H"

using namespace Foam;

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createDynamicFvMesh.H"
    
    
    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
	
    IOdictionary initDynamicMeshDict
    (
        IOobject
        (
            "initDynamicMeshDict",
            mesh.time().system(),
            mesh,
            IOobject::MUST_READ_IF_MODIFIED,
            IOobject::NO_WRITE
        )
    );
    
    word alphaName = initDynamicMeshDict.lookup("alphaName");
    
    List<word> vsfNames = initDynamicMeshDict.lookup("volScalarFields");
    List<word> vvfNames = initDynamicMeshDict.lookup("volVectorFields");
    
    
    PtrList<volScalarField> vsfs(vsfNames.size());
    PtrList<volVectorField> vvfs(vvfNames.size());
    
    forAll(vsfNames, vi)
    {
        Info<< "Loading " << vsfNames[vi] << endl;
        vsfs.set
        (
            vi,
            new volScalarField
            (
                IOobject
                (
                    vsfNames[vi],
                    runTime.timeName(),
                    mesh,
                    IOobject::MUST_READ,
                    IOobject::AUTO_WRITE
                ),
                mesh
            )
        );
    }
    
    forAll(vvfNames, vi)
    {
        Info<< "Loading " << vvfNames[vi] << endl;
        vvfs.set
        (
            vi,
            new volVectorField
            (
                IOobject
                (
                    vvfNames[vi],
                    runTime.timeName(),
                    mesh,
                    IOobject::MUST_READ,
                    IOobject::AUTO_WRITE
                ),
                mesh
            )
        );
    }
    
    //const volVectorField& U = mesh.lookupObject<volVectorField>("U");
    //#include "createPhi.H" //needed to do boundary corrections.
    
    
    
    Info<< "Reading field " << alphaName << endl;
    
    volScalarField alpha1
    (
        IOobject
        (
            alphaName,
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    );
    

    volScalarField refinementField
    (
        IOobject
        (
            "refinementField",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        1e6*mag(fvc::grad(alpha1))
    );

    runTime.setDeltaT(1e-6);
    runTime++;
    
    Info<< "Time = " << runTime.timeName() << nl << endl;

    scalar timeBeforeMeshUpdate = runTime.elapsedCpuTime();
    {
	    mesh.update();
    }
    
    /*
    alpha1.correctBoundaryConditions();
    
    forAll(vsfs, i)
    {
        vsfs[i].correctBoundaryConditions();
    }
    
    forAll(vvfs, i)
    {
        vvfs[i].correctBoundaryConditions();
    }
    */

	if (mesh.changing())
	{
		Info<< "Execution time for mesh.update() = "
			<< runTime.elapsedCpuTime() - timeBeforeMeshUpdate
			<< " s" << endl;
	}

	
	runTime.writeNow();


    Info<< "End\n" << endl;

    return 0;
}


// ************************************************************************* //
