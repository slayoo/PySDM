from PySDM.attributes.physics.dry_volume import (DryVolumeOrganic, DryVolumeInorganic,
                                                 DryVolume, DryVolumeInorganicDynamic,
                                                 OrganicFraction)
from PySDM.attributes.physics.hygroscopicity import Kappa, KappaTimesDryVolume
from PySDM.attributes.physics import (Multiplicities, Volume, DryVolumeDynamic, DryVolumeStatic, Radius, DryRadius,
                                      TerminalVelocity, Temperature, Heat, CriticalVolume)
from PySDM.attributes.ice import FreezingTemperature, NucleationSites
from PySDM.attributes.numerics import CellID, CellOrigin, PositionInCell
from PySDM.attributes.chemistry import MoleAmount, Concentration, pH, HydrogenIonConcentration
from PySDM.physics.aqueous_chemistry.support import AQUEOUS_COMPOUNDS
from functools import partial

attributes = {
    'n': lambda _: Multiplicities,
    'volume': lambda _: Volume,
    'dry volume organic': lambda _: DryVolumeOrganic,
    'dry volume inorganic': lambda dynamics:
        DryVolumeInorganicDynamic if 'AqueousChemistry' in dynamics else DryVolumeInorganic,
    'dry volume': lambda _: DryVolume,
    'dry volume organic fraction': lambda _: OrganicFraction,
    'kappa times dry volume': lambda _: KappaTimesDryVolume,
    'kappa': lambda _: Kappa,
    'radius': lambda _: Radius,
    'dry radius': lambda _: DryRadius,
    'terminal velocity': lambda _: TerminalVelocity,
    'cell id': lambda _: CellID,
    'cell origin': lambda _: CellOrigin,
    'position in cell': lambda _: PositionInCell,
    'temperature': lambda _: Temperature,
    'heat': lambda _: Heat,
    'critical volume': lambda _: CriticalVolume,
    **{"moles_" + compound: partial(lambda _, c: MoleAmount(c), c=compound)
       for compound in AQUEOUS_COMPOUNDS.keys()},
    **{"conc_" + compound: partial(lambda _, c: Concentration(c), c=compound)
       for compound in AQUEOUS_COMPOUNDS.keys()},
    'pH': lambda _: pH,
    'conc_H': lambda _: HydrogenIonConcentration,
    'freezing temperature': lambda _: FreezingTemperature,
    'nucleation sites': lambda _: NucleationSites
}


def get_class(name, dynamics):
    return attributes[name](dynamics)
