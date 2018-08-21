from collections import namedtuple
import numpy as np

SteelData = namedtuple('Steel_data', ['HV'])


class _SS2506Material:
    def __init__(self):
        self.ne = np.log(1e5)
        self.ns = np.log(0.1)
        self.b = 5.

    @staticmethod
    def findley_k(steel_properties):
        return 0.017 + 8.27E-4*steel_properties.HV

    @staticmethod
    def weibull_sw(steel_properties, a=138, b=0.71):
        return a + b*steel_properties.HV

    @staticmethod
    def weibull_m(steel_properties, b=11.06e6):
        return b/steel_properties.HV**2


SS2506 = _SS2506Material()
