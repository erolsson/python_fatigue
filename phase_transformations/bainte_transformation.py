from collections import namedtuple

import numpy as np

import matplotlib
import matplotlib.pyplot as plt

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}", r"\usepackage{gensymb}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

Experiment = namedtuple('Experiment', ['temperature', 'color'])
colors = 'rbgk'
temperatures = np.arange(650, 850, 50)

experiments = [Experiment(temperature=t, color=c) for t, c in zip(temperatures, colors)]
for experiment in experiments:
    data = np.genfromtxt('data_tehler/bainite_transformation/C02_' + str(int(experiment.temperature)) + 'K',
                         delimiter=',')
    time = 10**data[:, 0]
    bainite = 10**data[:, 1]/(1 + 10**data[:, 1])
    plt.plot(time, bainite, experiment.color, lw=2)

plt.show()
