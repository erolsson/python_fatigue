from collections import namedtuple

import numpy as np

from materials.gear_materials import SS2506


def dilatormeter_experiment(temperature, carbon, material=SS2506):
    f_martensite = SS2506.martensite_fraction(temperature, carbon)
    f_austenite = 1 - f_martensite
    e = f_martensite*material.transformation_strain.Martensite(temperature, carbon)
    e += f_austenite*material.transformation_strain.Austenite(temperature, carbon)
    return e


if __name__ == '__main__':
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.style.use('classic')
    plt.rc('text', usetex=True)
    plt.rc('font', serif='Computer Modern Roman')
    plt.rcParams.update({'font.size': 20})
    plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
    plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                      'monospace': ['Computer Modern Typewriter']})

    Simulation = namedtuple('Simulation', ['carbon', 'color'])
    simulations = [Simulation(carbon=0.002, color='k'),
                   Simulation(carbon=0.0036, color='b'),
                   Simulation(carbon=0.0052, color='m'),
                   Simulation(carbon=0.0065, color='r'),
                   Simulation(carbon=0.008, color='y')]
    t = np.linspace(300, 1200, 1000) - 273.15
    for simulation in simulations:
        c = simulation.carbon
        strain = dilatormeter_experiment(t, c)
        plt.plot(t + 273.15, strain, simulation.color, lw=2)
    plt.show()
