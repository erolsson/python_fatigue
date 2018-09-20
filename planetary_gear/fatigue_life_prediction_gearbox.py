import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from fatigue_life_prediction_pulsator import calculate_life

from multiprocesser.multiprocesser import multi_processer

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

if __name__ == '__main__':
    haiback = True

    mesh = '1x'
    test_directory = os.path.expanduser('~/scania_gear_analysis/experimental_data/gearbox_testing/')

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
