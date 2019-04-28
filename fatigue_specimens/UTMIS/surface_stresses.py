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

heat_treatment_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/'
                                                     'heat_treatment_data/')

mechanical_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/'
                                                 'mechanical_data/')

fatigue_limits = {'smooth': {-1: 760., 0: 424},
                  'notched': {-1: 440., 0: 237.}}

for specimen, color in zip(['smooth', 'notched'], ['b', 'r']):
    for i, path in enumerate(['y', 'z']):
        with open(heat_treatment_pickle_directory + 'utmis_' + specimen + '_dante_path_' + path
                  + '.pkl', 'r') as heat_pickle:
            heat_treatment_data = pickle.load(heat_pickle)

        with open(mechanical_pickle_directory + 'unit_load_' + specimen + '_path_' + path
                  + '.pkl', 'r') as mechanical_pickle:
            mechanical_data = pickle.load(mechanical_pickle)

        plt.figure(i)
        plt.plot(heat_treatment_data['r'], heat_treatment_data['S'])

        plt.figure(i + 2)
        plt.plot(mechanical_data[:, 0], mechanical_data[:, 1])

        plt.figure(i + 4)
        plt.plot(mechanical_data[:, 0], fatigue_limits[specimen][-1]*mechanical_data[:, 1] +
                 heat_treatment_data['S'])

        plt.figure(6)
        for R, su in fatigue_limits[specimen].iteritems():
            plt.plot(heat_treatment_data['S'] + (1+R)/(1-R)*su*mechanical_data[:, 1],
                     su*mechanical_data[:, 1], color, lw=2)

plt.show()
