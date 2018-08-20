import sys

import pickle
import numpy as np


mesh = '1x'
residual_stress_multiplier = 0.5     # This should be removed later
dante_pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' \
                       + mesh + '/dante/'

with open(dante_pickle_directory + 'data_' + str(cd).replace('.', '_') + '.pkl') as pickle_handle:
    dante_data = pickle.load(pickle_handle)

cd = float(sys.argv[1])
loads = np.arange(30, 41, 1.)

for load in loads:
