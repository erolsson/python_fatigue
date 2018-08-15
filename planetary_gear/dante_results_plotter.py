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


pickle_path = os.path.expanduser('~/scania_gear_analysis/pickles/heat_treatment/mesh_1x/')
experimental_path = os.path.expanduser('~/scania_gear_analysis/experimental_data/')
Simulation = namedtuple('Simulation', ['cd', 'color', 'sym'])
simulations = [Simulation(cd=0.5, color='b', sym='o'), Simulation(cd=0.8, color='r', sym='s'),
               Simulation(cd=1.1, color='g', sym='d'), Simulation(cd=1.4, color='k', sym='p')]

figures = []
for simulation in simulations:
    pickle_name = pickle_path + 'dante_results_' + str(simulation.cd).replace('.', '_')
    for j, data_path in enumerate(['root', 'flank']):
        with open(pickle_name + '_' + data_path + '.pkl', 'r') as pickle_handle:
            dante_data = pickle.load(pickle_handle)

        figures.append(plt.figure(0 + 2*j))
        plt.plot(dante_data['r'], dante_data['HV'], '--' + simulation.color, lw=2)
        experimental_data = np.genfromtxt(experimental_path + 'hardness/exp_' + data_path + '_' +
                                          str(simulation.cd).replace('.', '_') + '.csv', delimiter=',')

        plt.plot(experimental_data[:, 0], experimental_data[:, 1], '-' + simulation.sym + simulation.color,
                 lw=2, ms=12, mec='k')
        figures.append(plt.figure(1 + 2*j))
        plt.plot(dante_data['r'], dante_data['S'], '--' + simulation.color, lw=2)

for figure in range(4):
    plt.figure(figure)
    plt.grid(True)
    plt.xlabel('Distance from surface [mm]')
    plt.xlim(0, 3)
    plt.tight_layout()

plt.show()
