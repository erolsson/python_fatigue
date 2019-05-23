import os
import sys

import pickle
import numpy as np

from multiaxial_fatigue.findley_evaluation_functions import evaluate_findley

specimen = sys.argv[1]
R = float(sys.argv[2])
load = float(sys.argv[3])

interesting_point = np.array([0., -2.5, 0])
pickle_path = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/mechanical_data/')

specimen_loads = {'smooth': {-1.: [737., 774., 820.], 0.: [425., 440.]},
                  'notched': {-1.: [427., 450.], 0.: [225., 240., 255.]}}

loads = specimen_loads[specimen][R]
name = 'utmis_' + specimen + '_' + str(load).replace('.', '_') + '_R=' + str(int(R))
with open(pickle_path + 'fatigue_pickle_' + name + '.pkl') as pickle_handle:
    fatigue_data = pickle.load(pickle_handle)
nodal_coordinates = fatigue_data['pos']

distance_to_monitor_node = 0*nodal_coordinates + nodal_coordinates
for i in range(3):
    distance_to_monitor_node[:, i] -= interesting_point[i]
monitor_node_idx = np.argmin(np.sum(np.abs(distance_to_monitor_node), 1))

print "The monitor node has coordinates", nodal_coordinates[monitor_node_idx]

stress_history = fatigue_data['S']

print "======== Combined stress state =========="
print "The maximum stress at interesting point in the x-direction is ", stress_history[1, monitor_node_idx, 0], \
    "MPa"
print "The minimum stress at interesting point in the x-direction is ", stress_history[0, monitor_node_idx, 0], \
    "MPa"
for a800 in np.array([0.6, 0.8, 1.0, 1.2, 1.4, 1.6]):
    print '======================================================================================================='
    print '          Analyzing a800 =', a800
    print '======================================================================================================='

    HV = fatigue_data['HV']
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
    i_max = np.argmax(findley_stress)
    print "The maximum findley stress is", findley_stress[i_max], "and occurs at", nodal_coordinates[i_max]
    findley_pickle_name = 'findley_' + name + '.pkl'
    with open(pickle_path + findley_pickle_name, 'w') as pickle_handle:
        pickle.dump(findley_stress, pickle_handle)
