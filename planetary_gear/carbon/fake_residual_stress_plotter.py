import os
import pickle

import matplotlib.pyplot as plt
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def plot_data(pickle_name, line_style):
    with open(pickle_name) as data_pickle:
        data = pickle.load(data_pickle)
    plt.plot(data[:, 0], data[:, 1], line_style, lw=2)
    return data

for cd, c in zip(['0_5', '0_8', '1_1', '1_4'], ['r', 'b', 'g', 'k']):
    pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/')
    plot_data(pickle_directory + 'fake_heat_treatment/residual_stresses_' + cd + '.pkl', '--' + c)
    plot_data(pickle_directory + 'old_heat_treatment/residual_stresses_' + cd + '.pkl', '-' + c)

plt.show()
