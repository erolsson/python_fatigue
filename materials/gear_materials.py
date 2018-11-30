from collections import namedtuple
import numpy as np

SteelData = namedtuple('Steel_data', ['HV'])
PhaseData = namedtuple('PhaseData', ['Martensite', 'Austenite', 'Bainite', 'Pearlite', 'Ferrite'])


class SS2506MaterialTemplate:
    def __init__(self, swa, swb, mb):
        self.ne = np.log(1e5)
        self.ns = np.log(0.1)
        self.b = 5.
        self.sw_par = [swa, swb]
        self.m_par = [mb]

        self.name = 'SS2506'

        self.transformation_strain = PhaseData(Martensite=self._trans_strain_martensite,
                                               Austenite=self._trans_strain_austenite,
                                               Bainite=self._trans_strain_bainite,
                                               Pearlite=self._trans_strain_fp,
                                               Ferrite=self._trans_strain_fp)

        self.thermal_expansion = PhaseData(Martensite=self._thermal_exp_martensite,
                                           Austenite=self._thermal_exp_austenite,
                                           Bainite=self._thermal_exp_bainite,
                                           Pearlite=self._thermal_exp_fp,
                                           Ferrite=self._thermal_exp_fp)

    @staticmethod
    def findley_k(steel_properties):
        return 0.017 + 8.27E-4*steel_properties.HV

    def weibull_sw(self, steel_properties):
        return self.sw_par[0] + self.sw_par[1]*steel_properties.HV

    def weibull_m(self, steel_properties):
        return self.m_par[0]/steel_properties.HV**2

    # Phase transformation data
    @staticmethod
    def _trans_strain_martensite(temperature, carbon):
        return temperature*(1.6369e-5 - 2.1344e-3*carbon) - 6.12e-3 + 1.05*carbon

    @staticmethod
    def _thermal_exp_martensite(temperature, carbon):
        return 1.6369e-5 - 2.1344e-3*carbon

    @staticmethod
    def _trans_strain_austenite(temperature, carbon):
        return temperature*2.4e-5 - 0.017961 + 0.33041*carbon

    @staticmethod
    def _thermal_exp_austenite(temperature, carbon):
        return 2.4e-5 + 0*temperature

    @staticmethod
    def _trans_strain_fp(temperature, carbon):
        return 2.2520e-9*temperature**2 + 1.1643e-5*temperature - 3.6923e-3

    @staticmethod
    def _thermal_exp_fp(temperature, carbon):
        return 2*2.2520e-9*temperature + 1.1643e-5

    def _trans_strain_bainite(self, temperature, carbon):
        return self._thermal_exp_fp(temperature, carbon) - 1.3315e-3 + 0.10908*carbon

    def _thermal_exp_bainite(self, temperature, carbon):
        return self._thermal_exp_fp(temperature, carbon)


# SS2506 = SS2506MaterialTemplate(swa=138, swb=0.71, mb=11.06e6)
SS2506 = SS2506MaterialTemplate(swa=240, swb=0.482, mb=11.06e6)
