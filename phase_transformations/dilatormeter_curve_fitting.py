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
M20 = 0.2

ferrite = {0.2: 0.325, 0.36: 0.22, 0.52: 0., 0.65: 0., 0.8: 0.}


def expansion_martensite(par, c, t):
    m1, m2, m3, m4, m5 = par
    # m2 = 0.9e-5
    # m3 = 2.9e-9
    return m1 + m2*t + m3*t**2 + m4*c + m5*c**2


def heat_expanion_martensite(par, c, t):
    m1, m2, m3, m4, m5 = par
    return m2 + 2*m3*t


def fraction_martensite(par, t, c):
    # a = np.interp(c, np.array([0.2, 0.5, 0.8]), np.array([par[0], par[1], 0.016]))
    par = np.abs(par)
    a = np.interp(c, np.array([0.2, 0.5, 0.8]), par[0:3])
    ms_temp = np.interp(c, np.array([0.2, 0.5, 0.8]), par[3:6])
    a80 = -np.log(M20)/(ms_temp - 20)
    a = np.interp(c, np.array([0.2, 0.5, 0.8]), np.array([par[0], par[1], par[2]]))

    # ms_temp = SS2506.ms_temperature(c / 100) - 273.15
    martensite = 0*t

    martensite[t < ms_temp] = (1 - np.exp(-a*(ms_temp - t[t < ms_temp])))*(1-ferrite[c])
    return martensite


def transformation_strain(par, c, t):
    martensite = fraction_martensite(par, t, c)
    austenite = 1 - martensite - ferrite[c]
    expansion_austenite = SS2506.transformation_strain.Austenite(t, c/100)
    expansion_ferrite = SS2506.transformation_strain.Ferrite(t, c/100)
    return austenite*expansion_austenite + martensite*expansion_martensite(par[6:], c, t) + ferrite[c]*expansion_ferrite


def residual(par, *data):
    r = 0
    for data_set in data[0]:
        exp, t, e = data_set
        ms_temp = par
        ms_temp = np.interp(exp.carbon, [0.2, 0.5, 0.8], par[3:6])
        par[3] = 368.8
        e = e[t < ms_temp]
        t = t[t < ms_temp]
        t_interp = np.linspace(t[-1], ms_temp, 1000)
        e_interp = np.interp(t_interp, np.flip(t), np.flip(e))

        model_e = transformation_strain(par, exp.carbon, t_interp)
        r += np.sum((e_interp - model_e)**2)/(len(model_e))
    return r*1e9


def bainite_residual(par, *data):
    par[3] = 0
    a, b, c, d = par
    r = 0
    for data_set in data[0]:
        exp, t, e = data_set
        model_e = a + c*t + b*exp.carbon + d*exp.carbon*t
        r1 = np.sum((e - model_e)**2)/len(t)
        if exp.carbon < 0.25:
            r1 *= 10
        r += r1
    return r*1e9


def austenite_residual(par, *data):
    a, b, c = par
    r = 0
    for data_set in data[0]:
        exp, t, e = data_set
        model_e = a + c*t + b*exp.carbon
        r += np.sum((e - model_e) ** 2) / len(t)
    return r * 1e9


if __name__ == '__main__':
    Experiment = namedtuple('Experiment', ['carbon', 'color', 'included_martensite', 'included_bainite', 'mf'])
    experiments = [Experiment(carbon=0.2, color='k', included_martensite=True, included_bainite=True, mf=200),
                   Experiment(carbon=0.36, color='b', included_martensite=True, included_bainite=False, mf=90),
                   Experiment(carbon=0.52, color='m', included_martensite=True, included_bainite=False, mf=40),
                   Experiment(carbon=0.65, color='r', included_martensite=True, included_bainite=True, mf=20)]

    data_sets = []
    bainite_data_sets = []
    austenite_data_sets = []

    for experiment in experiments:
        exp_data = np.genfromtxt('data_tehler/expansion_' + str(experiment.carbon).replace('.', '_'), delimiter=',')
        temp = exp_data[:, 0] - 273.15
        e0 = SS2506.transformation_strain.Austenite(0, experiment.carbon/100)
        strain = exp_data[:, 1] / 10000
        plt.figure(0)
        label = 'Exp.' if experiment.carbon == 0.2 else None
        plt.plot(temp, strain, '-x' + experiment.color, lw=2, label=label)

        temperature = np.linspace(temp[-1], temp[0], 1000)
        plt.plot(temperature, SS2506.transformation_strain.Austenite(temperature, experiment.carbon/100),
                 ':' + experiment.color)

        plt.plot(temperature, SS2506.transformation_strain.Martensite(temperature, experiment.carbon/100),
                 ':' + experiment.color)

        plt.plot(temperature, SS2506.transformation_strain.Ferrite(temperature, experiment.carbon/100), '.-')

        if experiment.mf > temp[-1]:
            t_mf = np.linspace(temp[-1], experiment.mf, 100)
            mf_strain = np.interp(t_mf, np.flip(temp), np.flip(strain))

        if experiment.included_martensite:
            data_sets.append((experiment, temp, strain))
        austenite_data_sets.append((experiment, temp[temp > 600], strain[temp > 600]))

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
                      [0.04, 0.02, 0.015, 370, 274, 179,
                       -2e-3, 1.30e-5, 2.9e-9, 7e-3, 1E-05],
                      (data_sets,), maxiter=1e6, maxfun=1e6)

    bainite_parameters = fmin(bainite_residual, [-1.44e-3, 1.893e-3, 1.323e-5, 0.000000], (bainite_data_sets,))
    print bainite_parameters

    austenite_parameters = fmin(austenite_residual, [-0.01141, 0.0038, 2.4e-5], (austenite_data_sets,))
    print austenite_parameters

    experiments.append(Experiment(carbon=0.8, color='y', included_martensite=True, included_bainite=True, mf=-91))
    for i, experiment in enumerate(experiments):
        temperature = np.linspace(0, 1000, 1000)
        strain = transformation_strain(parameters, experiment.carbon, temperature)
        plt.figure(0)
        label = 'Model' if experiment.carbon == 0.2 else None
        plt.plot(temperature, strain, '--' + experiment.color, lw=2, label=label)
        austenite_strain = austenite_parameters[0] + austenite_parameters[1]*experiment.carbon + \
            austenite_parameters[2]*temperature
        plt.plot(temperature, austenite_strain, '--' + experiment.color, lw=2, label=label)

        plt.figure(1)
        # ms = SS2506.ms_temperature(experiment.carbon / 100) - 273.15
        mart = fraction_martensite(parameters, temperature, experiment.carbon)
        label = str(experiment.carbon) + r' wt. \%C'

        # label += '\nExtrapolated'
        plt.plot(temperature, mart, experiment.color, lw=2, label=label)

        plt.figure(3)
        temperature = np.linspace(0, 600, 1000)
        bainite_strain = bainite_parameters[0] + bainite_parameters[2]*temperature + \
            bainite_parameters[1]*experiment.carbon + bainite_parameters[3]*experiment.carbon*temperature

        plt.plot(temperature, bainite_strain, '--' + experiment.color, lw=2)

    print (expansion_martensite(parameters[6:], 0.8, 22) - (austenite_parameters[0] +
                                                            austenite_parameters[1]*0.8 + austenite_parameters[2]*22))*3
    a80 = -np.log(M20)/(parameters[5] - 20)
    t20 = np.array([parameters[5] + np.log(0.20)/parameters[2]])
    print "20 % Retained Austenite at", t20
    expan02 = expansion_martensite(parameters[6:], np.array([0.2]), np.array([t20])) - \
        transformation_strain(parameters, 0.2, np.array([1000]))
    expan08 = 0.8*expansion_martensite(parameters[6:], np.array([0.8]), np.array([t20])) + \
        0.2*SS2506.transformation_strain.Austenite(t20, 0.008) - \
        transformation_strain(parameters, 0.8, np.array([1000]))
    print "Difference in expansion is", expan08 - expan02

    plt.figure(0)
    plt.xlim(0, 800)
    plt.ylim(-0.005, 0.01)
    plt.xlabel(r'Temperature [ $\degree$C]')
    plt.ylabel(r'Strain [-]')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('dilatometer_sim.png')

    plt.figure(1)
    # plt.xlim(0, 200)
    plt.xlabel(r'Temperature [ $\degree$C]')
    plt.ylabel(r'Fraction Martensite [-]')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('martensite_transformation.png')

    for i, carbon in enumerate([0.2, 0.5, 0.8]):
        print '-------- Carbon,', carbon, '% -----------------'
        ms = parameters[i+3]
        print "\tMs temperature:\t", ms
        if carbon == 1.2:
            a = -np.log(M20)/(ms - 20)
        else:
            a = parameters[i]
        print "\tMobility:\t\t", a
    print "Expansion parameters of Martensite is"
    print parameters[6:]

    print "Expansion parameters of Bainite is"
    print bainite_parameters
    print "Expansion parameters for Austenite is"
    print austenite_parameters
    plt.show()
