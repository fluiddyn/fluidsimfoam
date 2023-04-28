FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      omega.b;
}

dimensions  [0 0 -1 0 0 0 0];

internalField  uniform 1e-20;

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
