import pickle
import numpy as np

import matplotlib.pyplot as plt
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


pickle_path = '/scratch/users/erik/scania_gear_analysis/pickles/heat_treatment/mesh_1x/'

for cd in np.linspace(0.5, 1.4, 4, endpoint=True):
    pickle_name =
