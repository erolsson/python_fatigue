import os
import sys

import pickle
import numpy as np

from multiaxial_fatigue.findley_evaluation_functions import evaluate_findley

specimen = sys.argv[1]
R = float(sys.argv[2])

interesting_point = np.array([0., 2.5, 0])

dante_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/dante/')
mechanical_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/stresses/')
geometry_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/geometry/')

load_levels = {'smooth': {-1.: np.array([737., 774, 820]),
                          0.0: np.array([425., 440])},
               'notched': {-1.: np.array([427., 450]),
                           0.0: np.array([225., 240, 255])}}

with open(mechanical_pickle_directory + 'unit_load_' + specimen + '.pkl') as pickle_handle:
    mechanical_data = pickle.load(pickle_handle)

with open(geometry_pickle_directory + 'nodal_coordinates_' + specimen + '.pkl') as pickle_handle:
    nodal_coordinates = pickle.load(pickle_handle)


distance_to_monitor_node = 0*nodal_coordinates + nodal_coordinates
for i in range(3):
    distance_to_monitor_node[:, i] -= interesting_point[i]
monitor_node_idx = np.argmin(np.sum(np.abs(distance_to_monitor_node), 1))

with open(dante_pickle_directory + 'data_utmis_' + specimen + '.pkl') as pickle_handle:
    dante_data = pickle.load(pickle_handle)
n = dante_data['HV'].shape[0]

for amplitude_stress in load_levels[specimen][R]:
    mean_stress = amplitude_stress*(1+R)/(1-R)

    print "======== Mechanical stress state =========="
    print "sa =", amplitude_stress, "sm=", mean_stress

    max_stress = (mean_stress + amplitude_stress)*mechanical_data
    min_stress = (mean_stress - amplitude_stress)*mechanical_data

    print "The mechanical stress at interesting point in the x-direction is ", max_stress[monitor_node_idx, 0], "MPa"

    stress_history = np.zeros((2, n, 6))
    stress_history[0, :, :] = min_stress + dante_data['S']
    stress_history[1, :, :] = max_stress + dante_data['S']
    print "======== Combined stress state =========="
    print "The maximum stress at interesting point in the x-direction is ", stress_history[1, monitor_node_idx, 0], \
        "MPa"
    print "The minimum stress at interesting point in the x-direction is ", stress_history[0, monitor_node_idx, 0], \
        "MPa"
    for a800 in np.arange(0.6, 1.7, 0.1):
        print '======================================================================================================='
        print '          Analyzing a800 =', a800
        print '======================================================================================================='
        findley_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/stresses/findley/'
                                                      + 'a800=' + str(a800).replace('.', '_') + '/')

        if not os.path.isdir(findley_pickle_directory):
            os.makedirs(findley_pickle_directory)

        HV = dante_data['HV']
        b = (a800 - 0.3)/(800-450)
        a = a800 - b*800

        print "The findley parameter coefficients are a={} and b={}".format(a, b)
        findley_k = a + b*HV
        print "The maximum value of the findley parameter is", np.max(findley_k), "and the minimum is", \
            np.min(findley_k)
        findley_data = evaluate_findley(combined_stress=stress_history, a_cp=findley_k, worker_run_out_time=80000,
                                        num_workers=8, chunk_size=1000, search_grid=10)

        findley_stress = findley_data[:, 2]
        print "Findley stress at interesting point", findley_stress[monitor_node_idx], 'MPa'
        findley_pickle_name = 'findley_' + specimen + '_R=' + str(int(R)) + '_' + 's=' + str(int(amplitude_stress)) + \
                              'MPa.pkl'
        with open(findley_pickle_directory + findley_pickle_name, 'w') as pickle_handle:
            pickle.dump(findley_stress, pickle_handle)
