FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      epsilon;
}

dimensions  [0 2 -3 0 0 0 0];

internalField  uniform 1e-08;

boundaryField
{
    inlet
    {
        type    cyclic;
    }
    outlet
    {
        type    cyclic;
    }
    top
    {
        type    zeroGradient;
    }
    bottom
    {
        type    zeroGradient;
    }
    frontAndBackPlanes
    {
        type    empty;
    }
}
