from collections import namedtuple
import os
import pickle

import numpy as np

from scipy.optimize import fmin

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
HRC_austenite = np.array([22., 24., 30., 50., 50.])
HRC_T_martensite1 = np.array([50, 55., 62.7, 70., 72.])

austenite_par = [22.,  24.,  40.,  50,  50.]
martensite_par = [50, 57, 61.5, 71, 74]


def hardness_residual(par, *data):
    residual = 0
    aust_params = 1 * HRC_austenite
    mart_params = par[1:]

    aust_params[3:-1] = par[0:1]
    aust_params = np.abs(aust_params)
    for opt_data in data:
        hardness_exp, carbon, aust, mart, remaining_hardness = opt_data

        carbon_threshold = 0.002
        hardness_exp = hardness_exp[carbon > carbon_threshold]

        aust = aust[carbon > carbon_threshold]
        mart = mart[carbon > carbon_threshold]
        remaining_hardness = remaining_hardness[carbon > carbon_threshold]
        carbon = carbon[carbon > carbon_threshold]

        hrc_aust = np.interp(carbon, carbon_levels, aust_params)*aust
        hrc_mart = np.interp(carbon, carbon_levels, mart_params)*mart

        hardness_sim = remaining_hardness + hrc_aust + hrc_mart
        residual += np.sum((hardness_exp - hardness_sim)**2)

    print mart_params, aust_params, residual
    return residual


data_sets = []
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

        plt.figure(j + 2)
        plt.plot(dante_data['r'], au, simulation.color, lw=2)

        plt.figure(j + 4)
        plt.plot(dante_data['r'], c, simulation.color, lw=2)

        plt.figure(j + 6)
        plt.plot(dante_data['r'], m, simulation.color, lw=2)

        c_sim = np.interp(distance_from_surface, dante_data['r'], dante_data['Carbon'])
        au_sim = np.interp(distance_from_surface, dante_data['r'], dante_data['Austenite'])
        mart_sim = np.interp(distance_from_surface, dante_data['r'], dante_data['T-Martensite'])
        simulated_hardness = HV2HRC(np.interp(distance_from_surface, dante_data['r'], dante_data['HV']))
        hardness_from_other_phases = simulated_hardness - np.interp(c_sim, carbon_levels, HRC_austenite)*au_sim - \
            np.interp(c_sim, carbon_levels, HRC_T_martensite1)*mart_sim

        data_set = HV2HRC(exp_data), c_sim, au_sim, mart_sim, hardness_from_other_phases
        data_sets.append(data_set)

        c_sim = dante_data['Carbon']
        au_sim = dante_data['Austenite']
        mart_sim = dante_data['T-Martensite']
        simulated_hardness = HV2HRC(dante_data['HV'])
        plt.figure(j)

        hardness_from_other_phases = simulated_hardness - np.interp(c_sim, carbon_levels, HRC_austenite) * au_sim - \
            np.interp(c_sim, carbon_levels, HRC_T_martensite1) * mart_sim
        plt.plot(dante_data['r'], HRC2HV(hardness_from_other_phases), simulation.color)
        new_hrc_aust = np.interp(c_sim, carbon_levels, austenite_par)*au_sim
        new_hrc_mart = np.interp(c_sim, carbon_levels, martensite_par)*mart_sim
        new_hardness = HRC2HV(hardness_from_other_phases + new_hrc_mart + new_hrc_aust)

        plt.plot(dante_data['r'], new_hardness, ':' + simulation.color, lw=2)

plt.figure(100)
plt.plot(carbon_levels, HRC_austenite, 'b', lw=2)
plt.plot(carbon_levels, HRC_T_martensite1, 'r', lw=2)
carb = np.linspace(0.0, 1.0, 1000, endpoint=True)/100


# fit_par = fmin(hardness_residual, np.append(HRC_austenite[3:-1], HRC_T_martensite1), tuple(data_sets),
#               maxiter=1e6, maxfun=1e6)

# print fit_par
plt.show()
