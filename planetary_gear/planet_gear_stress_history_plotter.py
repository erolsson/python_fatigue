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
simulations = [Simulation(torque=1000, color='b'),
               Simulation(torque=1200, color='r'), Simulation(torque=1400, color='g')]

pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_stresses/')
max_values = {'pos': {'max': [0], 'min': [0]}, 'neg': {'max': [0], 'min': [0]}}
torques = np.array([0, 1000, 1200, 1400])
for i, name in enumerate(['pos', 'neg']):
    plt.figure(i)
    for simulation in simulations:
        stress_pickle_name = pickle_directory + 'stresses_' + str(simulation.torque) + '_Nm_' + name + '.pkl'
        with open(stress_pickle_name) as stress_pickle:
            stress_data = pickle.load(stress_pickle)
        stress_data[:, 0] -= stress_data[0, 0]
        idx = np.argwhere(stress_data[:, 0] == 0)[1][0]
        max_values[name]['max'].append(np.max(stress_data[:, 1]))
        max_values[name]['min'].append(np.min(stress_data[:, 1]))
        plt.plot(stress_data[idx:, 0], stress_data[idx:, 1], simulation.color, lw=2)
        plt.plot(stress_data[:idx, 0], stress_data[:idx, 1], simulation.color, lw=2)

    plt.grid(True)
    plt.xlabel('Time')
    plt.ylabel('Stress [MPa]')
    if name == 'pos':
        tooth_name = 'Positive'
    else:
        tooth_name = 'Negative'
    plt.text(0.2, -1750, tooth_name + ' tooth')
    plt.tight_layout()
    plt.figure(i+2)
    plt.plot(torques, max_values[name]['max'], 'rs')
    plt.plot(torques, max_values[name]['min'], 'bo')
print max_values
plt.show()
