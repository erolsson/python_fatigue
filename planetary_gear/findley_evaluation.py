import sys
import os
import pickle

import numpy as np

from multiaxial_fatigue.findley_evaluation_functions import evaluate_findley
from materials.gear_materials import SS2506
from materials.gear_materials import SteelData

case_depth = float(sys.argv[1])
loads = np.arange(29., 41., 1.)
residual_stress_multiplier = 0.5
stress_ratio = float(sys.argv[2])

data_directory = 'pickles/tooth_root_data/'

for eval_type in ['surface', 'volume']:
    mechanical_pickle = open(data_directory + eval_type + '_data/mechanical_loads.pkl')
    mechanical_stress = pickle.load(mechanical_pickle)
    mechanical_pickle.close()

    dante_pickle = open(data_directory + eval_type + '_data/danteCD' + str(case_depth).replace('.', '_') + '.pkl')
    dante_data = pickle.load(dante_pickle)
    dante_pickle.close()
    findley_k = SS2506.findley_k(SteelData(HV=dante_data['HV']))

    output_dir = 'pickles/tooth_root_data/' + eval_type + '_data/findley_R=' + str(stress_ratio).replace('.', '_')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for load_amplitude in loads:
        print 'Working with CHD =', case_depth, 'mm with a load of', load_amplitude, 'kN'

        mean_load = (1+stress_ratio)/(1-stress_ratio)*load_amplitude

        max_load = mean_load + load_amplitude
        min_load = mean_load - load_amplitude

        # Stress ratio in FEM simulation is R = 0.1
        max_load_sim = abs((1+0.1)/(1-0.1)*mechanical_stress['force'] + mechanical_stress['force'])
        min_load_sim = abs((1+0.1)/(1-0.1)*mechanical_stress['force'] - mechanical_stress['force'])

        stress_history = np.zeros((2, mechanical_stress['max'].shape[0], 6))

        # Finding out if the maximum stress or the minimum stress from the FEM should be used
        if abs(abs(min_load) - max_load_sim) < abs(abs(min_load) - min_load_sim):
            stress_history[1, :, :] = mechanical_stress['max']/max_load_sim*min_load
        else:
            stress_history[1, :, :] = mechanical_stress['min']/min_load_sim*min_load

        if abs(abs(max_load) - max_load_sim) < abs(abs(max_load) - min_load_sim):
            stress_history[1, :, :] = mechanical_stress['max']/max_load_sim*max_load
        else:
            stress_history[1, :, :] = mechanical_stress['min']/min_load_sim*max_load

        # Adding the residual stresses
        for i in range(stress_history.shape[0]):
            stress_history[i, :, :] += dante_data['S']*residual_stress_multiplier

        findley_data = evaluate_findley(combined_stress=stress_history, a_cp=findley_k, worker_run_out_time=8000,
                                        num_workers=8, chunk_size=300, search_grid=10)
        findley_stress = findley_data[:, 2]

        findley_pickle = open(output_dir + '/CD' + str(case_depth).replace('.', '_') + '_Pamp=' +
                              str(load_amplitude).replace('.', '_') + 'kN.pkl', 'w')
        pickle.dump(findley_stress, findley_pickle)
        findley_pickle.close()
