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

with open(os.path.expanduser('~/scania_gear_analysis/pickles/pulsator/tooth_root_stresses_pos.pkl')) as data_pickle:
    stress_data = pickle.load(data_pickle)
print stress_data
