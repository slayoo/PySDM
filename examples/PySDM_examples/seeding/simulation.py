import numpy as np

from PySDM_examples.seeding.settings import Settings

from PySDM import Builder, Formulae
from PySDM.backends import CPU
from PySDM.environments import Parcel
from PySDM.dynamics import Condensation, AmbientThermodynamics, Coalescence, Seeding
from PySDM.dynamics.collisions.collision_kernels import Geometric
from PySDM.initialisation.sampling.spectral_sampling import ConstantMultiplicity
from PySDM import products


class Simulation:
    def __init__(self, settings: Settings):
        builder = Builder(
            n_sd=settings.n_sd_seeding + settings.n_sd_initial,
            backend=CPU(formulae=Formulae(seed=100), override_jit_flags={"parallel": False}),
            environment=Parcel(
                dt=settings.timestep,
                mass_of_dry_air=settings.mass_of_dry_air,
                w=settings.updraft,
                initial_water_vapour_mixing_ratio=settings.initial_water_vapour_mixing_ratio,
                p0=settings.initial_total_pressure,
                T0=settings.initial_temperature,
            ),
        )
        builder.add_dynamic(AmbientThermodynamics())
        builder.add_dynamic(Condensation())
        builder.add_dynamic(Coalescence(collision_kernel=Geometric()))
        builder.add_dynamic(
            Seeding(
                super_droplet_injection_rate=settings.super_droplet_injection_rate,
                seeded_particle_multiplicity=settings.seeded_particle_multiplicity,
                seeded_particle_extensive_attributes=settings.seeded_particle_extensive_attributes,
            )
        )

        r_dry, n_in_dv = ConstantMultiplicity(
            settings.initial_aerosol_dry_radii
        ).sample(n_sd=settings.n_sd_initial, backend=builder.particulator.backend)
        attributes = builder.particulator.environment.init_attributes(
            n_in_dv=n_in_dv, kappa=settings.initial_aerosol_kappa, r_dry=r_dry
        )
        self.particulator = builder.build(
            attributes={
                k: np.pad(
                    array=v,
                    pad_width=(0, settings.n_sd_seeding),
                    mode="constant",
                    constant_values=np.nan if k == "multiplicity" else 0,
                )
                for k, v in attributes.items()
            },
            products=(
                products.SuperDropletCountPerGridbox(name="sd_count"),
                products.Time(),
            ),
        )
        self.n_steps = int(settings.t_max // settings.timestep)

    def run(self):
        output = {
            "attributes": {"water mass": []},
            "products": {"sd_count": [], "time": []},
        }
        for step in range(self.n_steps + 1):
            if step != 0:
                self.particulator.run(steps=1)
            for key, attr in output["attributes"].items():
                data = self.particulator.attributes[key].to_ndarray(raw=True)
                data[data == 0] = np.nan
                attr.append(data)
            for key, prod in output["products"].items():
                prod.append(float(self.particulator.products[key].get()))
        for out in ("attributes", "products"):
            for key, val in output[out].items():
                output[out][key] = np.array(val)
        return output
