import pickle

import numpy as np

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

fake_pickle_name = '/scratch/users/erik/scania_gear_analysis/pickles/fake_heat_treatment/residual_stresses_1_4.pkl'
old_pickle_name = '/scratch/users/erik/scania_gear_analysis/pickles/old_heat_treatment/residual_stresses_1_4.pkl'

plot_data(fake_pickle_name, '--b')
plot_data(old_pickle_name, 'b')
plt.show()
