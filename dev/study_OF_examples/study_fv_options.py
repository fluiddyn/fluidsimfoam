import os
from pathlib import Path
from pprint import pprint

from fluidsimfoam.foam_input_files import dump, parse

tutorials_dir = Path(os.environ["FOAM_TUTORIALS"])

print(f"{tutorials_dir = }")

types = set()
types_coeffs = set()
types_no_coeffs = set()
no_types = set()

types_coeffs_saved = {
    "acousticDampingSource",
    "directionalPressureGradientExplicitSource",
    "explicitPorositySource",
    "interRegionExplicitPorositySource",
    "jouleHeatingSource",
    "multiphaseMangrovesSource",
    "multiphaseMangrovesTurbulenceModel",
    "solidificationMeltingSource",
}


for path in tutorials_dir.rglob("*"):
    if path.is_dir() or path.name != "fvOptions":
        continue

    print(path)

    text = path.read_text()

    tree = parse(text)

    for key, option in tree.children.items():
        try:
            _type = option["type"]
        except (TypeError, KeyError):
            _type = None
            # print(code)
            # options can be inside a `options` dict...
            no_types.add(key)
            continue

        types.add(_type)

        code = dump(option)

        if _type + "Coeffs" in code:
            types_coeffs.add(_type)
        else:
            types_no_coeffs.add(_type)

        # if _type in {"vectorSemiImplicitSource", "scalarSemiImplicitSource"}:
        #     print(code)

        # if _type in types_coeffs_saved:
        #     print(code)

        if "fixedCoeff" in code:
            print(code)


print("types:")
pprint(types)
print("types_coeffs:")
pprint(types_coeffs)
print("types_no_coeffs:")
pprint(types_no_coeffs)

print(f"{types_coeffs.intersection(types_no_coeffs) = }")
# {"vectorSemiImplicitSource", "scalarSemiImplicitSource"}
