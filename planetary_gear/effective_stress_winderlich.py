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
residual_stress_multiplier = 0.57
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

    plt.figure(0)
    plt.plot(stress_mean, winderlich_stress, pulsator_test.color + 'o', ms=12)
    plt.plot(stress_mean, findley_stress, pulsator_test.color + 's', ms=12)

    plt.figure(1)
    plt.plot(stress_mean, stress_amplitude, pulsator_test.color + 'o', ms=12)


torques = np.array([1000., 1200., 1400.])
simulated_torques = np.array([0, 1000, 1200, 1400])
stress_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_stresses/')
for cd, color in zip([0.8, 1.1], ['r', 'g']):
    with open(dante_pickle_directory + 'dante_results_' +
              str(cd).replace('.', '_') + '_root.pkl') as pickle_handle:
        root_data = pickle.load(pickle_handle)
    residual_stress = root_data['S'][0] * residual_stress_multiplier
    hardness = root_data['HV'][0]
    kw = hardness / 1000
    kf = SS2506.findley_k(SteelData(HV=hardness))
    for torque in torques:
        f1, f2 = tuple(np.sort(simulated_torques[np.argsort(np.abs(simulated_torques - torque))][0:2]))
        for name in ['pos', 'neg']:
            stresses = []
            for level in (f1, f2):
                stress_pickle_name = stress_pickle_directory + 'stresses_' + str(int(torque)) + '_Nm_' + name + '.pkl'
                with open(stress_pickle_name) as stress_pickle:
                    stresses.append(pickle.load(stress_pickle)[:, 1])

            stress_history = stresses[0] + (stresses[1]-stresses[0])/(f2-f1)*(torque - f1)
            stress_history += residual_stress
            stress_amplitude = (max(stress_history) - min(stress_history))/2
            stress_mean = (max(stress_history) + min(stress_history))/2

            print stress_amplitude, stress_mean
            winderlich_stress = stress_amplitude + kw*stress_mean
            print kw
            findley_stress = 0.5*(kf*(stress_amplitude+stress_mean) +
                                  np.sqrt(stress_amplitude**2 + kf**2*(stress_amplitude+stress_mean)**2))

            plt.figure(0)
            plt.plot(stress_mean, winderlich_stress, color + 'o', ms=12)
            plt.plot(stress_mean, findley_stress, color + 's', ms=12)

            plt.figure(1)
            plt.plot(stress_mean, stress_amplitude, color + 'o', ms=12)


plt.figure(0)
plt.xlabel('Mean stress [MPa]')
plt.ylabel('Effective fatigue stress [MPa]')
plt.grid(True)

plt.figure(1)
plt.xlabel('Mean stress [MPa]')
plt.ylabel('Amplitude stress [MPa]')
plt.grid(True)
plt.show()
