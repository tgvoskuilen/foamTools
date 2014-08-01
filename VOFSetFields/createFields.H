
    // Load VOFSetFields dictionary
    IOdictionary VOFDict
    (
        IOobject
        (
            "VOFSetFieldsDict",
            mesh.time().system(),
            mesh,
            IOobject::MUST_READ_IF_MODIFIED,
            IOobject::NO_WRITE
        )
    );
    
    word vaporPhaseName = VOFDict.lookupOrDefault<word>("vaporPhaseName","none");
    
    vector Udefault = VOFDict.lookupOrDefault<vector>("Udefault",vector::zero);
    scalar Tdefault = VOFDict.lookupOrDefault<scalar>("Tdefault",0);
    
    volScalarField alphaLiquid
    (
        IOobject
        (
            "alphaL_",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mesh,
        dimensionedScalar("alphaL",dimless,0.0)
    );
    
    volScalarField* alphaVaporPtr = NULL;
    
    if( vaporPhaseName != "none" )
    {
        alphaVaporPtr = new volScalarField
        (
            IOobject
            (
                vaporPhaseName,
                runTime.timeName(),
                mesh,
                IOobject::MUST_READ,
                IOobject::AUTO_WRITE
            ),
            mesh
        );
    }
    volScalarField* TPtr = NULL;
    
    if( Tdefault > 0 )
    {
        TPtr = new volScalarField
        (
            IOobject
            (
                "T",
                runTime.timeName(),
                mesh,
                IOobject::MUST_READ,
                IOobject::AUTO_WRITE
            ),
            mesh
        );
    }
    
    
    volVectorField U
    (
        IOobject
        (
            "U",
            runTime.timeName(),
            mesh,
            IOobject::MUST_READ,
            IOobject::AUTO_WRITE
        ),
        mesh
    );
    

    
    volScalarField Yremaining
    (
        IOobject
        (
            "Yremaining",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mesh,
        dimensionedScalar("Yr",dimless,1.0)
    );
    
    
    // Read entries from dictionary
    
    PtrDictionary<shape> shapes
    (
        VOFDict.lookup("shapes"),
        shape::iNew(mesh)
    );
    
    HashTable<scalar> defaultSpecieValues(VOFDict.lookup("defaultSpecies"));
    
    HashTable<label> phaseNames(5);
    label idx = 0;
    
    List<word> specieNames = defaultSpecieValues.toc();
    
    forAllConstIter(PtrDictionary<shape>, shapes, shapeI)
    {
        specieNames.append( shapeI().species() );
        phaseNames.insert( shapeI().phaseName(), idx );
        idx++;
    }
    
    
    
    PtrList<volScalarField> liquidPhases(phaseNames.size());
    
    Info<< "Loading phases " << phaseNames << endl;
    
    for(label i = 0; i < phaseNames.size(); ++i)
    {
        word name = phaseNames.toc()[i];
        label idx = phaseNames[name];
        Info<< "Loading phase " << name  << endl;
        
        liquidPhases.set
        (
            idx,
            new volScalarField
            (
                IOobject
                (
                    name,
                    runTime.timeName(),
                    mesh,
                    IOobject::MUST_READ,
                    IOobject::AUTO_WRITE
                ),
                mesh
            )
        );
        
        liquidPhases[idx] = dimensionedScalar("zero",dimless,0.0);
    }
    
    
    
    
    
    PtrList<volScalarField> species(specieNames.size());
    
    Info<< "Loading species " << specieNames << endl;
    
    for(label i = 0; i < specieNames.size(); ++i)
    {
        //Follow basicMultiComponentMixture
        Info<< "Loading specie " << specieNames[i] << endl;
        
        IOobject header
        (
            specieNames[i],
            mesh.time().timeName(),
            mesh,
            IOobject::NO_READ
        );
        
        if (header.headerOk())
        {
            species.set
            (
                i,
                new volScalarField
                (
                    IOobject
                    (
                        specieNames[i],
                        runTime.timeName(),
                        mesh,
                        IOobject::MUST_READ,
                        IOobject::AUTO_WRITE
                    ),
                    mesh
                )  
            );
        }
        else
        {
            volScalarField Ydefault
            (
                IOobject
                (
                    "Ydefault",
                    mesh.time().timeName(),
                    mesh,
                    IOobject::MUST_READ,
                    IOobject::NO_WRITE
                ),
                mesh
            );

            species.set
            (
                i,
                new volScalarField
                (
                    IOobject
                    (
                        specieNames[i],
                        mesh.time().timeName(),
                        mesh,
                        IOobject::NO_READ,
                        IOobject::AUTO_WRITE
                    ),
                    Ydefault
                )
            );
        }
    }
    
    
    alphaLiquid = dimensionedScalar("alphaLiquid",dimless,0.0);
    
    U = dimensionedVector("U",dimVelocity,Udefault);
    
    if( TPtr != NULL )
    {
        volScalarField& T = *TPtr;
        T = dimensionedScalar("T",dimTemperature,Tdefault);
    }
    
    forAll(species, i)
    {
        species[i] = dimensionedScalar(species[i].name(),dimless,0.0);
    }
    
    

    
