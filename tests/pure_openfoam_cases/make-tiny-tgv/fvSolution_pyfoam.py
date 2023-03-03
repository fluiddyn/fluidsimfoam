from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from jinja2 import Template


# Load the fvSolution file using PyFoam
fvSolution = ParsedParameterFile("system/fvSolution")

# Access the solvers dictionary
solvers = fvSolution["solvers"]

# Set FoamFile

fvSolution_data = {
    "version": "2.0",
    "format": "ascii",
    "class": "dictionary",
    "location": "system",
    "object": "fvSolution",
}


fvSolution_data["solvers"] = dict(solvers)

# Access the PISO dictionary
piso = fvSolution["PISO"]
fvSolution_data["piso"] = dict(piso)


# Load the template
template_text = open("templates/fvSolution.j2").read()
template = Template(template_text)


# Render the template with the fvSolution_data
output = template.render(fvSolution_data)

# Write the rendered template to fvSolution2 to compare with fvSolution
with open("system/fvSolution2", "w") as f:
    f.write(output)

print(f"{output_path} was generated successfully!")