import os
import sys

import pickle
import numpy as np

from materials.gear_materials import SS2506
from materials.gear_materials import SteelData

from multiaxial_fatigue.findley_evaluation_functions import evaluate_findley

specimen = sys.argv[1]
R = float(sys.argv[2])

dante_pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/dante/'
mechanical_pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/stresses/'
findley_pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/utmis_specimens/stresses/findley/'

if not os.path.isdir(findley_pickle_directory):
    os.makedirs(findley_pickle_directory)

load_levels = {'smooth': {-1.: np.array([760.]),
                          0.0: np.array([424.])},
               'notched': {-1.: np.array([439.]),
                           0.0: np.array([237.])}}

with open(mechanical_pickle_directory + 'unit_load_' + specimen + '.pkl') as pickle_handle:
    mechanical_data = pickle.load(pickle_handle)

with open(dante_pickle_directory + 'data_utmis_' + specimen + '.pkl') as pickle_handle:
    dante_data = pickle.load(pickle_handle)
n = dante_data['HV'].shape[0]

for amplitude_stress in load_levels[specimen][R]:
    mean_stress = amplitude_stress*(1+R)/(1-R)
    print "sa =", amplitude_stress, "sm=", mean_stress

    max_stress = (mean_stress + amplitude_stress)*mechanical_data
    min_stress = (mean_stress - amplitude_stress)*mechanical_data

    stress_history = np.zeros((2, n, 6))
    stress_history[0, :, :] = min_stress + dante_data['S']
    stress_history[1, :, :] = max_stress + dante_data['S']
    steel_data = SteelData(HV=dante_data['HV'])

    findley_k = SS2506.findley_k(steel_data)
    findley_data = evaluate_findley(combined_stress=stress_history, a_cp=findley_k, worker_run_out_time=80000,
                                    num_workers=8, chunk_size=1000, search_grid=10)

    findley_stress = findley_data[:, 2]
    print "Maximum Findley stress", np.max(findley_stress), 'MPa'
    findley_pickle_name = 'findley_' + specimen + 'R=' + str(int(R)) + '_' + _ + 's=' + str(int(amplitude_stress)) + \
                          'MPa.pkl'
    with open(findley_pickle_directory + findley_pickle_name, 'w') as pickle_handle:
        pickle.dump(findley_stress, pickle_handle)
