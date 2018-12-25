from collections import namedtuple
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

from materials.gear_materials import SS2506

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def martensite_fraction(carbon, temperature, austenite_fraction=None):
    temperature = temperature + 273.15
    ms = 706.05 - 31745*carbon
    a = 4.8405e-2 - 4.3710*carbon
    f = 0*temperature
    f[temperature < ms] = 1-np.exp(-a*(ms-temperature[temperature < ms]))
    if austenite_fraction is None:
        austenite_fraction = f*0 + 1.

    return f*austenite_fraction


def expansion_martensite(temperature, carbon):
    temperature = temperature + 273.15
    return temperature*(1.6369e-5 - 2.1344e-3*carbon) - 6.12e-3 + 1.05*carbon


def expansion_austenite(temperature, carbon):
    temperature = temperature + 273.15
    return temperature*2.4e-5 - 0.017961 + 0.33041*carbon


def volume_expansion(temperature, carbon, martensite, austenite, material=SS2506):
    # return expansion_martensite(temperature, carbon)*martensite + expansion_austenite(temperature, carbon)*austenite
    e = martensite*material.transformation_strain.Martensite(temperature, carbon)
    e += austenite*material.transformation_strain.Austenite(temperature, carbon)
    return e


if __name__ == '__main__':
    Simulation = namedtuple('Simulation', ['carbon', 'color'])
    simulations = [Simulation(carbon=0.002, color='k'),
                   Simulation(carbon=0.0036, color='b'),
                   Simulation(carbon=0.0052, color='m'),
                   Simulation(carbon=0.0065, color='r'),
                   Simulation(carbon=0.008, color='k')]
    for simulation in simulations:
        c = simulation.carbon
        t = np.linspace(300, 860 + 273.15, 1000) - 273.15
        f_martensite = martensite_fraction(c, t)
        f_austenite = 1 - f_martensite
        strain = volume_expansion(t, c, f_martensite, f_austenite)
        plt.plot(t+273.15, strain, simulation.color, lw=2)

    jmat_data = np.genfromtxt('SS2506_data/jmat_pro_0_8_carbon.csv', delimiter=',', skip_header=1)
    t = jmat_data[:, 0]
    strain = jmat_data[:, 11]/100 + strain[-1]

    plt.plot(t+273.15, strain)

    plt.show()
