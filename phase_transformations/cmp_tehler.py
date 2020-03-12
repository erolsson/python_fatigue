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

Experiment = namedtuple('Experiment', ['carbon', 'color', 'column'])
experiments = [Experiment(carbon=0.2, color='k', column=15),
               Experiment(carbon=0.36, color='b', column=15),
               Experiment(carbon=0.52, color='m', column=15),
               Experiment(carbon=0.65, color='r', column=12)]

for experiment in experiments:
    exp_data = np.genfromtxt('data_tehler/expansion_' + str(experiment.carbon).replace('.', '_'), delimiter=',')
    temp = exp_data[:, 0] - 273.15
    strain = exp_data[:, 1] / 10000
    e750 = np.interp(750, np.flip(temp), np.flip(strain))
    plt.figure(0)
    label = 'Tehler' if experiment.carbon == 0.2 else None
    plt.plot(temp, strain, experiment.color, lw=2, label=label)

    data = np.genfromtxt('data_jmat_pro_tehler/50C/jmat_pro_tehler_' + str(experiment.carbon).replace('.', '_') + '.csv',
                         delimiter=',')
    temperature = data[:, 0]
    strain = data[:, experiment.column]/100
    strain += -np.interp(750, np.flip(temperature), np.flip(strain)) + e750

    label = 'JMAT-PRO' if experiment.carbon == 0.2 else None

    plt.plot(temperature, strain, '--' + experiment.color, lw=2, label=label)

plt.ylabel('Transformation strain [-]')
plt.xlabel(r'Temperature [ $\degree$C]')

plt.annotate('', xy=(600, 0.01), xytext=(800, 0.006), arrowprops={'arrowstyle': '->'})
plt.text(50, 0.011, r'\textbf{Carbon wt\%: \{0.2, 0.36, 0.52, 0.65\}}')
plt.tight_layout()
plt.xlim(25, 900)
plt.grid(True)

plt.legend(loc='upper left', bbox_to_anchor=(0.45, 0.3))
plt.savefig('trans_strain_jmat_teher.png')
plt.show()
