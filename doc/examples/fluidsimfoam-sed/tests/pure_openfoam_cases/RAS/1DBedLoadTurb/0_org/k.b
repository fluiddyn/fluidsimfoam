FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      k;
}

dimensions  [0 2 -2 0 0 0 0];

internalField   uniform 1e-6;

boundaryField
{
    inlet
    {
        type            cyclic;
    }
    outlet
    {
        type            cyclic;
    }
    top
    {
        type            zeroGradient;
    }
    bottom
    {
        type            fixedValue;
        value           uniform 1e-6;
    }
    frontAndBackPlanes
    {
        type            empty;
    }
}
