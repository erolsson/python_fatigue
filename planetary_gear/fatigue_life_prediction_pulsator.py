import os
import pickle

import numpy as np
import matplotlib.pyplot as plt

from multiprocesser.multiprocesser import multi_processer

from materials.gear_materials import SS2506
from materials.gear_materials import SteelData

from planetary_gear.test_results import TestResults

from testing.test_results_functions import plot_test_results

from weakest_link.weakest_link_gear import FEM_data
from weakest_link.weakest_link_gear import WeakestLinkEvaluatorGear

plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def calculate_life(findley_file_name, cd, size_factor):
    with open(data_directory + findley_file_name) as findley_pickle:
        stress = pickle.load(findley_pickle)
    n_vol = stress.shape[0]

    with open(data_directory + 'dante/data_' + str(cd).replace('.', '_') + '.pkl') as dante_pickle:
        dante_data = pickle.load(dante_pickle)
    steel_data_volume = SteelData(HV=dante_data['HV'].reshape(n_vol / 8, 8))

    with open(data_directory + 'geometry/nodal_positions.pkl') as position_pickle:
        position = pickle.load(position_pickle)

    fem_volume = FEM_data(stress=stress.reshape(n_vol / 8, 8),
                          steel_data=steel_data_volume,
                          nodal_positions=position.reshape(n_vol / 8, 8, 3))

    wl_evaluator = WeakestLinkEvaluatorGear(data_volume=fem_volume, data_area=None, size_factor=size_factor)
    lives = 0*pf_levels
    for it, pf in enumerate(pf_levels):
        lives[it] = wl_evaluator.calculate_life_time(pf=pf, haiback=haiback)
    pf = wl_evaluator.calculate_pf()
    return pf, lives


if __name__ == '__main__':
    haiback = True

    case_depths = [0.5, 0.8, 1.1, 1.4]
    # case_depths = [1.4]
    pf_levels = np.array([0.25, 0.5, 0.75])
    sim_forces = np.arange(30., 41., 1.)
    mesh = '1x'
    test_directory = os.path.expanduser('~/scania_gear_analysis/experimental_data/pulsator_testing/')
    data_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' + mesh + '/')

    for i, case_depth in enumerate(case_depths):
        # Plotting test results
        name = test_directory + 'case_depth_' + str(case_depth)
        name = name.replace('.', '_')
        testData = TestResults(name + '.dat')

        data = testData.get_test_results()
        plot_test_results(data, i, 'b', [1E4, 1E7, 29, 40],
                          ylab='$P_{a}$ [kN]',
                          plot_fatigue_line=False,
                          title='Experiment')

        N = np.zeros((sim_forces.shape[0], len(pf_levels)))

        # Calculating life time at specific pf
        job_list = []
        for force in sim_forces:
            data_file_name = 'findley/pulsator/findley_CD=' + str(case_depth).replace('.', '_') + \
                                '_Pamp=' + str(force).replace('.', '_') + 'kN.pkl'
            job_list.append((calculate_life, [data_file_name, case_depth, 4], {}))

        wl_data = multi_processer(job_list, timeout=600, delay=0., cpus=8)

        simulated_pf = 0 * sim_forces
        for force_level in range(sim_forces.shape[0]):
            simulated_pf[force_level] = wl_data[force_level][0]
            N[force_level, :] = wl_data[force_level][1]

        # Plotting life curves
        data_to_write = []
        for pf_level, (pf_val, color) in enumerate(zip(pf_levels, 'brg')):
            if haiback:
                data_to_plot = np.vstack((N[:, pf_level].T, sim_forces.T))
            else:
                force_at_pf = np.interp(pf_val, simulated_pf, sim_forces)
                data_to_plot = np.vstack((N[sim_forces > force_at_pf, pf_level].T, sim_forces[sim_forces > force_at_pf].T))
                data_to_plot = np.hstack((np.array([[1E7, np.exp(SS2506.ne)],
                                                    [force_at_pf, force_at_pf]]),
                                          data_to_plot))
            plt.plot(data_to_plot[0, :], data_to_plot[1, :], '--' + color, lw=2)
            data_to_write.append(data_to_plot)

        n = max(data_to_write, key=lambda x: x.shape[1]).shape[1]
        write_array = np.zeros((n, 6))

        for pf_level, data in enumerate(data_to_write):
            write_array[:, 2*pf_level] = data[0, 0]
            write_array[:, 2 * pf_level+1] = data[1, 0]
            write_array[n-data.shape[1]:, 2*pf_level:2*pf_level+2] = data.T

        load_cycles = np.log(np.array([write_array[-1, 0], write_array[-1, 2], write_array[-1, 4]]))
        long_life = (np.linspace(load_cycles[-1], np.log(1e7), 100))
        load_cycles = np.hstack((load_cycles, long_life))
        data_to_write = np.zeros((load_cycles.shape[0], 4))
        data_to_write[:, 0] = np.exp(load_cycles)
        for j in range(3):
            data_to_write[:, j+1] = np.interp(load_cycles, np.log(write_array[::-1, 2*j]), write_array[::-1, 2*j+1],
                                              left=41)
            plt.plot(np.exp(load_cycles), data_to_write[:, j+1], ':')
        print data_to_write
        np.savetxt(str(case_depth).replace('.', '_') + 'lifeData.csv', data_to_write, delimiter=',')
    plt.show()
