from collections import namedtuple

import numpy as np
from scipy.optimize import fmin

import matplotlib
import matplotlib.pyplot as plt

from materials.gear_materials import SS2506

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def expansion_martensite(par, c, t):
    m1, m2, m3, m4, m5, m6, m7, m8 = par
    # m6 = 0
    # m7 = 0
    # m8 = 0
    return m1 + m2*c + m3*c**2 + m4*t + m5*c*t + m6*t**2 + m7*c*t**2 + m8*t**3


def heat_expanion_martensite(par, c, t):
    m1, m2, m3, m4, m5, m6, m7, m8 = par
    # m6 = 0
    # m7 = 0
    # m8 = 0
    return m4 + m5*c + 2*m6*t + 2*m7*c*t + 3*m8*t**2


def fraction_martensite(par, t, c):
    a = np.interp(c, np.array([0.2, 0.5, 0.8]), np.array([par[0], par[1], 0.016]))
    ms_temp = SS2506.ms_temperature(c / 100) - 273.15
    martensite = 0*t
    martensite[t < ms_temp] = 1 - np.exp(-a*(ms_temp - t[t < ms_temp]))
    return martensite


def transformation_strain(par, c, t):
    martensite = fraction_martensite(par, t, c)
    austenite = 1 - martensite
    expansion_austenite = SS2506.transformation_strain.Austenite(t, c/100)
    return austenite*expansion_austenite + martensite*expansion_martensite(par[2:], c, t)


def residual(par, *data):
    r = 0
    for data_set in data[0]:
        exp, t, e = data_set
        ms_temp = SS2506.ms_temperature(exp.carbon/100) - 273.15
        e = e[t < ms_temp]
        t = t[t < ms_temp]
        model_e = transformation_strain(par, exp.carbon, t)
        r += np.sum((e - model_e)**2)
    return r


if __name__ == '__main__':
    Experiment = namedtuple('Experiment', ['carbon', 'color'])
    experiments = [Experiment(carbon=0.2, color='k'),
                   Experiment(carbon=0.36, color='b'),
                   Experiment(carbon=0.52, color='m'),
                   Experiment(carbon=0.65, color='r')]

    data_sets = []

    for experiment in experiments:
        exp_data = np.genfromtxt('data_tehler/expansion_' + str(experiment.carbon).replace('.', '_'), delimiter=',')
        temp = exp_data[:, 0] - 273.15
        strain = exp_data[:, 1] / 10000
        plt.figure(0)
        plt.plot(temp, strain, experiment.color, lw=2)

        temperature = np.linspace(temp[-1], temp[0], 1000)
        plt.plot(temperature, SS2506.transformation_strain.Austenite(temperature, experiment.carbon/100),
                 ':' + experiment.color)

        ms = SS2506.ms_temperature(experiment.carbon/100) - 273.15
        plt.plot(ms, SS2506.transformation_strain.Austenite(ms, experiment.carbon / 100),
                 'x' + experiment.color, ms=12, mew=2)

        data_sets.append((experiment, temp, strain))

    parameters = fmin(residual,
                      [0.03, 0.01,
                       -0.009882, -0.0003061, 0.01430, 1.3e-5, -4.3e-6, 2.9e-9, 1.4e-9, 1.091e-12],
                      (data_sets,), maxiter=1e6, maxfun=1e6)

    temperature = np.linspace(0, 1000)
    experiments.append(Experiment(carbon=0.8, color='y'))
    for i, experiment in enumerate(experiments):
        strain = transformation_strain(parameters, experiment.carbon, temperature)
        plt.figure(0)
        plt.plot(temperature, strain, '--' + experiment.color, lw=2)

        plt.figure(1)
        ms = SS2506.ms_temperature(experiment.carbon / 100) - 273.15
        mart = fraction_martensite(parameters, temperature, experiment.carbon)
        plt.plot(temperature, mart, experiment.color, lw=2)

    plt.figure(2)
    carbon = np.linspace(0, 1.2, 100)
    for temperature in [0, 200, 400]:
        plt.plot(carbon, heat_expanion_martensite(parameters[2:], carbon, temperature))

    for carbon in [0.2, 0.5, 0.8]:
        print '-------- Carbon,', carbon, '% -----------------'
        print "\tMs temperature:\t", SS2506.ms_temperature(carbon/100) - 273.15
        print "\tMobility:\t\t", np.interp(carbon, [0.2, 0.5, 0.8], np.array([parameters[0], parameters[1], 0.016]))

    print "Expansion parameters of Martensite is"
    print parameters[2:]
    plt.show()
