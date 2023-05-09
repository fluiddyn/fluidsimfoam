FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      turbulenceProperties.b;
}

simulationType  RAS;

RAS
{
    // can be twophaseMixingLength, twophasekEpsilon or twophasekOmega
    RASModel                      twophaseMixingLength;
    turbulence                    on;
    printCoeffs                   on;
    twophaseMixingLengthCoeffs
    {
        expoLM        1.0;
        alphaMaxLM    0.61;
        kappaLM       0.41;
    }
}
