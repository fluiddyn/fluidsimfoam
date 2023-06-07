"""Helper to create decomposeParDict files"""

from math import prod

from fluidsimfoam.foam_input_files import FileHelper, FoamInputFile

supported_methods = set(
    [
        "simple",
        "scotch",
        "hierarchical",
    ]
)

methods = set(
    [
        "manual",
        "simple",
        "hierarchical",
        "kahip",
        "metis",
        "scotch",
        "structured",
        "multiLevel",
    ]
)


def check_method(method):
    if method not in methods:
        raise ValueError(f"{method = } not in {methods}")

    if method not in supported_methods:
        raise NotImplementedError(f"{method = } not in {supported_methods = }")


class DecomposeParDictHelper(FileHelper):
    def __init__(
        self,
        nsubdoms=1,
        method="scotch",
    ):
        self.nsubdoms = nsubdoms
        check_method(method)
        self.method = method

    def complete_params(self, params):
        par_params = params._set_child(
            "parallel",
            attribs={
                "nsubdoms": 1,
                "method": self.method,
                "nsubdoms_xyz": None,
                "order": "xyz",
                "delta": 0.001,
            },
            doc="TODO",
        )

        par_params._set_child("scotch", attribs={"strategy": None})

    def make_tree(self, params):
        par_params = params.parallel

        nsubdoms = par_params.nsubdoms
        if nsubdoms == 1:
            return False

        method = par_params.method
        check_method(method)

        tree = FoamInputFile(
            info={
                "version": 2.0,
                "format": "ascii",
                "class": "dictionary",
                "location": '"system"',
                "object": "decomposeParDict",
            }
        )

        data = {"numberOfSubdomains": nsubdoms, "method": method}

        key_coeffs_dict = "coeffs"
        if method == "simple":
            coeffs = {
                "n": par_params.nsubdoms_xyz,
                "order": par_params.order,
                "delta": par_params.delta,
            }
        elif method == "scotch":
            if par_params.scotch.strategy is None:
                coeffs = None
            else:
                coeffs = {"strategy": par_params.scotch.strategy}
        elif method == "hierarchical":
            coeffs = {"n": par_params.nsubdoms_xyz}
        else:
            raise RuntimeError

        if coeffs is not None:
            try:
                nsubdoms_xyz = coeffs["n"]
            except KeyError:
                pass
            else:
                if nsubdoms_xyz is None:
                    raise ValueError("params.parallel.nsubdoms_xyz is None")

                if isinstance(nsubdoms_xyz, str):
                    nsubdoms_xyz = [
                        int(word) for word in nsubdoms_xyz.strip()[1:-1].split()
                    ]

                if prod(nsubdoms_xyz) != nsubdoms:
                    raise ValueError(
                        "Inconsistent parallel parameters: "
                        f"prod({nsubdoms_xyz=}) != {nsubdoms=}"
                    )

            data[key_coeffs_dict] = coeffs

        tree.init_from_py_objects(data)

        return tree
