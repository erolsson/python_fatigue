from collections import namedtuple
import pickle
import os

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


def main():
    pickle_path = os.path.expanduser('~/scania_gear_analysis/pickles/heat_treatment/mesh_1x/root_data/'
                                     'tempering_72min_200C/')
    experiment_path = os.path.expanduser('~/scania_gear_analysis/experimental_data/')
    Simulation = namedtuple('Simulation', ['cd', 'color', 'sym'])
    simulations = [Simulation(cd=0.5, color='b', sym='o'), Simulation(cd=0.8, color='r', sym='s'),
                   Simulation(cd=1.1, color='g', sym='d'), Simulation(cd=1.4, color='k', sym='p')]

    residual_stresses_ivf = np.genfromtxt(experiment_path + 'residual_stresses/residual_stresses_ivf.csv')
    residual_stresses_scania = np.genfromtxt(experiment_path + 'residual_stresses/residual_stresses_scania.csv')

    for i, simulation in enumerate(simulations):
        flank_pickle_name = pickle_path + 'dante_results_' + str(simulation.cd).replace('.', '_') + '_flank.pkl'
        with open(flank_pickle_name, 'rb') as flank_pickle:
            flank_data = pickle.load(flank_pickle, encoding='latin1')
        plt.figure(0)
        plt.plot(flank_data['r'], flank_data['normal_stress'],  '--' + simulation.color, lw=2)

        plt.plot(residual_stresses_ivf[:, 3*i], residual_stresses_ivf[:, 3*i + 2], simulation.color, lw=2)
        plt.plot(residual_stresses_scania[:, 3*i], residual_stresses_scania[:, 3*i + 2], simulation.color, lw=2)

        plt.figure(1)
        plt.plot(flank_data['r'], flank_data['normal_stress'], '--' + simulation.color, lw=2)

        plt.figure(2)
        plt.plot(flank_data['r'], flank_data['S'][:, 2], '--' + simulation.color, lw=2)
        plt.plot(residual_stresses_ivf[:, 3*i], residual_stresses_ivf[:, 3*i + 1], simulation.color, lw=2)
        plt.plot(residual_stresses_scania[:, 3*i], residual_stresses_scania[:, 3*i + 1], simulation.color, lw=2)

        root_pickle_name = pickle_path + 'dante_results_' + str(simulation.cd).replace('.', '_') + '_root.pkl'
        with open(root_pickle_name, 'rb') as root_pickle:
            root_data = pickle.load(root_pickle, encoding='latin1')
        plt.figure(3)
        plt.plot(root_data['r'], root_data['normal_stress'],  '--' + simulation.color, lw=2)

    plt.figure(0)
    plt.xlim(0, 0.2)
    plt.ylim(-350, 0)

    plt.figure(2)
    plt.xlim(0, 0.2)
    plt.ylim(-350, 0)
    plt.show()


if __name__ == '__main__':
    main()
