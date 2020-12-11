from collections import namedtuple
import os
import pickle

import numpy as np

from scipy.optimize import fmin

import matplotlib.pyplot as plt
import matplotlib.style

from materials.hardess_convertion_functions import HRC2HV
from materials.hardess_convertion_functions import HV2HRC

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

pickle_path = os.path.expanduser('~/scania_gear_analysis/pickles/heat_treatment/mesh_1x/root_data/'
                                 'carbon_transfer/')

carbon_levels = np.array([0.002, 0.004, 0.006, 0.008, 0.01])
old_t_martensite_par = np.array([51, 56.4, 61.2, 71.2, 72])
old_q_martensite_par = np.array([56, 63, 68, 76, 77])
old_austenite_par = np.array([23, 26, 29, 32, 35])

old_parameters = np.zeros(10)
old_parameters[0:5] = old_austenite_par
old_parameters[5:] = old_t_martensite_par


class Simulation:
    def __init__(self, cd, color, sym, position):
        self.cd = cd
        self.color = color
        self.sym = sym

        pickle_name = pickle_path + 'dante_results_' + str(self.cd).replace('.', '_') + '_' + position + '.pkl'
        with open(pickle_name, 'rb') as flank_pickle:
            simulation_data = pickle.load(flank_pickle, encoding='latin1')
        self.r = simulation_data['r'].flatten()
        self.austenite = simulation_data['SDV_AUSTENITE'].flatten()
        self.hv = simulation_data['HV'].flatten()
        self.hrc = HV2HRC(self.hv)
        self.carbon = simulation_data['SDV_CARBON'].flatten()
        self.t_martensite = simulation_data['SDV_T_MARTENSITE'].flatten()
        self.q_martensite = simulation_data['SDV_Q_MARTENSITE'].flatten()

    def hv_ma(self, parameters):
        au_par = parameters[0:5]
        tm_par = parameters[5:]

        hrc_ma = (self.t_martensite*np.interp(self.carbon, carbon_levels, tm_par)
                  + self.q_martensite*np.interp(self.carbon, carbon_levels, old_q_martensite_par)
                  + self.austenite*np.interp(self.carbon, carbon_levels, au_par))
        return HRC2HV(hrc_ma)

    def hv_bf(self, parameters):
        return self.hv - self.hv_ma(parameters)


class Experiment:
    def __init__(self, cd, color, sym, position, data_array):
        self.r = data_array[:, 0]
        if position == 'flank':
            idx = 2*np.where(np.array([0.2, 0.5, 0.8, 1.1, 1.4]) == cd)[0] + 1
        else:
            idx = 2*np.where(np.array([0.2, 0.5, 0.8, 1.1, 1.4]) == cd)[0] + 2
        self.hv = data_array[:, idx].flatten()
        self.color = color
        self.sym = sym


def hardness_residual(parameters, experiments, simulations, min_bounds, max_bounds):
    parameters[parameters < min_bounds] = min_bounds[parameters < min_bounds]
    parameters[parameters > max_bounds] = max_bounds[parameters > max_bounds]

    residual = 0
    for exp, sim in zip(experiments, simulations):
        hv_bf = np.interp(exp.r, sim.r, sim.hv_bf(old_parameters))
        sim_hrc_ma = sim.hv_ma(parameters)
        sim_hv = np.interp(exp.r, sim.r, sim_hrc_ma) + hv_bf
        residual += np.sum((1 - sim_hv/exp.hv)**2)
    return residual


def main():
    position = 'flank'
    experiment_path = os.path.expanduser('~/scania_gear_analysis/experimental_data/')
    experimental_hardness = np.genfromtxt(experiment_path + 'hardness/hardness_scania.csv')
    simulations = []
    experiments = []
    for cd, c, sym in zip([0.5, 0.8, 1.1, 1.4], 'brgk', 'osdp'):
        simulations.append(Simulation(cd=cd, sym=sym, color=c, position=position))
        experiments.append(Experiment(cd=cd, color=c, sym=sym, position=position, data_array=experimental_hardness))

    for simulation, experiment in zip(simulations, experiments):
        plt.figure(0)

        plt.plot(experiment.r, experiment.hv, '-' + experiment.sym + experiment.color, lw=2, ms=12,
                 label='CD=' + str(simulation.cd) + 'mm')
        plt.plot(simulation.r, simulation.hv, '--' + simulation.color, lw=2)
        # plt.plot(simulation.r, simulation.hv_ma(old_parameters), ':'+simulation.color, lw=2)

        # plt.plot(simulation.r, simulation.hv_bf(old_parameters), simulation.color + ':', lw=2)

    min_bounds = np.array([20, 20, 20, 20, 20, 50, 50, 55, 60, 60])
    max_bounds = np.array([30, 30, 35, 32, 35, 80, 65, 70, 75, 80])
    new_par = fmin(hardness_residual, old_parameters,
                   args=(experiments, simulations, min_bounds, max_bounds), maxfun=1e6, maxiter=1e6)

    print(new_par)

    new_par[5] = 51
    new_par[6] = 56
    for sim in simulations:
        plt.plot(sim.r, sim.hv_bf(old_parameters) + sim.hv_ma(new_par), sim.color + ':', lw=2)
    plt.show()


if __name__ == '__main__':
    main()
