from chempy import Substance
from pystrict import strict

from PySDM.initialisation import spectra
from PySDM.initialisation.aerosol_composition import DryAerosolMixture
from PySDM.physics import si
from PySDM.physics.constants_defaults import rho_w

# not in the paper - guessed and checked to match
CONSTANTS_ARG = {
    "Mv": 18.015 * si.g / si.mol,
    "Md": 28.97 * si.g / si.mol,
}
nu_w = CONSTANTS_ARG["Mv"] / rho_w


@strict
class AerosolARG(DryAerosolMixture):
    def __init__(
        self,
        M2_sol: float = 0,
        M2_N: float = 100 / si.cm**3,
        M2_rad: float = 50 * si.nm,
    ):
        mode1 = {"(NH4)2SO4": 1.0, "insoluble": 0.0}
        mode2 = {"(NH4)2SO4": M2_sol, "insoluble": (1 - M2_sol)}
        super().__init__(
            compounds=("(NH4)2SO4", "insoluble"),
            molar_masses={
                "(NH4)2SO4": 132.14 * si.g / si.mole,
                "insoluble": 44 * si.g / si.mole,
            },
            densities={
                "(NH4)2SO4": 1.77 * si.g / si.cm**3,
                "insoluble": 1.77 * si.g / si.cm**3,
            },
            is_soluble={"(NH4)2SO4": True, "insoluble": False},
            ionic_dissociation_phi={"(NH4)2SO4": 3, "insoluble": 0},
        )
        self.modes = (
            {
                "kappa": self.kappa(mode1, nu_w),
                "spectrum": spectra.Lognormal(
                    norm_factor=100.0 / si.cm**3, m_mode=50.0 * si.nm, s_geom=2.0
                ),
            },
            {
                "kappa": self.kappa(mode2, nu_w),
                "spectrum": spectra.Lognormal(
                    norm_factor=M2_N, m_mode=M2_rad, s_geom=2.0
                ),
            },
        )


@strict
class AerosolWhitby(DryAerosolMixture):
    def __init__(self):
        nuclei = {"(NH4)2SO4": 1.0}
        accum = {"(NH4)2SO4": 1.0}
        coarse = {"(NH4)2SO4": 1.0}

        super().__init__(
            ionic_dissociation_phi={"(NH4)2SO4": 3},
            molar_masses={
                "(NH4)2SO4": Substance.from_formula("(NH4)2SO4").mass
                * si.gram
                / si.mole
            },
            densities={"(NH4)2SO4": 1.77 * si.g / si.cm**3},
            compounds=("(NH4)2SO4",),
            is_soluble={"(NH4)2SO4": True},
        )
        self.modes = (
            {
                "kappa": self.kappa(nuclei, nu_w),
                "spectrum": spectra.Lognormal(
                    norm_factor=1000.0 / si.cm**3, m_mode=0.008 * si.um, s_geom=1.6
                ),
            },
            {
                "kappa": self.kappa(accum, nu_w),
                "spectrum": spectra.Lognormal(
                    norm_factor=800 / si.cm**3, m_mode=0.034 * si.um, s_geom=2.1
                ),
            },
            {
                "kappa": self.kappa(coarse, nu_w),
                "spectrum": spectra.Lognormal(
                    norm_factor=0.72 / si.cm**3, m_mode=0.46 * si.um, s_geom=2.2
                ),
            },
        )
