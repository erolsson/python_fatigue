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
    tooth_stresses = []
    for tooth_part in ['tooth_left', 'tooth_right']:
        findley_file_name = 'findley/gear_box/findley_' + tooth_part + '_CD=' + str(case_depth).replace('.', '_') + \
                            '_Pamp=' + str(load).replace('.', '_') + 'kN.pkl'
        with open(data_directory + findley_file_name) as findley_pickle:
            tooth_stresses.append(pickle.load(findley_pickle))
    stress = np.zeros(tooth_stresses[0].shape[0] + tooth_stresses[0].shape[0])
    stress[0:tooth_stresses[0].shape[0]] = tooth_stresses[0]
    stress[tooth_stresses[0].shape[0]:tooth_stresses[1].shape[0]] = tooth_stresses[1]
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
    pf_levels = np.array([0.25, 0.5, 0.75])
    mesh = '1x'
    test_directory = os.path.expanduser('~/scania_gear_analysis/experimental_data/gearbox_testing/')
    data_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' + mesh + '/')

    test_results = np.genfromtxt(test_directory + 'test_results.dat', delimiter=',')
    root_failures = test_results[test_results[:, 2] == -1]
    root_run_outs = test_results[test_results[:, 2] != -1]

    plt.semilogx(root_run_outs[:, -1], root_run_outs[:, 2], 'ko', ms=12, mew=2, mfc='w')
    plt.semilogx(root_failures[:, -1], root_failures[:, 1], 'kx', ms=12, mew=2, mfc='w')

    torques = np.arange(900, 1600, 1000)
    case_depths = [0.8, 1.1]

    for case_depth in case_depths:
        job_list = []
        for torque in torques:


    plt.ylabel('Torque [Nm]')
    plt.xlabel('Cycles')
    plt.xlim(1e4, 1e7)
    plt.ylim(800, 1600)
    plt.grid(True)

    plt.show()
