import numpy as np

import re

import matplotlib.pyplot as plt
import matplotlib

from materials.gear_materials import SS2506

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

phases = ['Austenite', 'Martensite']
data_lines = [100, 115]
umat_filename = 'U92506.MEC'
parameters = {}
with open(umat_filename, 'r') as umat_file:
    lines = umat_file.readlines()
    for i, phase in enumerate(phases):
        parameters[phase] = np.zeros(8)
        parameter_line = lines[data_lines[i]]
        parameter_line = re.sub('line.+', '', parameter_line)
        parameter_line = parameter_line.replace(' ', '')
        parameter_line = parameter_line.split(',')
        n = len(parameter_line)
        if n == 3:
            parameters[phase][0:2] = parameter_line[0:2]
            parameters[phase][3] = parameter_line[2]
        else:
            parameters[phase] = np.array([float(p) for p in parameter_line])

print parameters

temperature = np.linspace(20, 500, 1000)
carbon_levels = np.arange(0.2, 1.0, 0.3)/100

for i, phase in enumerate(phases):
    plt.figure(i)
    for carbon in carbon_levels:
        cte = SS2506.transformation_strain.__getattribute__(phase)(temperature, carbon)

        plt.plot(temperature, cte, lw=2)

        p = parameters[phase]
        carbon = carbon
        cte_model = p[0]+p[1]*carbon + p[2]*carbon**2 + p[3]*temperature + p[4]*carbon*temperature + \
            p[5]*temperature**2 + p[6]*carbon*temperature**2 + p[7]*temperature**3

        plt.plot(temperature, cte_model, '--', lw=2)


plt.show()
