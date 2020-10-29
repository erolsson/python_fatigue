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
                                     'tempering_60min_200C_HRD_1/')
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

        plt.plot(residual_stresses_ivf[:, 3*i], residual_stresses_ivf[:, 3*i + 2],
                 '-' + simulation.sym + simulation.color, ms=12, lw=2, label='CDH = ' + str(simulation.cd) + ' mm')
        plt.plot(residual_stresses_scania[:, 3*i], residual_stresses_scania[:, 3*i + 2],
                 '-' + simulation.sym + simulation.color, ms=12, lw=2)

        plt.figure(1)
        plt.plot(flank_data['r'], flank_data['normal_stress'], '--' + simulation.color, lw=2,
                 label='CHD = ' + str(simulation.cd) + ' mm')

        plt.figure(2)
        plt.plot(flank_data['r'], flank_data['S'][:, 2], '--' + simulation.color, lw=2)
        plt.plot(residual_stresses_ivf[:, 3*i], residual_stresses_ivf[:, 3*i + 1], simulation.color, lw=2)
        plt.plot(residual_stresses_scania[:, 3*i], residual_stresses_scania[:, 3*i + 1], simulation.color, lw=2)

        root_pickle_name = pickle_path + 'dante_results_' + str(simulation.cd).replace('.', '_') + '_root.pkl'
        with open(root_pickle_name, 'rb') as root_pickle:
            root_data = pickle.load(root_pickle, encoding='latin1')
        plt.figure(3)
        plt.plot(root_data['r'], root_data['normal_stress'],  '--' + simulation.color, lw=2,
                 label='CHD = ' + str(simulation.cd) + ' mm')

    fig = plt.figure(0)
    plt.plot([-1, -2], [0, 0], 'k', lw=2, label='Exp.')
    plt.plot([-1, -2], [0, 0], '--k', lw=2, label='Model')
    plt.xlabel('Distance from surface [mm]')
    plt.ylabel('Residual stress [MPa]')
    plt.xlim(0, 0.2)
    plt.ylim(-350, 0)
    plt.text(0.02, 0.92, r'\bf{(a)}', transform=plt.axes().transAxes)
    fig.set_size_inches(11., 6., forward=True)
    ax = plt.subplot(111)
    box = ax.get_position()
    ax.set_position([0.1, 0.12, 0.55, box.height])
    legend = ax.legend(loc='upper left', bbox_to_anchor=(1., 1.035), numpoints=1)
    plt.gca().add_artist(legend)
    plt.savefig('residual_stress_comparison.png')

    plt.figure(2)
    plt.xlim(0, 0.2)
    plt.ylim(-350, 0)

    for fig_nr, label in zip([1, 3], ['b', 'c']):
        plt.figure(fig_nr)
        plt.xlabel('Distance from surface [mm]')
        plt.ylabel('Residual stress [MPa]')
        plt.text(0.02, 0.92, r'\bf{(' + label + ')}', transform=plt.axes().transAxes)
        plt.legend(loc='best', framealpha=0.5)
        plt.tight_layout()

    plt.figure(1)
    plt.text(1., 200., r'\bf{Flank}', fontsize=24)
    plt.savefig('residual_stresses_flank.png')

    plt.figure(3)
    plt.text(1.8, -50., r'\bf{Root}', fontsize=24)
    plt.savefig('residual_stresses_root.png')

    plt.show()


if __name__ == '__main__':
    main()
