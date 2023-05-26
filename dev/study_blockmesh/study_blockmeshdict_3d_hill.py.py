import os
from math import exp
from runpy import run_path

d = {
    "a": 5,
    "height": 5,
    "width": 10,
    "l2": 25,
    "divx": 20,
    "divy": 20,
    "divz": 20,
    "ngau": 100,
    "AmpGau": 3,
}


default_params = {
    "converttometer": 1,
    "xgrading": 1,
    "ygrading": 0.2,
    "zgrading": 1,
}

for key, value in default_params.items():
    if key not in d:
        d[key] = value

semiwidth = d["width"] / 2

txt = """
FoamFile
{
version 2.0;
format ascii;
class dictionary;
object blockMeshDict;
}
"""

txt += """
scale {k};

vertices
(
( {l2} {height} 0.0) // NorthEstsq = 0
(-{l2} {height} 0.0) // NorthWestsq = 1
(-{l2} 0.0 0.0) // SouthWestsq = 2
( {l2} 0.0 0.0) // SouthEstsq = 3

( {a} {height} 0.) // NorthEst = 4
(-{a} {height} 0.) // NorthWest = 5
(-{a} 0. 0.) // SouthWest = 6
( {a} 0. 0.) // SouthEst = 7

( {l2} {height} {h}) // NorthEstsqt = 8
(-{l2} {height} {h}) // NorthWestsqt = 9
(-{l2} 0. {h}) // SouthWestsqt = 10
( {l2} 0. {h}) // SouthEstsqt = 11

( {a} {height} {h}) // NorthEstsqt = 12
(-{a} {height} {h}) // NorthWestsqt = 13
(-{a} 0. {h}) // SouthWestsqt = 14
( {a} 0. {h}) // SouthEstsqt = 15

( {l2} {height} -{h}) // NorthEstsqt = 16
(-{l2} {height} -{h}) // NorthWestsqt = 17
(-{l2} 0. -{h}) // SouthWestsqt = 18
( {l2} 0. -{h}) // SouthEstsqt = 19

( {a} {height} -{h}) // NorthEstsqt = 20
(-{a} {height} -{h}) // NorthWestsqt = 21
(-{a} 0. -{h}) // SouthWestsqt = 22
( {a} 0. -{h}) // SouthEstsqt = 23

( 0. 0. -{h}) // NorthEstsqt = 24
( 0. {AG} 0.) // NorthWestsqt = 25
( 0. 0. {h}) // SouthWestsqt = 26

( 0. {height} -{h}) // SouthEstsqt = 27
( 0. {height} 0.) // NorthEstsqt = 28
( 0. {height} {h}) // NorthWestsqt = 29
);

""".format(
    l2=d["l2"],
    height=d["height"],
    h=semiwidth,
    a=d["a"],
    AG=d["AmpGau"],
    k=d["converttometer"],
)


txt += """
blocks
(
    //square block
    hex (9 13 14 10 1 5 6 2) ({divx} {divy} {divz}) simpleGrading ({xgrading} {ygrading} {zgrading})

    //square block
    hex (1 5 6 2 17 21 22 18) ({divx} {divy} {divz}) simpleGrading ({xgrading} {ygrading} {zgrading})

    //square block
    hex (12 8 11 15 4 0 3 7) ({divx} {divy} {divz}) simpleGrading ({xgrading} {ygrading} {zgrading})

    //square block
    hex (4 0 3 7 20 16 19 23) ({divx} {divy} {divz}) simpleGrading ({xgrading} {ygrading} {zgrading})

    //slice1
    hex (13 29 26 14 5 28 25 6) ({divx} {divy} {divz}) simpleGrading ({xgrading} {ygrading} {zgrading})

    //slice1
    hex (29 12 15 26 28 4 7 25) ({divx} {divy} {divz}) simpleGrading ({xgrading} {ygrading} {zgrading})

    //slice1
    hex (5 28 25 6 21 27 24 22) ({divx} {divy} {divz}) simpleGrading ({xgrading} {ygrading} {zgrading})

    //slice1
    hex (28 4 7 25 27 20 23 24) ({divx} {divy} {divz}) simpleGrading ({xgrading} {ygrading} {zgrading})

);
""".format(
    divx=d["divx"],
    divy=d["divy"],
    divz=d["divz"],
    xgrading=d["xgrading"],
    ygrading=d["ygrading"],
    zgrading=d["zgrading"],
)

x_dot = []
y_dot = []

z_dot2 = []
y_dot2 = []

txt += """
//create the spline
edges
(
spline 6 25 ("""

for i in range(d["ngau"]):
    txt += """
    ({x} {y} {z})""".format(
        x=-d["a"] + d["a"] * float(i + 1) / d["ngau"],
        y=d["AmpGau"]
        * exp(-((-d["a"] + d["a"] * float(i + 1) / d["ngau"]) ** 2.0) / 2.0),
        z=0,
    )
    x_dot.append(-d["a"] + d["a"] * float(i + 1) / d["ngau"])
    y_dot.append(
        d["AmpGau"]
        * exp(-((-d["a"] + d["a"] * float(i + 1) / d["ngau"]) ** 2.0) / 2.0)
    )

txt += """
)
   (0 0 0)
   (0 0 0)

spline 25 7 ("""

for i in range(d["ngau"]):
    txt += """
    ({x} {y} {z})""".format(
        x=d["a"] * float(i + 1) / d["ngau"],
        y=d["AmpGau"] * exp(-((d["a"] * float(i + 1) / d["ngau"]) ** 2.0) / 2.0),
        z=0,
    )
    x_dot.append(d["a"] * float(i + 1) / d["ngau"])
    y_dot.append(
        d["AmpGau"] * exp(-((d["a"] * float(i + 1) / d["ngau"]) ** 2.0) / 2.0)
    )

txt += """
)
   (0 0 0)
   (0 0 0)

spline 24 25 (
"""

for i in range(d["ngau"]):
    txt += """
    ({x} {y} {z})""".format(
        x=0,
        y=d["AmpGau"]
        * exp(
            -((-semiwidth + semiwidth * float(i + 1) / d["ngau"]) ** 2.0) / 2.0
        ),
        z=-semiwidth + semiwidth * float(i + 1) / d["ngau"],
    )
    z_dot2.append(-semiwidth + semiwidth * float(i + 1) / d["ngau"])
    y_dot2.append(
        d["AmpGau"]
        * exp(-((-semiwidth + semiwidth * float(i + 1) / d["ngau"]) ** 2.0) / 2.0)
    )
txt += """
)
(0 0 0)
(0 0 0)


spline 25 26 (
"""

for i in range(d["ngau"]):
    txt += """
    ({x} {y} {z})""".format(
        x=0,
        y=d["AmpGau"]
        * exp(-((semiwidth * float(i + 1) / d["ngau"]) ** 2.0) / 2.0),
        z=semiwidth * float(i + 1) / d["ngau"],
    )
    z_dot2.append(semiwidth * float(i + 1) / d["ngau"])
    y_dot2.append(
        d["AmpGau"] * exp(-((semiwidth * float(i + 1) / d["ngau"]) ** 2.0) / 2.0)
    )
txt += """
)
(0 0 0)
(0 0 0)

);"""

txt += """
patches
(

patch surface
(
(9 13 5 1)
(13 29 28 5)
(29 12 4 28)
(12 8 0 4)
(1 5 21 17)
(5 28 27 21)
(28 4 20 27)
(4 0 16 20)
)

wall bottom
(
(10 14 6 2)
(14 26 25 6)
(26 15 7 25)
(15 11 3 7)
(2 6 22 18)
(6 25 24 22)
(25 7 23 24)
(7 3 19 23)
)

patch side_r
(
(9 13 14 10)
(13 29 26 14)
(29 12 15 26)
(12 8 11 15)
)

patch side_l
(
(17 21 22 18)
(21 27 24 22)
(27 20 23 24)
(20 16 19 23)
)

patch inlet
(
(1 9 10 2)
(17 1 2 18)
)

patch outlet
(
(0 8 11 3)
(16 0 3 19)
)
);"""

# print(txt)

path = os.path.join("system", "blockMeshDict")
print("save new blockMeshDict in path\n" + path)

with open(path, "w") as f:
    f.write(txt)

import numpy as np

import matplotlib.pyplot as plt

plt.subplot(1, 2, 1)
plt.plot(x_dot, y_dot, label="x-y")
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(z_dot2, y_dot2, label="z-y")
plt.legend()
plt.show()
