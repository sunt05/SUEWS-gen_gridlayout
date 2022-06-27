import f90nml
from pathlib import Path
import numpy as np


def gen_nml_GridLayout(p_sample, nlayer_new=9):

    if nlayer_new > 15:
        print("nlayer_new should NOT be larger than 15")
        return
    p_sample = Path(p_sample)
    nml = f90nml.read(p_sample)
    dict_nml = nml.todict()

    print(f"using {p_sample} as template ...")
    for group, dict_group in dict_nml.items():
        # print(f"{group}:")
        if group != "surf":
            for var, val in dict_group.items():
                if var == "nlayer":
                    print(f"{var}: {val} -> {nlayer_new}")
                    nlayer_old = val
                    dict_group[var] = nlayer_new
                    n_pad = nlayer_new - nlayer_old
                    print(f"padding {n_pad} layers ...")
                else:
                    ar_var_old = np.array(val)
                    if n_pad < 0:
                        raise ValueError(
                            f"nlayer_new [{nlayer_new}] < nlayer_old [{nlayer_old}]"
                        )
                    if n_pad > 0:
                        # 1d array
                        if len(ar_var_old.shape) == 1:
                            ar_var = np.pad(ar_var_old, (0, n_pad), "edge")
                        # 2d array
                        elif len(ar_var_old.shape) == 2:
                            # special cases
                            if var in [
                                "roof_albedo_dir_mult_fact",
                                "wall_specular_frac",
                            ]:
                                ar_var = np.pad(
                                    ar_var_old, ((0, n_pad), (0, 0)), "edge"
                                )
                            else:
                                ar_var = np.pad(
                                    ar_var_old, ((0, 0), (0, n_pad)), "edge"
                                )
                    # update nml
                    if var.startswith("_"):
                        pass
                    else:
                        dict_group[var] = ar_var.tolist()

                # if group == "roof":
                #     print(
                #         f"working on {var}: {type(val)}, {ar_var_old.shape} --> {ar_var.shape}"
                #     )
        # print("")

    nml_new = f90nml.Namelist(dict_nml)

    p_new = p_sample.parent / (p_sample.name + f".{nlayer_new}-layer")
    if p_new.exists():
        p_new.unlink()
    nml_new.write(p_new, force=True)
    print(f"saved to {p_new}")


if __name__ == "__main__":
    p_sample = Path("./GridLayouttest.nml.save")
    nlayer_new = 6
    gen_nml_GridLayout(p_sample, nlayer_new)
