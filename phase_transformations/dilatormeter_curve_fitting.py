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
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}", r"\usepackage{gensymb}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def expansion_martensite(par, c, t):
    par[5:] = 0
    par[4] = (4.559703619264866e-06 - 1.2678425108258802e-05)/(0.52 - 0.2)
    par[3] = 1.2678425e-5 - par[4] * 0.2

    m1, m2, m3, m4, m5, m6, m7, m8 = par
    return m1 + m2*c + m3*c**2 + m4*t + m5*c*t + m6*t**2 + m7*c*t**2 + m8*t**3


def heat_expanion_martensite(par, c, t):
    par[5:] = 0
    par[4] = (4.559703619264866e-06 - 1.2678425108258802e-05)/(0.52 - 0.2)
    par[3] = 1.2678425e-5 - par[4]*0.2

    m1, m2, m3, m4, m5, m6, m7, m8 = par
    return m4 + m5*c + 2*m6*t + 2*m7*c*t + 3*m8*t**2


def fraction_martensite(par, t, c):
    # a = np.interp(c, np.array([0.2, 0.5, 0.8]), np.array([par[0], par[1], 0.016]))
    par = np.abs(par)
    # par[0] = 0.05
    par[2] = 0.017
    a = np.interp(c, np.array([0.2, 0.5, 0.8]), par[0:3])
    ms_temp = SS2506.ms_temperature(c / 100) - 273.15
    martensite = 0*t

    martensite[t < ms_temp] = 1 - np.exp(-a*(ms_temp - t[t < ms_temp]))
    return martensite


def transformation_strain(par, c, t):
    martensite = fraction_martensite(par, t, c)
    austenite = 1 - martensite
    expansion_austenite = SS2506.transformation_strain.Austenite(t, c/100)
    return austenite*expansion_austenite + martensite*expansion_martensite(par[3:], c, t)


def residual(par, *data):
    r = 0
    par[2] = 0.017
    for data_set in data[0]:
        exp, t, e = data_set
        ms_temp = SS2506.ms_temperature(exp.carbon/100) - 273.15
        ms_temp*0.75
        e = e[t < ms_temp]
        t = t[t < ms_temp]
        t_interp = np.linspace(t[-1], ms_temp, 1000)
        e_interp = np.interp(t_interp, np.flip(t), np.flip(e))

        model_e = transformation_strain(par, exp.carbon, t_interp)
        r += np.sum((e_interp - model_e)**2)
    return r


def bainite_residual(par, *data):
    par[3] = 0
    a, b, c, d = par
    r = 0
    for data_set in data[0]:
        exp, t, e = data_set
        model_e = a + b*t + c*exp.carbon + d*exp.carbon*t
        r += np.sum((e - model_e)**2)/len(t)
    return r*1e9


if __name__ == '__main__':
    Experiment = namedtuple('Experiment', ['carbon', 'color', 'included_martensite', 'included_bainite', 'mf'])
    experiments = [Experiment(carbon=0.2, color='k', included_martensite=True, included_bainite=True, mf=200),
                   Experiment(carbon=0.36, color='b', included_martensite=True, included_bainite=False, mf=90),
                   Experiment(carbon=0.52, color='m', included_martensite=True, included_bainite=False, mf=40),
                   Experiment(carbon=0.65, color='r', included_martensite=True, included_bainite=True, mf=-20)]

    data_sets = []
    bainite_data_sets = []

    for experiment in experiments:
        exp_data = np.genfromtxt('data_tehler/expansion_' + str(experiment.carbon).replace('.', '_'), delimiter=',')
        temp = exp_data[:, 0] - 273.15
        strain = exp_data[:, 1] / 10000
        plt.figure(0)
        label = 'Exp.' if experiment.carbon == 0.2 else None
        plt.plot(temp, strain, '-x' + experiment.color, lw=2, label=label)

        temperature = np.linspace(temp[-1], temp[0], 1000)
        plt.plot(temperature, SS2506.transformation_strain.Austenite(temperature, experiment.carbon/100),
                 ':' + experiment.color)

        if experiment.mf > temp[-1]:
            mf_strain = np.interp(experiment.mf, np.flip(temp), np.flip(strain))
            print (mf_strain - strain[-1])/(experiment.mf - temp[-1])
        ms = SS2506.ms_temperature(experiment.carbon/100) - 273.15
        plt.plot(ms, SS2506.transformation_strain.Austenite(ms, experiment.carbon / 100),
                 'x' + experiment.color, ms=12, mew=2)

        if experiment.included_martensite:
            data_sets.append((experiment, temp, strain))

        plt.figure(3)
        exp_data = np.genfromtxt('data_tehler/bainite_' + str(experiment.carbon).replace('.', '_'), delimiter=',')
        temp = exp_data[:, 0] - 273.15
        strain = exp_data[:, 1] + SS2506.transformation_strain.Austenite(temp, experiment.carbon/100)
        plt.plot(temp, strain, '-x' + experiment.color, lw=2)

        plt.plot(temperature, SS2506.transformation_strain.Bainite(temperature, experiment.carbon/100),
                 ':' + experiment.color, lw=2)

        if experiment.included_bainite:
            bainite_data_sets.append([experiment, temp, strain])

    parameters = fmin(residual,
                      [0.04, 0.02, 0.015,
                       -0.009882, -0.01, 0.01, 1.3e-5, -4.3e-6, 2.9e-9, 1.4e-9, 1.091e-12],
                      (data_sets,), maxiter=1e6, maxfun=1e6)

    bainite_parameters = fmin(bainite_residual, [-2e-5, 4e-6, 2e-5, 1e-5], (bainite_data_sets,))
    print bainite_parameters

    experiments.append(Experiment(carbon=0.8, color='y', included_martensite=True, included_bainite=True, mf=-91))
    for i, experiment in enumerate(experiments):
        temperature = np.linspace(0, 400, 1000)
        strain = transformation_strain(parameters, experiment.carbon, temperature)
        plt.figure(0)
        label = 'Model' if experiment.carbon == 0.2 else None
        plt.plot(temperature, strain, '--' + experiment.color, lw=2, label=label)

        plt.figure(1)
        ms = SS2506.ms_temperature(experiment.carbon / 100) - 273.15
        mart = fraction_martensite(parameters, temperature, experiment.carbon)
        label = str(experiment.carbon) + r' wt. \%C'
        if experiment.carbon > 0.7:
            label += '\nExtrapolated'
        plt.plot(temperature, mart, experiment.color, lw=2, label=label)

        plt.figure(3)
        temperature = np.linspace(0, 600, 1000)
        bainite_strain = bainite_parameters[0] + bainite_parameters[1]*temperature + \
            bainite_parameters[2]*experiment.carbon + bainite_parameters[3]*experiment.carbon*temperature

        plt.plot(temperature, bainite_strain, '--' + experiment.color, lw=2)

    plt.figure(0)
    plt.xlim(0, 800)
    plt.ylim(-0.005, 0.01)
    plt.xlabel(r'Temperature [ $\degree$C]')
    plt.ylabel(r'Strain [-]')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('dilatometer_sim.png')

    plt.figure(1)
    plt.xlim(0, 400)
    plt.xlabel(r'Temperature [ $\degree$C]')
    plt.ylabel(r'Fraction Martensite [-]')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('martensite_transformation.png')

    plt.figure(2)
    carbon = np.linspace(0, 1.2, 100)
    for temperature in [20., 200.]:
        plt.plot(carbon, heat_expanion_martensite(parameters[3:], carbon, temperature))

    for carbon in [0.2, 0.5, 0.8]:
        print '-------- Carbon,', carbon, '% -----------------'
        print "\tMs temperature:\t", SS2506.ms_temperature(carbon/100) - 273.15
        print "\tMobility:\t\t", np.interp(carbon, [0.2, 0.5, 0.8], parameters[0:3])

    print "Expansion parameters of Martensite is"
    print parameters[3:]
    plt.show()
