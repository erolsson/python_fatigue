import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from planetary_gear.test_results import TestResults

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

for case_depth in case_depths:
    name = test_directory + 'case_depth_' + str(case_depth)
    name = name.replace('.', '_')
    test_data = TestResults(name + '.dat')
    print test_data.get_test_results()[32.]
