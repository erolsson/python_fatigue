from collections import namedtuple
import pickle
import os

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

from materials.gear_materials import SS2506
from materials.gear_materials import SteelData

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

dante_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/heat_treatment/mesh_1x/')
residual_stress_multiplier = 1.
pulsator_loads = np.array([30., 35., 40.])


PulsatorTest = namedtuple('PulsatorTest', ['case_depth', 'fatigue_limit', 'color'])
pulsator_tests = [PulsatorTest(case_depth=0.5, fatigue_limit=30.5, color='b'),
                  PulsatorTest(case_depth=0.8, fatigue_limit=31.5, color='r'),
                  PulsatorTest(case_depth=1.1, fatigue_limit=34., color='g'),
                  PulsatorTest(case_depth=1.4, fatigue_limit=35.4, color='k')]

with open(os.path.expanduser('~/scania_gear_analysis/pickles/pulsator/tooth_root_stresses_neg.pkl')) as data_pickle:
    stress_data = pickle.load(data_pickle)
stress_data = {30: stress_data[0:2, 1], 35: stress_data[2:4, 1], 40: stress_data[4:6, 1]}

for pulsator_test in pulsator_tests:
    with open(dante_pickle_directory + 'dante_results_' +
              str(pulsator_test.case_depth).replace('.', '_') + '_root.pkl') as pickle_handle:
        root_data = pickle.load(pickle_handle)
    residual_stress = root_data['S'][0]*residual_stress_multiplier
    hardness = root_data['HV'][0]

    f1, f2 = tuple(np.sort(pulsator_loads[np.argsort(np.abs(pulsator_loads - pulsator_test.fatigue_limit))][0:2]))
    stresses = stress_data[f1] + (stress_data[f2] - stress_data[f1])/(f2 - f1)*(pulsator_test.fatigue_limit - f1)
    stresses += residual_stress
    stress_amplitude = (max(stresses) - min(stresses))/2
    stress_mean = (max(stresses) + min(stresses))/2

    kw = hardness/1000
    kf = SS2506.findley_k(SteelData(HV=hardness))

    winderlich_stress = stress_amplitude + kw*stress_mean
    findley_stress = 0.5*(kf*(stress_amplitude+stress_mean) +
                          np.sqrt(stress_amplitude**2 + kf**2*(stress_amplitude+stress_mean)**2))

    plt.plot(stress_mean, winderlich_stress, pulsator_test.color + 'o', ms=12)
    plt.plot(stress_mean, findley_stress, pulsator_test.color + 's', ms=12)


plt.xlabel('Mean stress [MPa]')
plt.ylabel('Effective fatigue stress [MPa]')
plt.grid(True)
plt.show()
