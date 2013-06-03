
    // Correct processor patches by calling "evaluate"
        
    forAll(vsfs, i)
    {
        volScalarField& vsf = vsfs[i];
        
        volScalarField::GeometricBoundaryField& bf = vsf.boundaryField();
        
        //mimic "evaluate" but only for coupled patches (processor or cyclic)
        // and only for blocking or nonBlocking comms (no scheduled comms)
        if
        (
            Pstream::defaultCommsType == Pstream::blocking
         || Pstream::defaultCommsType == Pstream::nonBlocking
        )
        {
            label nReq = Pstream::nRequests();

            forAll(bf, patchi)
            {
                if(bf[patchi].coupled())
                {
                    bf[patchi].initEvaluate(Pstream::defaultCommsType);
                }
            }

            // Block for any outstanding requests
            if
            (
                Pstream::parRun()
             && Pstream::defaultCommsType == Pstream::nonBlocking
            )
            {
                Pstream::waitRequests(nReq);
            }

            forAll(bf, patchi)
            {
                if(bf[patchi].coupled())
                {
                    bf[patchi].evaluate(Pstream::defaultCommsType);
                }
            }
        }
        else
        {
            //Scheduled patch updates not supported
            FatalErrorIn("initDynamicMesh::correctProcessorPatches.H")
                << "Unsuported communications type "
                << Pstream::commsTypeNames[Pstream::defaultCommsType]
                << exit(FatalError);
        }
    }
    
    forAll(vvfs, i)
    {
        volVectorField& vvf = vvfs[i];
        
        volVectorField::GeometricBoundaryField& bf = vvf.boundaryField();
        
        //mimic "evaluate" but only for coupled patches (processor or cyclic)
        // and only for blocking or nonBlocking comms (no scheduled comms)
        if
        (
            Pstream::defaultCommsType == Pstream::blocking
         || Pstream::defaultCommsType == Pstream::nonBlocking
        )
        {
            label nReq = Pstream::nRequests();

            forAll(bf, patchi)
            {
                if(bf[patchi].coupled())
                {
                    bf[patchi].initEvaluate(Pstream::defaultCommsType);
                }
            }

            // Block for any outstanding requests
            if
            (
                Pstream::parRun()
             && Pstream::defaultCommsType == Pstream::nonBlocking
            )
            {
                Pstream::waitRequests(nReq);
            }

            forAll(bf, patchi)
            {
                if(bf[patchi].coupled())
                {
                    bf[patchi].evaluate(Pstream::defaultCommsType);
                }
            }
        }
        else
        {
            //Scheduled patch updates not supported
            FatalErrorIn("initDynamicMesh::correctProcessorPatches.H")
                << "Unsuported communications type "
                << Pstream::commsTypeNames[Pstream::defaultCommsType]
                << exit(FatalError);
        }
    }
