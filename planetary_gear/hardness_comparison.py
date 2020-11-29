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
                                     'carbon_transfer/')
    experiment_path = os.path.expanduser('~/scania_gear_analysis/experimental_data/')
    Simulation = namedtuple('Simulation', ['cd', 'color', 'sym'])
    simulations = [Simulation(cd=0.5, color='b', sym='o'), Simulation(cd=0.8, color='r', sym='s'),
                   Simulation(cd=1.1, color='g', sym='d'), Simulation(cd=1.4, color='k', sym='p')]

    experimental_hardness = np.genfromtxt(experiment_path + 'hardness/hardness_scania.csv')
    experimental_carbon = np.genfromtxt(experiment_path + 'carbon_profiles/carbon_profiles.csv',
                                        delimiter='\t')
    print(experimental_carbon)

    for i, simulation in enumerate(simulations):
        plt.figure(0)
        plt.plot(experimental_hardness[:, 0], experimental_hardness[:, 2*i + 3],
                 '-' + simulation.sym + simulation.color, lw=2, ms=12, label='CD=' + str(simulation.cd) + 'mm')
        flank_pickle_name = pickle_path + 'dante_results_' + str(simulation.cd).replace('.', '_') + '_flank.pkl'
        with open(flank_pickle_name, 'rb') as flank_pickle:
            flank_data = pickle.load(flank_pickle, encoding='latin1')
        plt.plot(flank_data['r'], flank_data['HV'], '--' + simulation.color, lw=2)

        plt.figure(1)
        plt.plot(experimental_hardness[:, 0], experimental_hardness[:, 2*i + 4],
                 '-' + simulation.sym + simulation.color, lw=2, ms=12, label='CHD = ' + str(simulation.cd) + ' mm')
        root_pickle_name = pickle_path + 'dante_results_' + str(simulation.cd).replace('.', '_') + '_root.pkl'
        with open(root_pickle_name, 'rb') as root_pickle:
            root_data = pickle.load(root_pickle, encoding='latin1')
        plt.plot(root_data['r'], root_data['HV'], '--' + simulation.color, lw=2)

        plt.figure(2)
        plt.plot(flank_data['r'], flank_data['SDV_CARBON'], '--' + simulation.color, lw=2)

        plt.figure(3)
        plt.plot(flank_data['r'], flank_data['SDV_UBAINITE'] + flank_data['SDV_LBAINITE'],
                 '--' + simulation.color, lw=2)
        plt.figure(4)
        plt.plot(flank_data['r'], root_data['SDV_UBAINITE'] + root_data['SDV_LBAINITE'],
                 '--' + simulation.color, lw=2)

        plt.figure(2)
        plt.plot(experimental_carbon[:, 1], experimental_carbon[:, 3+i]/100, '-' + simulation.sym + simulation.color,
                 lw=2, ms=12)

    fig = plt.figure(1)
    plt.plot([-1, -2], [0, 0], 'k', lw=2, label='Exp.')
    plt.plot([-1, -2], [0, 0], '--k', lw=2, label='Model')
    plt.xlabel('Distance from surface [mm]')
    plt.ylabel('Hardness [HV]')
    fig.set_size_inches(11., 6., forward=True)
    plt.xlim(0, 3)
    plt.ylim(300, 800)
    ax = plt.subplot(111)
    box = ax.get_position()
    ax.set_position([0.1, 0.12, 0.55, box.height])
    legend = ax.legend(loc='upper left', bbox_to_anchor=(1., 1.035), numpoints=1)

    plt.gca().add_artist(legend)
    plt.savefig('hardness_root.png')
    plt.show()


if __name__ == '__main__':
    main()
