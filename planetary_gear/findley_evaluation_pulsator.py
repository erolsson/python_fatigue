import os
import sys

import pickle
import numpy as np

from multiaxial_fatigue.findley_evaluation_functions import evaluate_findley

mesh = '1x'
cd = float(sys.argv[1])

interesting_point = np.array([-4.40, 33.288, 0.0])

dante_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' +
                                            mesh + '/dante_tempering_2h_180C_20190129/')

mechanical_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' +
                                                 mesh + '/pulsator_stresses/')

geometry_data_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' +
                                             mesh + '/geometry/')

with open(dante_pickle_directory + 'data_' + str(cd).replace('.', '_') + '_left.pkl') as pickle_handle:
    dante_data = pickle.load(pickle_handle)

with open(mechanical_pickle_directory + 'pulsator_stresses.pkl') as pickle_handle:
    mechanical_data = pickle.load(pickle_handle)

with open(geometry_data_directory + '/nodal_coordinates_tooth_left.pkl') as position_pickle:
    nodal_coordinates = pickle.load(position_pickle)

distance_to_monitor_node = 0*nodal_coordinates + nodal_coordinates
for i in range(3):
    distance_to_monitor_node[:, i] -= interesting_point[i]
monitor_node_idx = np.argmin(np.sum(np.abs(distance_to_monitor_node), 1))
print "Coordinates of interesting point is", nodal_coordinates[monitor_node_idx], 'and has index', monitor_node_idx

print '========================================================================================================='
print 'The residual stress at interesting point is: '
print dante_data['S'][monitor_node_idx, :]
print '========================================================================================================='


loads = np.arange(30, 41, 1.)
n = dante_data.values()[0].shape[0]
stress_history = np.zeros((2, n, 6))

for load in loads:
    print '========================================================================================================'
    print "Analyzing Pamp =", load, 'kN'
    print '========================================================================================================'
    fem_loads = np.array(mechanical_data.values()[0].keys())
    f1, f2 = tuple(np.sort(fem_loads[np.argsort(np.abs(fem_loads - load))][0:2]))

    min_stresses = mechanical_data['min_load']
    max_stresses = mechanical_data['max_load']
    print "Max mechanical stress at interesting point"
    print "Pamp = 30 kN :", max_stresses[30][monitor_node_idx]
    print "Pamp = 35 kN :", max_stresses[35][monitor_node_idx]
    print "Pamp = 40 kN :", max_stresses[40][monitor_node_idx]

    min_stress = min_stresses[f1] + (min_stresses[f2] - min_stresses[f1])/(f2 - f1)*(load-f1)
    max_stress = max_stresses[f1] + (max_stresses[f2] - max_stresses[f1])/(f2 - f1)*(load-f1)

    stress_history[0, :, :] = min_stress + dante_data['S']
    stress_history[1, :, :] = max_stress + dante_data['S']

    print '========================================================================================================'
    print 'The minimum stress at interesting point is ', stress_history[0, monitor_node_idx, :]
    print 'The maximum stress at interesting point is ', stress_history[1, monitor_node_idx, :]
    print '========================================================================================================'
    for a800 in np.array([0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]):
        findley_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/'
                                                      'mesh_' + mesh + '/findley_tempering_2h_180C_a800=' +
                                                      str(a800).replace('.', '_') + '/pulsator/')

        if not os.path.isdir(findley_pickle_directory):
            os.makedirs(findley_pickle_directory)

        print '========================================================================================================'
        print "Analyzing a800 =", a800
        print '========================================================================================================'
        HV = dante_data['HV']
        b = (a800 - 0.3) / (800 - 450)
        a = a800 - b * 800

        findley_k = a + b * HV
        findley_data = evaluate_findley(combined_stress=stress_history,
                                        a_cp=findley_k,
                                        worker_run_out_time=8000,
                                        num_workers=8, chunk_size=300, search_grid=10)

        findley_stress = findley_data[:, 2]
        print "The Findley stress at interesting point is ", findley_stress[0], 'MPa'
        findley_pickle_name = 'findley_CD=' + str(cd).replace('.', '_') + '_Pamp=' + str(load).replace('.', '_') + \
                              'kN.pkl'
        with open(findley_pickle_directory + findley_pickle_name, 'w') as pickle_handle:
            pickle.dump(findley_stress, pickle_handle)
