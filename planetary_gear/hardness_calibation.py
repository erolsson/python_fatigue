from collections import namedtuple
import os
import pickle

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

from materials.hardess_convertion_functions import HRC2HV
from materials.hardess_convertion_functions import HV2HRC

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

pickle_path = os.path.expanduser('~/scania_gear_analysis/pickles/heat_treatment/mesh_1x/root_data/tempering_2h_180C/')
experimental_path = os.path.expanduser('~/scania_gear_analysis/experimental_data/hardness/')
Simulation = namedtuple('Simulation', ['cd', 'color', 'sym'])
simulations = [Simulation(cd=0.5, color='b', sym='o'), Simulation(cd=0.8, color='r', sym='s'),
               Simulation(cd=1.1, color='g', sym='d'), Simulation(cd=1.4, color='k', sym='p')]

experimental_data = np.genfromtxt(experimental_path + 'hardness_profiles.csv', delimiter=',', skip_header=1)
distance_from_surface = experimental_data[:, 0]

carbon_levels = np.arange(0.2, 1.2, 0.2)/100
HRC_austenite = np.array([22., 24., 40., 44., 46.])
HRC_T_martensite1 = np.array([47., 59., 64., 67., 68.])


def hardness_residual(par, *data):
    pass


for i, simulation in enumerate(simulations):
    pickle_name = pickle_path + 'dante_results_' + str(simulation.cd).replace('.', '_')
    for j, data_path in enumerate(['flank', 'root']):
        plt.figure(j)
        with open(pickle_name + '_' + data_path + '.pkl', 'r') as pickle_handle:
            dante_data = pickle.load(pickle_handle)

        plt.plot(dante_data['r'], dante_data['HV'], '--' + simulation.color, lw=2)
        exp_data = experimental_data[:, i*2 + j + 3]

        plt.plot(distance_from_surface, exp_data, '-' + simulation.sym + simulation.color,
                 lw=2, ms=12, mec='k', label='CHD = ' + str(simulation.cd) + ' mm')

        au = dante_data['Austenite']
        c = dante_data['Carbon']
        m = dante_data['T-Martensite']
        hrc_sim = HV2HRC(dante_data['HV'])
plt.show()
