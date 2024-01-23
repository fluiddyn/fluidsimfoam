FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      nut;
}

dimensions       [0 2 -1 0 0 0 0];

internalField    uniform 0.0;

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
        type     nutkWallFunction;
        value    uniform 0.0;
    }
    frontAndBackPlanes
    {
        type    empty;
    }
}
