import os

import numpy as np
import pickle
import matplotlib.pyplot as plt

plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

with open(os.path.expanduser('~/scania_gear_analysis/pickles/pulsator/tooth_root_stresses_neg.pkl')) as data_pickle:
    stress_data = pickle.load(data_pickle)

forces = np.array([30, 35, 40])

plt.plot(forces, stress_data[0:5:2, 1], 'o', ms=12)
plt.plot(forces, stress_data[1:6:2, 1], 's', ms=12)


f = np.linspace(30, 40, 100)
s = stress_data[4, 1]/40*f
plt.plot(f, s)
s = stress_data[5, 1]/40*f
plt.plot(f, s)

plt.show()
