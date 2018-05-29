import pickle

import numpy as np

import matplotlib.pyplot as plt
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


residual_stress_pickle = open('pickles/tooth_root_stresses/residual_stresses.pkl')
residual_stress_data = pickle.load(residual_stress_pickle)
residual_stress_pickle.close()

hardness_pickle = open('pickles/tooth_root_stresses/hardness.pkl')
hardness_data = pickle.load(hardness_pickle)
hardness_pickle.close()

mechanical_stress_pickle = open('pickles/tooth_root_stresses/mechanical_stresses.pkl')
mechanical_stress_data = pickle.load(mechanical_stress_pickle)
mechanical_stress_pickle.close()


z = residual_stress_data[:, 0]

for case_idx, case_depth in enumerate([0.5, 0.8, 1.1, 1.4]):
    s = -residual_stress_data[:, case_idx + 1] - 150
    plt.figure(0)
    plt.plot(z, s, lw=2, label='CDH = ' + str(case_depth) + ' mm')
    plt.figure(1)
    plt.plot(z, hardness_data[:, case_idx+1], lw=2, label='CDH = ' + str(case_depth) + ' mm')

plt.figure(2)
plt.plot(z, mechanical_stress_data[:, 1], lw=2)


plt.figure(0)
plt.xlim(0, z[-1])
plt.xlabel('Distance along tooth [mm]')
plt.ylabel('Residual stress [MPa]')
plt.grid(True)
plt.legend(loc='best')

plt.figure(1)
plt.xlim(0, z[-1])
plt.xlabel('Distance along tooth [mm]')
plt.ylabel('Vickers Hardness')
plt.grid(True)
plt.legend(loc='best')

plt.figure(2)
plt.xlim(0, z[-1])
plt.xlabel('Distance along tooth [mm]')
plt.ylabel('Mechanical stress [MPa]')
plt.text(3, 660, '$P_{amp}$ = 32 kN, $R=0.1$', fontsize=24)
plt.grid(True)

plt.show()
