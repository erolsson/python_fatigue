from collections import namedtuple

import numpy as np

import matplotlib
import matplotlib.pyplot as plt

from scipy.optimize import fmin

from materials.gear_materials import SS2506

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}", r"\usepackage{gensymb}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


MartensiteData = namedtuple('MartensiteData', ['martensite', 'temperature', 'ferrite', 'ms', 'carbon'])
carbon_par_levels = [0.2, 0.5, 0.8]

m80 = 0.93


class Experiment:
    def __init__(self, carbon, color, cooling_rate, ms):
        self.carbon = carbon
        self.color = color
        self.cooling_rate = cooling_rate
        self.ms = ms

        exp_data = np.genfromtxt('data_tehler/expansion_' + str(self.carbon).replace('.', '_'), delimiter=',')
        exp_data = exp_data[np.argsort(exp_data[:, 0]), :]
        self.strain = exp_data[:, 1]/1e4
        self.temperature = exp_data[:, 0] - 273.15

        self.time = -(self.temperature - self.temperature[-1])/self.cooling_rate

        self.austenite_strain = SS2506.transformation_strain.Austenite(self.temperature, self.carbon/100)
        self.ferrite_strain = SS2506.transformation_strain.Ferrite(self.temperature, self.carbon/100)

        ferrite_idx = np.logical_and(self.temperature < 700, self.temperature > self.ms)

        self.ferrite = 0*self.strain
        if self.carbon < 0.5:
            self.ferrite[ferrite_idx] = ((self.strain[ferrite_idx] - self.austenite_strain[ferrite_idx])
                                         / (self.ferrite_strain[ferrite_idx] - self.austenite_strain[ferrite_idx]))

        self.ferrite[self.temperature < self.ms] = self.ferrite[np.where(ferrite_idx)[0][0]]
        self.strain_af = (1 - self.ferrite)*self.austenite_strain + self.ferrite*self.ferrite_strain

    def fraction_martensite(self, expansion_parameters):
        m_strain = martensite_strain(self.temperature, self.carbon, expansion_parameters)
        martensite = ((self.strain - self.austenite_strain
                       - self.ferrite[0]*(self.ferrite_strain - self.austenite_strain))
                      / (m_strain - self.austenite_strain))
        martensite[self.temperature > self.ms] = 0
        return martensite


def martensite_residual(par, *data):
    ms_par = data[1]
    expansion_par = data[2]
    residual = 0.
    for data_set in data[0]:
        ms_temp = np.interp(data_set.carbon, carbon_par_levels, ms_par)
        temperature = np.linspace(data_set.temperature[0], ms_temp, 100)
        martensite_exp = np.interp(temperature, data_set.temperature, data_set.fraction_martensite(expansion_par))
        ferrite = np.interp(temperature, data_set.temperature, data_set.ferrite)
        mart_calc = koistinen_marburger(temperature, data_set.carbon, ms_par, par, ferrite)
        residual += np.sum((mart_calc - martensite_exp)**2)
    return residual


def ms_temperature_residual(par, *data):
    ms = np.zeros(len(data[0]))
    carbon = np.zeros(len(data[0]))
    for i, data_set in enumerate(data[0]):
        ms[i] = data_set.ms
        carbon[i] = data_set.carbon
    ms_calc = np.interp(carbon, carbon_par_levels, par)
    return np.sum((1 - ms/ms_calc)**2)


def koistinen_marburger(temperature, carbon, ms_par, km_par, other_phases=None):
    martensite = 0*temperature
    if other_phases is None:
        other_phases = 0*temperature
    km_par[-1] = -np.log(1 - m80)/(ms_par[-1] - 22.)
    km_par = [0.021150422801106586,  0.01884986437450156, 0.018174240914351353]
    ms = np.interp(carbon, carbon_par_levels, ms_par)
    k = np.interp(carbon, carbon_par_levels, km_par)
    martensite[temperature < ms] = ((1 - np.exp(-k*(ms - temperature[temperature < ms])))
                                    * (1 - other_phases[temperature < ms]))
    return martensite


def expansion_residual(par, *data):
    residual = 0.
    for data_set in data[0]:
        if data_set.carbon < 0.6:
            temperature = np.linspace(data_set.temperature[0], 50, 10)
            strain = np.interp(temperature, data_set.temperature, data_set.strain)
            calc_strain = (martensite_strain(temperature, data_set.carbon, par)*(1 - np.max(data_set.ferrite))
                           + data_set.ferrite[0]*SS2506.transformation_strain.Ferrite(temperature, data_set.carbon))
            residual += np.sum((1 - calc_strain/strain)**2)
    return residual


def martensite_strain(t, carbon, par):
    return par[0] + 1.20e-5*t + 2.9e-9*t**2 + par[1]*carbon*(1 + 0*t) + par[2]*carbon**2*(1 + 0*t)


def main():
    experiments = [Experiment(carbon=0.2, color='k', cooling_rate=100, ms=639 - 273.15),
                   Experiment(carbon=0.36, color='b', cooling_rate=50, ms=306),
                   Experiment(carbon=0.52, color='m', cooling_rate=30, ms=270),
                   Experiment(carbon=0.65, color='r', cooling_rate=30, ms=220)]
    expansion_par = fmin(expansion_residual, [-0.0005, 0.01, 0.0001], args=(experiments,))
    ms_temperature_parameters = fmin(ms_temperature_residual, [220, 220, 220], args=(experiments, ))
    km_parameters = fmin(martensite_residual, [0.04, 0.02, 0.01],
                         args=(experiments, ms_temperature_parameters, expansion_par))

    km_parameters[-1] = -np.log(1 - m80)/(ms_temperature_parameters[-1] - 22.)
    print km_parameters
    print expansion_par
    for experiment in experiments:
        plt.figure(0)
        plt.plot(experiment.temperature, experiment.strain, '-x' + experiment.color)

        plt.figure(1)
        plt.plot(experiment.time, experiment.strain, '-x' + experiment.color)

        plt.figure(2)
        plt.plot(experiment.temperature, experiment.ferrite, experiment.color)

        plt.figure(0)
        plt.plot(experiment.temperature, experiment.strain_af, '--' + experiment.color)

        plt.figure(1)
        plt.plot(experiment.time, experiment.strain_af, '--' + experiment.color)

        m_strain = martensite_strain(experiment.temperature, experiment.carbon, expansion_par)
        plt.figure(0)
        plt.plot(experiment.temperature, m_strain, ':' + experiment.color)

        plt.figure(3)
        plt.plot(experiment.temperature, experiment.fraction_martensite(expansion_par), experiment.color, lw=2)
        plt.xlim(0, 400)
        plt.plot(experiment.temperature,
                 koistinen_marburger(experiment.temperature, experiment.carbon, ms_temperature_parameters,
                                     km_parameters, experiment.ferrite))

        plt.figure(4)
        plt.plot(experiment.temperature, experiment.strain, experiment.color, lw=2)
        martensite = koistinen_marburger(experiment.temperature, experiment.carbon, ms_temperature_parameters,
                                         km_parameters, other_phases=experiment.ferrite)
        austenite = 1 - martensite - experiment.ferrite
        strain = (austenite*experiment.austenite_strain + experiment.ferrite*experiment.ferrite_strain
                  + martensite*martensite_strain(experiment.temperature, experiment.carbon, expansion_par))
        plt.plot(experiment.temperature, strain, '--' + experiment.color, lw=2)

    temperature = np.linspace(20, 1000, 1000)
    plt.figure(3)
    martensite = koistinen_marburger(temperature, 0.8, ms_temperature_parameters, km_parameters)
    plt.plot(temperature, martensite)

    plt.figure(4)
    austenite = 1 - martensite
    strain = (austenite*SS2506.transformation_strain.Austenite(temperature, 0.008) +
              + martensite*martensite_strain(temperature, 0.8, expansion_par))
    plt.plot(temperature, strain, '--', lw=2)

    plt.figure(3)
    martensite = koistinen_marburger(temperature, 0.2, ms_temperature_parameters, km_parameters)
    plt.plot(temperature, martensite)

    plt.figure(4)
    austenite = 1 - martensite
    strain = (austenite*SS2506.transformation_strain.Austenite(temperature, 0.002) +
              + martensite*martensite_strain(temperature, 0.2, expansion_par))
    plt.plot(temperature, strain, '--', lw=2)

    plt.show()


if __name__ == '__main__':
    main()
