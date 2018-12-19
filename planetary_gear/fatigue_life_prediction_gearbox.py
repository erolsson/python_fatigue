import os
import pickle

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from materials.gear_materials import SteelData

from weakest_link.weakest_link_gear import FEM_data
from weakest_link.weakest_link_gear import WeakestLinkEvaluatorGear

from multiprocesser.multiprocesser import multi_processer

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def calculate_life(load, cd, size_factor):
    tooth_data = {'stress': [], 'HV': []}
    for tooth_part in ['left', 'right']:
        findley_file_name = 'findley/gear_box/findley_tooth_' + tooth_part + '_CD=' + \
                            str(cd).replace('.', '_') + '_Pamp=' + str(load).replace('.', '_') + 'Nm.pkl'
        with open(data_directory + findley_file_name) as findley_pickle:
            stress_data = pickle.load(findley_pickle)
        stress_data = stress_data.reshape(stress_data.shape[0]/8, 8)
        tooth_data['stress'].append(stress_data)

    with open(data_directory + 'dante/data_' + str(cd).replace('.', '_') + '.pkl') as dante_pickle:
        dante_data = pickle.load(dante_pickle)

    hardness = dante_data['HV'].reshape(dante_data['HV'].shape[0]/8, 8)

    stress = np.concatenate(tooth_data['stress'])
    hardness = np.concatenate([hardness, hardness])

    with open(data_directory + 'geometry/nodal_positions.pkl') as position_pickle:
        position = pickle.load(position_pickle)
    position = position.reshape(position.shape[0]/8, 8, 3)
    position = np.concatenate([position, position])

    fem_volume = FEM_data(stress=stress,
                          steel_data=SteelData(HV=hardness),
                          nodal_positions=position)

    wl_evaluator = WeakestLinkEvaluatorGear(data_volume=fem_volume, data_area=None, size_factor=size_factor)
    lives = 0*pf_levels
    for it, pf in enumerate(pf_levels):
        lives[it] = wl_evaluator.calculate_life_time(pf=pf, haiback=haiback)
    pf = wl_evaluator.calculate_pf()
    return pf, lives


if __name__ == '__main__':
    haiback = False
    pf_levels = np.array([0.5])
    mesh = '1x'
    test_directory = os.path.expanduser('~/scania_gear_analysis/experimental_data/gearbox_testing/')
    data_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' + mesh + '/')

    test_results = np.genfromtxt(test_directory + 'test_results.dat', delimiter=',')
    root_failures = test_results[test_results[:, 2] == -1]
    root_run_outs = test_results[test_results[:, 2] != -1]

    plt.semilogx(root_run_outs[:, -1], root_run_outs[:, 2], 'ko', ms=12, mew=2, mfc='w')
    plt.semilogx(root_failures[:, -1], root_failures[:, 1], 'kx', ms=12, mew=2, mfc='w')

    torques = np.arange(900., 1600., 100.)
    case_depths = np.array([1.1])

    for sectors in [2, 2]:
        job_list = []
        for torque in torques:
            job_list.append([calculate_life, [torque, 1.1, sectors], {}])

        wl_data = multi_processer(job_list, timeout=600, delay=0., cpus=8)

        simulated_pf = 0*torques
        N = np.zeros((torques.shape[0], len(pf_levels)))

        for force_level in range(torques.shape[0]):
            simulated_pf[force_level] = wl_data[force_level][0]
            N[force_level, :] = wl_data[force_level][1]

        for pf_level, (pf_val, color) in enumerate(zip(pf_levels, 'brg')):
            data_to_plot = np.vstack((N[:, pf_level].T, torques.T))
            plt.plot(data_to_plot[0, :], data_to_plot[1, :], '--' + color, lw=2)

    plt.ylabel('Torque [Nm]')
    plt.xlabel('Cycles')
    plt.xlim(1e4, 1e7)
    plt.ylim(800, 1600)
    plt.grid(True)

    plt.show()
