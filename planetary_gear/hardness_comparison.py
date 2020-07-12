from collections import namedtuple
import pickle
import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style

from scipy.interpolate import interp1d

from python_fatigue.materials.hardess_convertion_functions import HRC2HV, HV2HRC

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def main():
    pickle_path = os.path.expanduser('~/scania_gear_analysis/pickles/heat_treatment/mesh_1x/root_data/'
                                     'tempering_60min_200C_HRD/')
    experiment_path = os.path.expanduser('~/scania_gear_analysis/experimental_data/')
    Simulation = namedtuple('Simulation', ['cd', 'color', 'sym'])
    simulations = [Simulation(cd=0.5, color='b', sym='o'), Simulation(cd=0.8, color='r', sym='s'),
                   Simulation(cd=1.1, color='g', sym='d'), Simulation(cd=1.4, color='k', sym='p')]

    experimental_hardness = np.genfromtxt(experiment_path + 'hardness/hardness_scania.csv')

    carbon_levels = np.array([0.1, 0.2, 0.4, 0.6, 0.8, 1.0])/100
    t_mart_old = np.array([38., 45., 52., 59., 71.5, 72.])
    t_mart_new = np.array([38., 52., 54., 61., 67.5, 70.])
    austenite_old = np.array([21., 23., 26., 29., 32., 35.])

    for i, simulation in enumerate(simulations):
        plt.figure(0)
        plt.plot(experimental_hardness[:, 0], experimental_hardness[:, 2*i+3], simulation.color, lw=2)
        flank_pickle_name = pickle_path + 'dante_results_' + str(simulation.cd).replace('.', '_') + '_flank.pkl'
        with open(flank_pickle_name, 'rb') as flank_pickle:
            flank_data = pickle.load(flank_pickle, encoding='latin1')
        plt.plot(flank_data['r'], flank_data['HV'], '--' + simulation.color, lw=2)

        plt.figure(1)
        plt.plot(experimental_hardness[:, 0], experimental_hardness[:, 2*i + 4], simulation.color, lw=2)
        root_pickle_name = pickle_path + 'dante_results_' + str(simulation.cd).replace('.', '_') + '_root.pkl'
        with open(root_pickle_name, 'rb') as root_pickle:
            root_data = pickle.load(root_pickle, encoding='latin1')
        plt.plot(root_data['r'], root_data['HV'], '--' + simulation.color, lw=2)

        plt.figure(2)
        plt.plot(root_data['r'], root_data['SDV_CARBON'], '--' + simulation.color, lw=2)

        plt.figure(3)
        plt.plot(root_data['r'], root_data['SDV_AUSTENITE'], '--' + simulation.color, lw=2)

        plt.figure(4)
        plt.plot(root_data['r'], flank_data['SDV_UBAINITE'] + flank_data['SDV_LBAINITE'], '--' + simulation.color, lw=2)

        plt.figure(5)
        plt.plot(flank_data['r'], flank_data['SDV_T_MARTENSITE'], '--' + simulation.color, lw=2)
        plt.plot(root_data['r'], root_data['SDV_T_MARTENSITE'], '--' + simulation.color, lw=2)

        interp_exp = np.interp(root_data['r'], experimental_hardness[:, 0], experimental_hardness[:, 2*i + 4])
        plt.figure(1)
        plt.plot(root_data['r'], interp_exp, ':' + simulation.color, lw=2)

        plt.figure(6)
        plt.plot(experimental_hardness[:, 0], HV2HRC(experimental_hardness[:, 2*i + 4]), simulation.color, lw=2)
        plt.plot(root_data['r'], HV2HRC(root_data['HV']), '--' + simulation.color, lw=2)

        hv_mart_old = HRC2HV(interp1d(carbon_levels, t_mart_old)(root_data['SDV_CARBON'])[:, 0])
        hv_mart_new = HRC2HV(interp1d(carbon_levels, t_mart_new)(root_data['SDV_CARBON'])[:, 0])
        hv_austenite = HRC2HV(interp1d(carbon_levels, austenite_old)(root_data['SDV_CARBON'])[:, 0])
        hv_mart_aust_old = (hv_mart_old*root_data['SDV_T_MARTENSITE'][:, 0]
                            + hv_austenite*root_data['SDV_AUSTENITE'][:, 0])
        hv_mart_aust_new = (hv_mart_new*root_data['SDV_T_MARTENSITE'][:, 0]
                            + hv_austenite*root_data['SDV_AUSTENITE'][:, 0])
        plt.figure(10)
        plt.plot(root_data['r'], root_data['HV'][:, 0] - hv_mart_aust_old, '--' + simulation.color, lw=2)
    plt.show()


if __name__ == '__main__':
    main()
