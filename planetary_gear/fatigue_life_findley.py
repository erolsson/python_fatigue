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


mesh = '1x'
pulsator_test_directory = os.path.expanduser('~/scania_gear_analysis/experimental_data/pulsator_testing/')
dante_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/heat_treatment/mesh_1x/')
residual_stress_multiplier = 0.57
pulsator_loads = np.array([30., 35., 40.])

CaseDepthSeries = namedtuple('CaseDepthSeries', ['case_depth', 'color'])
case_depth_series = [CaseDepthSeries(case_depth=0.5, color='b'),
                     CaseDepthSeries(case_depth=0.8, color='r'),
                     CaseDepthSeries(case_depth=1.1, color='g'),
                     CaseDepthSeries(case_depth=1.4, color='k')]

with open(os.path.expanduser('~/scania_gear_analysis/pickles/pulsator/tooth_root_stresses_neg.pkl')) as data_pickle:
    stress_data = pickle.load(data_pickle)
stress_data = {30: stress_data[0:2, 1], 35: stress_data[2:4, 1], 40: stress_data[4:6, 1]}

for serie in case_depth_series:
    cd = serie.case_depth
    with open(dante_pickle_directory + 'dante_results_' +
              str(cd).replace('.', '_') + '_root.pkl') as pickle_handle:
        root_data = pickle.load(pickle_handle)
    residual_stress = root_data['S'][0] +157
    print residual_stress
    hardness = root_data['HV'][0]
    kf = SS2506.findley_k(SteelData(HV=hardness))

    name = pulsator_test_directory + 'case_depth_' + str(cd)
    name = name.replace('.', '_')
    test_data = TestResults(name + '.dat')
    for load, data in test_data.get_test_results().iteritems():
        f1, f2 = tuple(np.sort(pulsator_loads[np.argsort(np.abs(pulsator_loads - load))][0:2]))
        stresses = stress_data[f1] + (stress_data[f2] - stress_data[f1])/(f2 - f1)*(load - f1)
        stresses += residual_stress
        stress_amplitude = (max(stresses) - min(stresses))/2
        stress_mean = (max(stresses) + min(stresses))/2
        findley_stress = 0.5 * (kf * (stress_amplitude + stress_mean) +
                                np.sqrt(stress_amplitude ** 2 + kf ** 2 * (stress_amplitude + stress_mean) ** 2))

