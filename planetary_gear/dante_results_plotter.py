from collections import namedtuple
import pickle
import os

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


pickle_path = os.path.expanduser('~/scania_gear_analysis/pickles/heat_treatment/mesh_1x/root_data/'
                                 'tempering_72min_200C/')
experiment_path = os.path.expanduser('~/scania_gear_analysis/experimental_data/')
Simulation = namedtuple('Simulation', ['cd', 'color', 'sym'])
simulations = [Simulation(cd=0.5, color='b', sym='o'), Simulation(cd=0.8, color='r', sym='s'),
               Simulation(cd=1.1, color='g', sym='d'), Simulation(cd=1.4, color='k', sym='p')]

experimental_hardness = np.genfromtxt(experiment_path + 'hardness/hardness_profiles.csv', delimiter=',',
                                      skip_header=1)
residual_stresses_ivf = np.genfromtxt(experiment_path + 'residual_stresses/residual_stresses_ivf.csv')
distance_from_surface = experimental_hardness[:, 0]

legend_handles = [[], [], [], []]

figures = []

# Reading the experimental carbon profile file
with open(experiment_path + '/carbon_profiles/carbon_profiles.csv', 'rb') as carbon_file:
    file_lines = carbon_file.readlines()
    carbon_experimental_data = np.zeros((len(file_lines), 5))
    for i, line in enumerate(file_lines):
        j = 0
        for word_count, word in enumerate(line.split(b'\t')):
            if word_count in [1, 3, 4, 5, 6]:
                try:
                    carbon_experimental_data[i, j] = float(word)
                except ValueError:
                    carbon_experimental_data[i, j] = np.nan
                j += 1

for i, simulation in enumerate(simulations):
    pickle_name = pickle_path + 'dante_results_' + str(simulation.cd).replace('.', '_')
    for j, data_path in enumerate(['flank', 'root']):
        with open(pickle_name + '_' + data_path + '.pkl', 'rb') as pickle_handle:
            dante_data = pickle.load(pickle_handle, encoding='latin1')

        figures.append(plt.figure(2*j))
        plt.plot(dante_data['r'], dante_data['HV'], '--' + simulation.color, lw=2)
        exp_data = experimental_hardness[:, i*2 + j + 3]

        leg_h = plt.plot(distance_from_surface, exp_data, '-' + simulation.sym + simulation.color,
                         lw=2, ms=12, mec='k', label='CHD = ' + str(simulation.cd) + ' mm')
        legend_handles[2*j].append(leg_h[0])

        if j == 0:
            plt.figure(7)
            plt.plot(dante_data['r'], dante_data['S'][:, 2], '--' + simulation.color, lw=2,
                     label='CHD = ' + str(simulation.cd) + ' mm')
            plt.plot(residual_stresses_ivf[:, i*3], residual_stresses_ivf[:, i*3+1], simulation.color, lw=2)

            plt.figure(1)
            plt.plot(residual_stresses_ivf[:, i*3], residual_stresses_ivf[:, i*3+2], simulation.color, lw=2)
        figures.append(plt.figure(1 + 2*j))
        leg_h = plt.plot(dante_data['r'], dante_data['normal_stress'], '--' + simulation.color, lw=2,
                         label='CHD = ' + str(simulation.cd) + ' mm')
        legend_handles[1 + 2*j].append(leg_h[0])
        if j == 1:
            plt.figure(6)
            plt.plot(dante_data['r'], dante_data['SDV_CARBON']*100, '--' + simulation.color, lw=2)
            plt.plot(carbon_experimental_data[:, 0], carbon_experimental_data[:, i+1], simulation.color, lw=2)

for i in range(2):
    fig = plt.figure(2*i)
    legend_handles[2*i].append(plt.plot([-2, -1], [0, 0], 'w', label=r'$\quad$')[0])
    legend_handles[2*i].append(plt.plot([-2, -1], [0, 0], 'k', lw=2, label='Experiment')[0])
    legend_handles[2*i].append(plt.plot([-2, -1], [0, 0], '--k', lw=2, label='Simulation')[0])
    plt.ylim(300, 800)
    plt.ylabel('Hardness [HV]')
    fig.set_size_inches(12., 6., forward=True)
    ax = plt.subplot(111)
    box = ax.get_position()
    ax.set_position([0.1, 0.12, 0.6, box.height])
    legend = ax.legend(handles=legend_handles[2*i], numpoints=1, loc='upper left', bbox_to_anchor=(1., 1.035))
    plt.gca().add_artist(legend)

for figure in range(4):
    fig = plt.figure(figure)
    plt.grid(True)
    plt.xlabel('Distance from surface [mm]')
    plt.xlim(0, 3)

for j, data_path in enumerate(['flank', 'root']):
    plt.figure(2*j)
    plt.savefig('hardness_' + data_path + '.png')
    plt.figure(2*j+1)
    plt.legend(handles=legend_handles[2*j+1], loc='best')
    plt.ylabel('Residual stress [MPa]')
    plt.tight_layout()
    plt.savefig('residual_stress_' + data_path + '.png')


plt.show()
