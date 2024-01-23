FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      kw;
}

dimensions       [0 2 -2 0 0 0 0];

internalField    uniform 1e-06;

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
    walls
    {
        type     kqRWallFunction;
        value    uniform 1e-10;
    }
    frontAndBackPlanes
    {
        type    empty;
    }
}
