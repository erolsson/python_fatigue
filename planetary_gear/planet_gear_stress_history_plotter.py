import os

from collections import namedtuple

import numpy as np
import pickle
import matplotlib.pyplot as plt
import matplotlib.style

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

Simulation = namedtuple('Simulation', ['torque', 'color'])
simulations = [Simulation(torque=400, color='k'), Simulation(torque=1000, color='b'),
               Simulation(torque=1200, color='r'), Simulation(torque=1400, color='g')]

pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_stresses/')

for i, name in enumerate(['pos', 'neg']):
    plt.figure(i)
    for simulation in simulations:
        stress_pickle_name = pickle_directory + 'stresses_' + str(simulation.torque) + '_Nm_' + name + '.pkl'
        with open(stress_pickle_name) as stress_pickle:
            stress_data = pickle.load(stress_pickle)
        stress_data[:, 0] -= stress_data[0, 0]
        idx = np.argwhere(stress_data[:, 0] == 0)[1][0]
    
        plt.plot(stress_data[idx:, 0], stress_data[idx:, 1], simulation.color, lw=2)
        plt.plot(stress_data[:idx, 0], stress_data[:idx, 1], simulation.color, lw=2)

    plt.grid(True)
    plt.xlabel('Time')
    plt.ylabel('Stress [MPa]')
plt.show()
