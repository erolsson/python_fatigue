import os
import pickle

from collections import namedtuple

import numpy as np

from scipy.spatial import ConvexHull

import matplotlib.pyplot as plt
import matplotlib.style

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def get_stress_values(stress_components):
    stress_tensor = np.zeros((2, 3, 3))
    stress_tensor[0, :, :] = np.diag(stress_components[0, :3])
    stress_tensor[1, :, :] = np.diag(stress_components[1, :3])

    stress_tensor[:, 0, 1] = stress_components[:, 3]
    stress_tensor[:, 1, 0] = stress_components[:, 3]

    stress_tensor[:, 0, 2] = stress_components[:, 4]
    stress_tensor[:, 2, 0] = stress_components[:, 4]

    stress_tensor[:, 1, 2] = stress_components[:, 5]
    stress_tensor[:, 2, 1] = stress_components[:, 5]

    vals, vecs = np.linalg.eig(stress_tensor[1, :, :])
    idx = np.argmax(vals)
    s_max = vals[idx]
    s_min = np.dot(np.dot(stress_tensor[0], vecs[idx]), vecs[idx])
    sm = (s_max + s_min)/2
    sa = abs(s_max - s_min)/2
    return sa, sm


if __name__ == '__main__':
    pickle_path = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/mechanical_data/')
    FEMSimulation = namedtuple('FEMSimulation', ['specimen', 'stress', 'R'])

    x_max = 5.
    simulations = [FEMSimulation('smooth', 774.0, -1), FEMSimulation('notched', 450.0, -1),
                   FEMSimulation('smooth', 440.0, 0), FEMSimulation('notched', 255.0, 0)]

    for simulation, c in zip(simulations, ['b', 'r', 'b', 'r']):
        plt.figure()
        pickle_file_name = 'utmis_' + simulation.specimen + '_' + str(simulation.stress).replace('.', '_') + '_R='  \
            + str(int(simulation.R))
        with open(pickle_path + 'surface_stresses_' + pickle_file_name + '.pkl', 'r') as pickle_handle:
            stresses = pickle.load(pickle_handle)
            positions = pickle.load(pickle_handle)
        stress_history = stresses[:, positions[:, 0] < x_max, :]
        positions = positions[positions[:, 0] < x_max, :]
        num_points = stress_history.shape[1]
        fatigue_stress = np.zeros((num_points, 2))
        for i in range(num_points):
            fatigue_stress[i, :] = get_stress_values(stress_history[:, i, :])
        i = np.argmax(fatigue_stress[:, 0] + fatigue_stress[:, 1])
        plt.plot(fatigue_stress[:, 1], fatigue_stress[:, 0], c + 'x')
        print positions[i], fatigue_stress[i, 0] + fatigue_stress[i, 1]
        plt.figure(100)
        hull = ConvexHull(np.fliplr(fatigue_stress))
        plt.plot(fatigue_stress[hull.vertices, 1], fatigue_stress[hull.vertices, 0], c + '--', lw=2)

        plt.xlim(-500, 500)
        plt.ylim(0, 1000)

    plt.show()
