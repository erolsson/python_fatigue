from collections import namedtuple

import numpy as np

from weakest_link.integration_methods import gauss_integration_3d
from weakest_link.hazard_functions import weibull

from materials.gear_materials import SS2506

FEM_data = namedtuple('FEM_data', ['stress', 'steel_data', 'nodal_positions'])


class WeakestLinkEvaluatorGear:
    def __init__(self, data_volume, data_area, size_factor=1):
        self.volume_data = data_volume
        self.area_data = data_area
        self.size_factor = size_factor

    def _calculate_pf_volume(self, cycles, hazard_function, material, haiback):
        if cycles and haiback:
            f = hazard_function.haiback(self.volume_data.stress, cycles, self.volume_data.steel_data, material)
        elif cycles:
            f = hazard_function.fatigue_life(self.volume_data.stress, cycles, self.volume_data.steel_data, material)
        else:
            f = hazard_function.fatigue_limit(self.volume_data.stress, self.volume_data.steel_data, material)
        integral = gauss_integration_3d(f, self.volume_data.nodal_positions)
        pf_subvol = (1-np.exp(-integral))
        return 1 - (1-pf_subvol)**self.size_factor

    def calculate_pf(self, cycles=None, hazard_function=weibull, material=SS2506, haiback=False):
        pf_vol = self._calculate_pf_volume(cycles, hazard_function, material, haiback)
        pf_area = 0
        return 1-(1-pf_vol)*(1-pf_area)

    def calculate_life_time(self, pf, hazard_function=weibull, material=SS2506, haiback=False):
        def func(life):
            pf_life = self.calculate_pf(cycles=np.exp(life), hazard_function=hazard_function, material=material,
                                        haiback=haiback)
            if np.isfinite(pf_life) and pf_life >= 0:
                return pf_life - pf
            return 1. - pf

        if not haiback:
            pf_limit = self.calculate_pf(cycles=None, hazard_function=hazard_function,
                                         material=material)
            f1 = pf_limit
            if pf > f1:
                return float("NaN")

        if haiback:
            n2 = np.log(1e8)
        else:
            n2 = material.ne
        n1 = material.ns

        cycles = (n1 + n2) / 2
        while abs(n1 - n2) / 2 > 1E-3:
            f = func(cycles)
            if f == 0:
                return np.exp(cycles)
            elif func(n1) * f < 0:
                n2 = cycles
            else:
                n1 = cycles
            cycles = (n1 + n2) / 2
        return np.exp(cycles)
