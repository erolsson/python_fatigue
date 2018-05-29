import pickle

import numpy as np

import matplotlib.pyplot as plt
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

# Plot residual stresses
plt.figure(0)
residual_stress_pickle = open('pickles/tooth_root_stresses/residual_stresses.pkl')
residual_stress_data = pickle.load(residual_stress_pickle)
residual_stress_pickle.close()

z = residual_stress_data[:, 0]

for case_idx, case_depth in enumerate([0.5, 0.8, 1.1, 1.4]):
    s = -residual_stress_data[:, case_idx + 1] - 150
    plt.plot(z, s, lw=2, label='CDH = ' + str(case_depth) + ' mm')

plt.xlim(0, z[-1])
plt.xlabel('Distance along tooth [mm]')
plt.ylabel('Residual stress [MPa]')
plt.grid(True)
plt.legend(loc='best')
plt.show()
