import os
import sys

import pickle
import numpy as np

from materials.gear_materials import SS2506
from materials.gear_materials import SteelData

from multiaxial_fatigue.findley_evaluation_functions import evaluate_findley

mesh = '1x'
cd = float(sys.argv[1])

# residual_stress_multiplier = 0.572     # This should be removed later
residual_stress_multiplier = 1.     # This should be removed later
dante_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' +
                                            mesh + '/dante/')


mechanical_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' +
                                                 mesh + '/planet_gear_stresses/')

findley_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' +
                                              mesh + '/findley_no_scaling/gear_box/')

with open(dante_pickle_directory + 'data_' + str(cd).replace('.', '_') + '.pkl') as pickle_handle:
    dante_data = pickle.load(pickle_handle)

with open(mechanical_pickle_directory + 'gear_stresses.pkl') as pickle_handle:
    mechanical_data = pickle.load(pickle_handle)

loads = np.arange(900, 1600, 100.)
n = dante_data.values()[0].shape[0]
stress_history = np.zeros((2, n, 6))

for load in loads:
    fem_loads = np.array(mechanical_data.values()[0].values()[0].keys())
    print fem_loads
    sdfsdfsd
    f1, f2 = tuple(np.sort(fem_loads[np.argsort(np.abs(fem_loads - load))][0:2]))

    min_stresses = mechanical_data['min_load']
    max_stresses = mechanical_data['max_load']
    min_stress = min_stresses[f1] + (min_stresses[f2] - min_stresses[f1])/(f2 - f1)*(load-f1)
    max_stress = max_stresses[f1] + (max_stresses[f2] - max_stresses[f1])/(f2 - f1)*(load-f1)

    stress_history[0, :, :] = min_stress + dante_data['S']*residual_stress_multiplier
    stress_history[1, :, :] = max_stress + dante_data['S']*residual_stress_multiplier
    steel_data = SteelData(HV=dante_data['HV'])
    print np.max(stress_history[1, :, :], 0)

    findley_k = SS2506.findley_k(steel_data)
    findley_data = evaluate_findley(combined_stress=stress_history, a_cp=findley_k, worker_run_out_time=8000,
                                    num_workers=8, chunk_size=300, search_grid=10)

    findley_stress = findley_data[:, 2]
    print "Maximum Findley stress", np.max(findley_stress), 'MPa'
    findley_pickle_name = 'findley_CD=' + str(cd).replace('.', '_') + '_Pamp=' + str(load).replace('.', '_') + 'kN.pkl'
    with open(findley_pickle_directory + findley_pickle_name, 'w') as pickle_handle:
        pickle.dump(findley_stress, pickle_handle)
