import os
import sys

import pickle
import numpy as np


mesh = '1x'
cd = float(sys.argv[1])

residual_stress_multiplier = 0.5     # This should be removed later
dante_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' +
                                            mesh + '/dante/')

mechanical_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' +
                                                 mesh + '/pulsator_stresses/')

with open(dante_pickle_directory + 'data_' + str(cd).replace('.', '_') + '.pkl') as pickle_handle:
    dante_data = pickle.load(pickle_handle)

with open(mechanical_pickle_directory + 'pulsator_stresses.pkl') as pickle_handle:
    mechanical_data = pickle.load(pickle_handle)

loads = np.arange(30, 41, 1.)
n = dante_data.values()[0].shape[0]
stress_history = np.zeros((2, n, 6))

for load in loads:
    fem_loads = np.array(mechanical_data.values()[0].keys())
    f1, f2 = tuple(np.sort(fem_loads[np.argsort(np.abs(fem_loads - load))][0:2]))

    min_stresses = mechanical_data['min_load']
    max_stresses = mechanical_data['max_load']
    min_stress = min_stresses[f1] + (min_stresses[f2] - min_stresses[f1])/(f2 - f1)*load
    max_stress = max_stresses[f1] + (max_stresses[f2] - max_stresses[f1])/(f2 - f1)*load
    print np.max(max_stress)
    print np.max(min_stress)

