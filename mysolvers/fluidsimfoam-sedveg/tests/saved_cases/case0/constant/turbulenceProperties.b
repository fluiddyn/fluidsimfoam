FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      turbulenceProperties.b;
}

simulationType    RAS;

RAS
{
    RASModel       twophasekOmegaVeg;
    turbulence     on;
    printCoeffs    on;
    twophasekOmegaVegCoeffs
    {
        alphaOmega         0.52;
        betaOmega          0.072;
        C3om               0.35;
        C4om               1.0;
        alphaKomega        0.5;
        alphaOmegaOmega    0.5;
        Clim               0.0;
        sigmad             0.0;
        Cmu                0.09;
        Clambda            0.01;
        KE2                0.0;
        KE4                1.0;
        KE6                0.2;
        KE7                0.15;
        nutMax             0.005;
        popeCorrection     false;
        writeTke           true;
    }
    twophasekOmegaCoeffs
    {
        alphaOmega         0.52;
        betaOmega          0.072;
        C3om               0.35;
        C4om               1.0;
        alphaKomega        0.5;
        alphaOmegaOmega    0.5;
        Clim               0.0;
        sigmad             0.0;
        Cmu                0.09;
        KE2                0.0;
        KE4                1.0;
        nutMax             0.005;
        popeCorrection     false;
        writeTke           true;
    }
}
