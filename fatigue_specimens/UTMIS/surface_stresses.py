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

FEMSimulation = namedtuple('FEMSimulation', ['specimen', 'stress', 'R'])

x_max = 5.
simulations = [FEMSimulation('smooth', )]

plt.show()
