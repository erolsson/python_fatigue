import os
import pickle

from collections import namedtuple

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


def get_stress_values(stress_components):
    stress_tensor = np.zeros((2, 3, 3))

    stress_tensor[0, :, :] = np.diag(0, stress_components[:3])
    stress_tensor[1, :, :] = np.diag(1, stress_components[:3])

    stress_tensor[:, 0, 1] = stress_components[:, 3]
    stress_tensor[:, 1, 0] = stress_components[:, 3]

    stress_tensor[:, 0, 2] = stress_components[:, 4]
    stress_tensor[:, 2, 0] = stress_components[:, 4]

    stress_tensor[:, 1, 2] = stress_components[:, 5]
    stress_tensor[:, 2, 1] = stress_components[:, 5]


FEMSimulation = namedtuple('FEMSimulation', ['specimen', 'stress', 'R'])

x_max = 5.
simulations = [FEMSimulation('smooth', 774, -1), FEMSimulation('notched', 450, -1)]

plt.show()
