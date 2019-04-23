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


umat_filename = 'UMAT_files/U925062/U925063.MEC'


def get_parameters_from_mech_file(mec_file):
    parameters = {}
    phases = ['Austenite', 'Martensite']
    data_lines = [100, 115]
    with open(mec_file, 'r') as umat_file:
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
                parameters[phase] = np.array([float(par) for par in parameter_line])
    return parameters


def cte_model(t, c, parameter_dict, phase):
    p = parameter_dict[phase]
    return p[0]+p[1]*c + p[2]*c**2 + p[3]*t + p[4]*c*t + p[5]*t**2 + p[6]*c*t**2 + p[7]*t**3


temperature = np.linspace(0, 500, 1000)
carbon_levels = np.arange(0.0, 1.0, 0.3)/100

parameters = get_parameters_from_mech_file(umat_filename)

for fig, phase_name in enumerate(['Austenite', 'Martensite']):
    plt.figure(fig)
    for carbon in carbon_levels:
        cte = SS2506.transformation_strain.__getattribute__(phase_name)(temperature, carbon)

        plt.plot(temperature, cte, lw=2)

        cte = cte_model(temperature, carbon*100, parameters, phase_name)

        plt.plot(temperature, cte, '--', lw=2)


plt.figure(100)
color_codes = 'rbg'

for carbon, color in zip(carbon_levels, color_codes):
    e_trans = cte_model(temperature, carbon*100, parameters, 'Martensite') -\
              cte_model(temperature, carbon*100, parameters, 'Austenite')

    plt.plot(temperature, e_trans, color, lw=2)

parameters = get_parameters_from_mech_file('UMAT_files/U925062/U925063.MEC.BAK')
for carbon, color in zip(carbon_levels, color_codes):
    e_trans = cte_model(temperature, carbon*100, parameters, 'Martensite') - \
              cte_model(temperature, carbon*100, parameters, 'Austenite')

    plt.plot(temperature, e_trans, '--'+color, lw=2)
plt.show()
