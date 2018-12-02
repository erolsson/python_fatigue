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
        temperature += 273.15
        t, c = np.meshgrid(temperature, carbon)
        e = t*(1.6369e-5 - 2.1344e-3*c) - 6.12e-3 + 1.05*c
        return np.squeeze(e)

    @staticmethod
    def _thermal_exp_martensite(temperature, carbon):
        temperature += 273.15
        t, c = np.meshgrid(temperature, carbon)
        a = 1.6369e-5 - 2.1344e-3*c
        return np.squeeze(a)

    @staticmethod
    def _trans_strain_austenite(temperature, carbon):
        temperature += 273.15
        t, c = np.meshgrid(temperature, carbon)
        e = t*2.4e-5 - 0.017961 + 0.33041*c
        return np.squeeze(e)

    @staticmethod
    def _thermal_exp_austenite(temperature, carbon):
        temperature += 273.15
        t, c = np.meshgrid(temperature, carbon)
        a = 2.4e-5 + 0*t
        return np.squeeze(a)

    @staticmethod
    def _trans_strain_fp(temperature, carbon):
        temperature += 273.15
        t, c = np.meshgrid(temperature, carbon)
        e = 2.2520e-9*t**2 + 1.1643e-5*t - 3.6923e-3
        return np.squeeze(e)

    @staticmethod
    def _thermal_exp_fp(temperature, carbon):
        temperature += 273.15
        t, c = np.meshgrid(temperature, carbon)
        a = 2*2.2520e-9*t + 1.1643e-5
        return np.squeeze(a)

    def _trans_strain_bainite(self, temperature, carbon):
        _, c = np.meshgrid(temperature, carbon)
        e = self._thermal_exp_fp(temperature, carbon) - 1.3315e-3 + 0.10908*c
        return np.squeeze(e)

    def _thermal_exp_bainite(self, temperature, carbon):
        a = self._thermal_exp_fp(temperature, carbon)
        return np.squeeze(a)


# SS2506 = SS2506MaterialTemplate(swa=138, swb=0.71, mb=11.06e6)
SS2506 = SS2506MaterialTemplate(swa=240, swb=0.482, mb=11.06e6)

if __name__ == '__main__':
    # Testing the transformation functions
    # carb = np.linspace(0.002, 0.0012, 10)
    # temp = np.linspace(0, 1000, 100)
    carb = 0.004
    temp = 300

    for trans_strain_func in SS2506.transformation_strain:
        print trans_strain_func, trans_strain_func(temp, carb)
