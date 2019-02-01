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

        self.composition = {'C': 0.23, 'Si': 0.2, 'Mn': 0.97, 'P': 0.01, 'S': 0.033, 'Cr':  0.6, 'Ni': 0.36, 'Mo': 0.7,
                            'Cu': 0.16, 'Al': 0.27}

    @staticmethod
    def findley_k(steel_properties):
        return 0.017 + 8.27E-4*steel_properties.HV

    def weibull_sw(self, steel_properties):
        return self.sw_par[0] + self.sw_par[1]*steel_properties.HV

    def weibull_m(self, steel_properties):
        return self.m_par[0]/steel_properties.HV**2

    # Phase transformation data
    def _trans_strain_martensite(self, temperature, carbon):
        temperature = temperature + 273.15
        t, c = np.meshgrid(temperature, carbon)
        e = t*(self._thermal_exp_martensite(temperature-273.15, carbon)) - 6.12e-3 + 1.05*c
        return np.squeeze(e)

    @staticmethod
    def _thermal_exp_martensite(temperature, carbon):
        temperature = temperature + 273.15
        _, c = np.meshgrid(temperature, carbon)
        a = 1.3e-5*(1-c/0.01)
        return np.squeeze(a)

    @staticmethod
    def _trans_strain_austenite(temperature, carbon):
        temperature = temperature + 273.15
        t, c = np.meshgrid(temperature, carbon)
        e = t*2.4e-5 - 0.017961 + 0.33041*c
        return np.squeeze(e)

    @staticmethod
    def _thermal_exp_austenite(temperature, carbon):
        temperature = temperature + 273.15
        t, c = np.meshgrid(temperature, carbon)
        a = 2.4e-5 + 0*t
        return np.squeeze(a)

    @staticmethod
    def _trans_strain_fp(temperature, carbon):
        temperature = temperature + 273.15
        t, c = np.meshgrid(temperature, carbon)
        e = 2.2520e-9*t**2 + 1.1643e-5*t - 3.6923e-3
        return np.squeeze(e)

    @staticmethod
    def _thermal_exp_fp(temperature, carbon):
        temperature = temperature + 273.15
        t, c = np.meshgrid(temperature, carbon)
        a = 2*2.2520e-9*t + 1.1643e-5
        return np.squeeze(a)

    def _trans_strain_bainite(self, temperature, carbon):
        _, c = np.meshgrid(temperature, carbon)
        e = self._trans_strain_fp(temperature, carbon) - 1.3315e-3 + 0.10908*c
        return np.squeeze(e)

    def _thermal_exp_bainite(self, temperature, carbon):
        a = self._thermal_exp_fp(temperature, carbon)
        return np.squeeze(a)

    @staticmethod
    def ms_temperature(carbon):
        return 706.05 - 31745 * carbon

    def martensite_fraction(self, temperature, carbon, austenite_fraction=None):
        temperature = temperature + 273.15
        t, c = np.meshgrid(temperature, carbon)
        if isinstance(carbon, float):
            carbon = np.array([carbon])
        martensite_start_temp = self.ms_temperature(carbon)
        # a = 4.8405e-2 - 4.3710*carbon
        a = 0.05344308817192316*np.exp(-144.08873331961297*carbon)
        f = 0 * t
        for i, ms in enumerate(martensite_start_temp):
            f[i, temperature < ms] = 1-np.exp(-a[i]*(ms-temperature[temperature < ms]))
        if austenite_fraction is None:
            austenite_fraction = 0*f + 1.
        return np.squeeze(f * austenite_fraction)


# SS2506 = SS2506MaterialTemplate(swa=138, swb=0.71, mb=11.06e6)
SS2506 = SS2506MaterialTemplate(swa=378, swb=0.175, mb=6.15e6)

if __name__ == '__main__':
    # Testing the transformation functions
    # carb = np.linspace(0.002, 0.0012, 10)
    # temp = np.linspace(0, 1000, 100)
    carb = 0.004
    temp = 300

    for trans_strain_func in SS2506.transformation_strain:
        print trans_strain_func, trans_strain_func(temp, carb)

    carb = np.linspace(0.002, 0.01, 10)
    temp = np.linspace(0, 1000, 100)
    SS2506.martensite_fraction(temp, carb)

    print SS2506.transformation_strain.Martensite(0, 0)
