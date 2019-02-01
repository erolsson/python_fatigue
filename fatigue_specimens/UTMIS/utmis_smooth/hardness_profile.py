import os
import pickle

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

experimental_data = np.genfromtxt('hardness_profile', delimiter=',')
plt.plot(experimental_data[:, 0], experimental_data[:, 1])

simulation_pickle = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/'
                                       'utmis_smooth_dante_path.pkl')

with open(simulation_pickle, 'r') as pickle_handle:
    dante_data = pickle.load(pickle_handle)

print dante_data

plt.plot(dante_data['r'], dante_data['HV'])

plt.show()
