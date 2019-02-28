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
plt.plot(experimental_data[:, 0], experimental_data[:, 1], 'b', lw=2)


for carb in [0.75, 0.8]:
    for temp in [180, 200]:
        simulation_pickle = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/'
                                               'dante/utmis_smoothdante_path_tempering_2h_' + str(temp) + '_' +
                                               str(carb).replace('.', '_') + 'C' + '.pkl')
        with open(simulation_pickle, 'r') as pickle_handle:
            dante_data = pickle.load(pickle_handle)

        label = 'Temp ' + str(temp) + 'C=' + str(carb)

        plt.plot(dante_data['r'][:-1], dante_data['HV'][:-1], '--', lw=2, label=label)


plt.show()
