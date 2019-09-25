import numpy as np

import matplotlib
import matplotlib.pyplot as plt

from materials.gear_materials import SS2506

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}", r"\usepackage{gensymb}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

atomic_masses = {'C': 12.0107, 'Si': 28.0855, 'Mn': 54.938, 'P': 30.9738, 'S': 32.065, 'Cr': 51.9961,
                 'Ni': 58.6934, 'Mo': 95.94, 'Cu': 63.546, 'Al': 26.9815}


def calc_atomic_pct(c):
    nc = c/atomic_masses['C']

    fraction = 0
    for _, value in SS2506.composition.iteritems():
        fraction += value
    fe = 1 - fraction/100
    nf = fe/55.845

    number = 0
    for element, value in SS2506.composition.iteritems():
        number += value/atomic_masses[element]/100

    return nc/(nf + number)


def heat_expansion_martensite(c):
    cm = calc_atomic_pct(c)
    return (14.9 - 1.9*cm*100)*1e-6


def heat_expansion_austenite(c):
    cm = calc_atomic_pct(c)
    return (24.9 - 0.5*cm*100)*1e-6


carbon = np.linspace(0.2, 0.8, 100)/100
a = heat_expansion_martensite(carbon)
print np.polyfit(carbon, a, 1)
plt.plot(carbon, a)

plt.figure(3)
carbon = np.linspace(0.2, 0.8, 100)/100
a = heat_expansion_austenite(carbon)
print np.polyfit(carbon, a, 1)
plt.plot(carbon, a)
print calc_atomic_pct(0.06)
plt.show()
