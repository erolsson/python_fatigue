import pickle

import numpy as np

import matplotlib.pyplot as plt
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

# Loading the experimental data
experimental_data = np.genfromtxt('../experimental_data/carbon_profile.csv', delimiter=';')

for fig_idx, path_name in enumerate(['root', 'flank']):
    plt.figure(fig_idx)
    sim_pickle = open('../pickles/carbon_' + path_name + '_sim.pkl')
    sim_data = pickle.load(sim_pickle)
    sim_pickle.close()

    for case_idx
