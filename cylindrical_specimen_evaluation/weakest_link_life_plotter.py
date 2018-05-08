import numpy as np
import matplotlib.pyplot as plt

from test_results import TestResults

plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

# Plot test data
test_results = TestResults(r'/home/erolsson/postDoc/cylindrical_specimen/testResults.csv')
test_results.adjust_runouts()

for ht in

