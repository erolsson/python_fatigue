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
        fig = plt.figure(fig_idx)
        sim_pickle = open('../pickles/carbon_' + path_name + '_sim.pkl', 'rb')
        sim_data = pickle.load(sim_pickle)
        sim_pickle.close()

        for sim_cd in sim_data.keys():
            plt.plot(sim_data[sim_cd][:, 0], sim_data[sim_cd][:, 1]*100, '--' + plot_symbols[sim_cd][0], lw=2)

            if path_name == 'flank':
                plt.plot(exp_results[sim_cd][:, 0], exp_results[sim_cd][:, 1], '-' + plot_symbols[sim_cd], lw=2, ms=12)

            plt.plot([-2, -1], [-1, -1], '-' + plot_symbols[sim_cd], lw=2, label='CHD = ' + str(sim_cd) + ' mm', ms=12)
        plt.plot([-2, -1], [-1, -1], '-w', lw=2, label=' ')

        plt.plot([-2, -1], [-1, -1], '-', lw=2, label='Experiment')
        plt.plot([-2, -1], [-1, -1], '--', lw=2, label='Simulation')
        plt.xlim(0, 2)
        plt.ylim(0.2, 1)
        fig.set_size_inches(12, 6, forward=True)
        ax = plt.subplot(111)
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, 0.55, box.height])
        plt.xlabel('Distance from surface [mm]')
        plt.ylabel('Carbon content [\%]')
        plt.grid(True)
        legend = ax.legend(loc='upper left', numpoints=1, bbox_to_anchor=(1, 1.035))
        plt.gca().add_artist(legend)

    plt.show()

