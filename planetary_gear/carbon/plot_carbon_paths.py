import pickle

import numpy as np

import matplotlib.pyplot as plt
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def create_experimental_dict_pickle():
    exp_array = np.genfromtxt('../experimental_data/carbon_profile.csv', delimiter=';')
    exp_dict = {}
    for cd_idx, cd in enumerate([0.2, 0.5, 0.8, 1.1, 1.4]):
        r = exp_array[~np.isnan(exp_array[:, cd_idx+2]), 1] - 0.05   # -0.05 for getting in the middle of the cut
        carbon = exp_array[~np.isnan(exp_array[:, cd_idx+2]), cd_idx+2]
        data_set = np.vstack((r, carbon)).T
        exp_dict[cd] = data_set
    exp_pickle = open('../pickles/carbon_exp.pkl', 'w')
    pickle.dump(exp_dict, exp_pickle)
    exp_pickle.close()

if __name__ == '__main__':
    pickle_handle = open('../pickles/carbon_exp.pkl', 'r')
    exp_results = pickle.load(pickle_handle)
    pickle_handle.close()

    plot_symbols = {0.2: 'rs', 0.5: 'bo', 0.8: 'gd', 1.1: 'kx', 1.4: 'cp'}

    for fig_idx, path_name in enumerate(['root', 'flank']):
        plt.figure(fig_idx)
        sim_pickle = open('../pickles/carbon_' + path_name + '_sim.pkl', 'rb')
        sim_data = pickle.load(sim_pickle)
        sim_pickle.close()

        for sim_cd in sim_data.keys():
            print sim_cd

