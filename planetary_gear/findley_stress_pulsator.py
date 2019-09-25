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

mesh = '1x'
findley_a = np.array([0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4])
ratio = 0*findley_a
loads = {0.5: 31., 1.4: 31.}
for i, a800 in enumerate(findley_a):
    findley_data_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' +
                                                mesh + '/findley_tempering_2h_180C_a800=' + str(a800).replace('.', '_')
                                                + '/pulsator/')

    with open(findley_data_directory + 'findley_CD=0_5_Pamp=' + str(loads[0.5]).replace('.', '_') +
              'kN.pkl', 'r') as pickle_file:
        findley1 = pickle.load(pickle_file)

    with open(findley_data_directory + 'findley_CD=1_4_Pamp=' + str(loads[1.4]).replace('.', '_') +
              'kN.pkl', 'r') as pickle_file:
        findley2 = pickle.load(pickle_file)

    ratio[i] = np.max(findley2)/np.max(findley1)

plt.plot(findley_a, ratio)
plt.show()
