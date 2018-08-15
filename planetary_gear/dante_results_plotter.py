from collections import namedtuple
import pickle
import os

import numpy as np

import matplotlib.pyplot as plt
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


pickle_path = os.path.expanduser('~/scania_gear_analysis/pickles/heat_treatment/mesh_1x/')
Simulation = namedtuple('Simulation', ['cd', 'color'])
simulations = [Simulation(cd=0.5, color='b'), Simulation(cd=0.8, color='r'),
               Simulation(cd=1.1, color='g'), Simulation(cd=1.4, color='k')]

for simulation in simulations:
    pickle_name = pickle_path + 'dante_results_' + str(simulation.cd).replace('.', '_')
    for j, data_path in enumerate(['root', 'flank']):
        with open(pickle_name + '_' + data_path + '.pkl', 'r') as pickle_handle:
            dante_data = pickle.load(pickle_handle)

        plt.figure(0 + 3*j)
        plt.plot(dante_data['r'], dante_data['HV'], '--' + simulation.color, lw=2)

plt.show()
