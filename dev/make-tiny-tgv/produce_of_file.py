from pathlib import Path

from jinja2 import Template

# Find the current path
here = Path(__file__).absolute().parent

fvSolution_temp_path = str(here) + "/templates/fvSolution.j2"
# Load the template
with open(fvSolution_temp_path) as template_text:
    template = Template(template_text.read())


# Define the fvSolution_data for the template
fvSolution_data = {
    "version": 2.0,
    "format": "ascii",
    "class": "dictionary",
    "location": "system",
    "object": "fvSolution",
    "solvers": {
        "p": {
            "solver": "PCG",
            "preconditioner": "DIC",
            "tolerance": 1e-06,
            "relTol": 0.01,
        },
        "pFinal": {
            "solver": "PCG",
            "preconditioner": "DIC",
            "tolerance": 1e-06,
            "relTol": 0,
        },
        "U": {
            "solver": "PBiCGStab",
            "preconditioner": "DILU",
            "tolerance": 1e-08,
            "relTol": 0,
        },
    },
    "piso": {
        "nCorrectors": 2,
        "nNonOrthogonalCorrectors": 1,
        "pRefPoint": "(0 0 0)",
        "pRefValue": 0,
    },
}


# Render the template with the fvSolution_data
output = template.render(fvSolution_data)

# Define the path where the output file will be saved
output_path = here / "tmp_fvSolution"

# Write the rendered template to fvSolution file
with open(output_path, "w") as f:
    f.write(output)

print(f"{output_path} was generated successfully!")
