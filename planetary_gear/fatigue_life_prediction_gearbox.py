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

haiback = True
