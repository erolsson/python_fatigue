from collections import namedtuple
import os
import pickle

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from materials.gear_materials import SteelData
from materials.gear_materials import SS2506
from planetary_gear.test_results import TestResults

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def calculate_findley_stress(fem_data, load_levels, load, dante_data):
    residual_stress = dante_data['S'][0] * residual_stress_multiplier

    hardness = dante_data['HV'][0]
    kf = SS2506.findley_k(SteelData(HV=hardness))

    f1, f2 = tuple(np.sort(load_levels[np.argsort(np.abs(load_levels - load))][0:2]))
    stresses = fem_data[f1] + (fem_data[f2] - fem_data[f1]) / (f2 - f1) * (load - f1)
    stresses += residual_stress
    stress_amplitude = (max(stresses) - min(stresses)) / 2
    stress_mean = (max(stresses) + min(stresses)) / 2
    return 0.5 * (kf * (stress_amplitude + stress_mean) +
                  np.sqrt(stress_amplitude ** 2 + kf ** 2 * (stress_amplitude + stress_mean) ** 2))


mesh = '1x'
pulsator_test_directory = os.path.expanduser('~/scania_gear_analysis/experimental_data/pulsator_testing/')
gearbox_test_directory = os.path.expanduser('~/scania_gear_analysis/experimental_data/gearbox_testing/')
dante_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/heat_treatment/mesh_1x/')
residual_stress_multiplier = 1.
pulsator_loads = np.array([30., 35., 40.])

CaseDepthSeries = namedtuple('CaseDepthSeries', ['case_depth', 'color'])
case_depth_series = [CaseDepthSeries(case_depth=0.8, color='r'),
                     CaseDepthSeries(case_depth=1.1, color='g')]

with open(os.path.expanduser('~/scania_gear_analysis/pickles/pulsator/tooth_root_stresses_neg.pkl')) as data_pickle:
    stress_data = pickle.load(data_pickle)
stress_data = {30: stress_data[0:2, 1], 35: stress_data[2:4, 1], 40: stress_data[4:6, 1]}

simulated_torques = np.array([0, 1000, 1200, 1400])
gearbox_stress_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_stresses/')

gearbox_stress_data = {'pos': {0.: np.array([0., 0.])}, 'neg': {0.: np.array([0., 0.])}}
for tooth in gearbox_stress_data:
    for torque in simulated_torques[1:]:
        stress_pickle_name = gearbox_stress_pickle_directory + 'stresses_' + str(int(torque)) + '_Nm_' + tooth + '.pkl'
        with open(stress_pickle_name) as stress_pickle:
            stress_history = pickle.load(stress_pickle)
        gearbox_stress_data[tooth][torque] = np.array([np.min(stress_history), np.max(stress_history)])

gearbox_test_results = np.genfromtxt(gearbox_test_directory + 'test_results.dat', delimiter=',')
gearbox_failures = gearbox_test_results[gearbox_test_results[:, 2] == -1]
gearbox_run_outs = gearbox_test_results[gearbox_test_results[:, 2] != -1]

for serie in case_depth_series:
    cd = serie.case_depth
    with open(dante_pickle_directory + 'dante_results_' +
              str(cd).replace('.', '_') + '_root.pkl') as pickle_handle:
        root_data = pickle.load(pickle_handle)

    name = pulsator_test_directory + 'case_depth_' + str(cd)
    name = name.replace('.', '_')
    test_data = TestResults(name + '.dat')
    for force, data in test_data.get_test_results().iteritems():
        findley_stress = calculate_findley_stress(stress_data, pulsator_loads, force, root_data)
        if data['survivors']:
            plt.semilogx(2e6, findley_stress, serie.color + 'o', ms=12)

        for failure_cycle in data['failures']:
            plt.semilogx(failure_cycle, findley_stress, serie.color + 'x', ms=12, mew=2)

    for tooth in ['pos', 'neg']:
        for gearbox_data in gearbox_test_results:

            findley_stress = calculate_findley_stress(gearbox_stress_data[tooth], simulated_torques,
                                                      gearbox_data[0]/5, root_data)
            print findley_stress, gearbox_data[0]/5
            if gearbox_data[2] == -1:
                plt.semilogx(gearbox_data[-1], findley_stress, serie.color + 'x', ms=16, mew=2)
            else:
                plt.semilogx(gearbox_data[-1], findley_stress, serie.color + 'o', ms=16)
plt.show()
