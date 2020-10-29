import os
import pickle

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

from python_fatigue.materials.hardess_convertion_functions import HRC2HV

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

experimental_data = np.genfromtxt('hardness_profile', delimiter=',')
plt.plot(experimental_data[:, 0], experimental_data[:, 1], 'b', lw=2)

simulation_pickle = os.path.expanduser('~/utmis_specimens/smooth/heat_treatment_data/utmis_smooth_dante_path_y.pkl')
with open(simulation_pickle, 'rb') as pickle_handle:
    dante_data = pickle.load(pickle_handle, encoding='latin1')

plt.plot(dante_data['r'][:-1], HRC2HV(dante_data['SDV_HARDNESS'][:-1]), '--', lw=2)

plt.figure(2)
plt.plot(dante_data['r'][:-1], dante_data['SDV_CARBON'][:-1], '--', lw=2)

plt.figure(3)
plt.plot(dante_data['r'][:-1], dante_data['SDV_AUSTENITE'][:-1], '--', lw=2)

plt.show()
