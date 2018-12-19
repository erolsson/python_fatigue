import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


mesh = '1x'
test_directory = os.path.expanduser('~/scania_gear_analysis/experimental_data/pulsator_testing/')
case_depths = [0.5, 0.8, 1.1, 1.4]

for cd in case_depths:
    pass