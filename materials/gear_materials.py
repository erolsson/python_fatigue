from collections import namedtuple
import numpy as np

SteelData = namedtuple('Steel_data', ['HV'])


class SS2506MaterialTemplate:
    def __init__(self, swa, swb, mb):
        self.ne = np.log(1e5)
        self.ns = np.log(0.1)
        self.b = 5.
        self.sw_par = [swa, swb]
        self.m_par = [mb]

    @staticmethod
    def findley_k(steel_properties):
        return 0.017 + 8.27E-4*steel_properties.HV

    def weibull_sw(self, steel_properties):
        return self.sw_par[0] + self.sw_par[1]*steel_properties.HV

    def weibull_m(self, steel_properties):
        return self.m_par[0]/steel_properties.HV**2


SS2506 = SS2506MaterialTemplate(swa=138, swb=0.71, mb=11.06e6)
