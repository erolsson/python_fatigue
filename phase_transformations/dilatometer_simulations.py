import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def martensite_fraction(carbon, temperature, austenite_fraction=None):
    ms = 706.05 - 31745*carbon
    a = 4.8405e-2 - 4.3710*carbon
    f = 0*temperature
    f[temperature < ms] = 1-np.exp(-a*(ms-temperature[temperature < ms]))
    if austenite_fraction is None:
        austenite_fraction = f*0 + 1.

    return f*austenite_fraction


def expansion_martensite(temperature, carbon):
    return temperature*(1.6369e-5 - 2.1344e-3*carbon) - 6.12e-3 + 1.05*carbon


def expansion_austenite(temperature, carbon):
    return temperature*2.4e-5 - 0.017961 + 0.33041*carbon


def volume_expansion(temperature, carbon, martensite, austenite):
    return expansion_martensite(temperature, carbon)*martensite + expansion_austenite(temperature, carbon)*austenite


if __name__ == '__main__':
    c = 0.002
    t = np.linspace(1200, 300, 1000)
    f_martensite = martensite_fraction(c, t)
    f_austenite = 1 - f_martensite
    strain = volume_expansion(t, c, f_martensite, f_austenite)
    plt.plot(t, strain)
    plt.show()
