FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      alpha_a;
}

dimensions       [0 0 0 0 0 0 0];

internalField    uniform 0.012;

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
        type    zeroGradient;
    }
    frontAndBackPlanes
    {
        type    empty;
    }
}
