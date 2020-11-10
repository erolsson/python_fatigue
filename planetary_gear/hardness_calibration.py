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
                                 'tempering_60min_200C_HRD_1/')


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


def hardness_residual(par):
    pass


def main():
    position = 'root'
    experiment_path = os.path.expanduser('~/scania_gear_analysis/experimental_data/')
    simulations = [Simulation(cd=0.5, color='b', sym='o', position=position),
                   Simulation(cd=0.8, color='r', sym='s', position=position),
                   Simulation(cd=1.1, color='g', sym='d', position=position),
                   Simulation(cd=1.4, color='k', sym='p', position=position)]

    experimental_hardness = np.genfromtxt(experiment_path + 'hardness/hardness_scania.csv')

    carbon_levels = [0.002, 0.004, 0.006, 0.008, 0.01]
    old_t_martensite_par = np.array([53, 52, 59, 69, 72])
    old_q_martensite_par = np.array([58, 59, 65, 74, 77])
    old_austenite_par = [23, 26, 29, 32, 35]

    for i, simulation in enumerate(simulations):
        plt.figure(0)
        plt.plot(experimental_hardness[:, 0], experimental_hardness[:, 2*i + 3],
                 '-' + simulation.sym + simulation.color, lw=2, ms=12, label='CD=' + str(simulation.cd) + 'mm')
        plt.plot(simulation.r, simulation.hv, '--' + simulation.color, lw=2)
        print(simulation.t_martensite)
        hrc_ma = (simulation.t_martensite*np.interp(simulation.carbon, carbon_levels, old_t_martensite_par),
                  + simulation.q_martensite*np.interp(simulation.carbon, carbon_levels, old_q_martensite_par)
                  + simulation.austenite*np.interp(simulation.carbon, carbon_levels, old_austenite_par))
        hv_ma = HRC2HV(hrc_ma)
        print(hv_ma)
        plt.plot(simulation.r, hv_ma, ':', simulation.color, lw=2)
    plt.show()


if __name__ == '__main__':
    main()
