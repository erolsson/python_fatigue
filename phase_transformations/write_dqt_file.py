import datetime

import numpy as np

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


base_file_name = 'U92506.DQT'
material_name = 'U92506EO'
umat_file_name = 'UMAT_files/U92506EO/' + material_name
directory = 'SS2506_data'
carbon_levels = np.arange(0.002, 0.01, 0.003)

martensite_parameters = np.zeros((carbon_levels.shape[0], 5))
martensite_parameters[:, 0] = SS2506.ms_temperature(carbon_levels) - 273.15

for i, carbon in enumerate(carbon_levels):
    carbon = round(carbon, 4)
    parameter_filename = directory + '/carbon_' + str(carbon).replace('.', '_') + '/'
    parameter_filename += 'parameters_' + str(carbon).replace('.', '_') + '_KINETICS.OUT'
    with open(parameter_filename, 'r') as parameter_file:
        file_lines = parameter_file.readlines()

        # reading the 4 parameters
        for par in range(4):
            parameter = float(file_lines[par+6].split(':')[1])
            martensite_parameters[i, par+1] = parameter

for i in range(martensite_parameters.shape[1]):
    plt.figure(i)
    plt.plot(carbon_levels, martensite_parameters[:, i])

# Reading template DQT file
with open(base_file_name, 'r') as template_file:
    template_lines = template_file.readlines()

    data_indices = []
    for i, line in enumerate(template_lines):
        if line.startswith('# Chemical composition of data'):
            composition_line = template_lines[i+2]
            carbon = float(composition_line.split()[1])/100
            if carbon in carbon_levels:
                data_indices.append(i)

    data_indices.append(len(template_lines))

# Remove line breaks in template_lines
template_lines = [line.replace('\r\n', '') for line in template_lines]

now = datetime.datetime.now()
file_lines = ['** SS2506 Kinetics Data by Erik Olsson ' + now.strftime('%d/%m/%Y'),
              now.strftime('%b').upper() + str(now.year) + '       ! model implementation date : use UPPERCASE',
              material_name + '         ! matnam must be UPPERCASE',
              '1           ! itprdb=1, require tempering data; otherwise no.',
              '1           ! iheat=1, require heating data; otherwise no.',
              '** stress effect on martensitic transformation',
              ' 6.500000E-02   !stress effect on martensite transformation',
              '** Total number of kinetic data sets with different chemistry',
              str(carbon_levels.shape[0])]

for i, carbon in enumerate(carbon_levels):
    file_lines += template_lines[data_indices[i]:data_indices[i]+3]
    file_lines.append(str(martensite_parameters[i, 0]) + '              !Ms')
    file_lines.append(str(martensite_parameters[i, 1]) + '              !mobility')
    file_lines.append(str(martensite_parameters[i, 2]) + '              !alpha')
    file_lines.append(str(martensite_parameters[i, 3]) + '              !beta')
    file_lines.append(str(martensite_parameters[i, 4]) + '              !epsilon_m')
    file_lines += template_lines[data_indices[i]+9:data_indices[i+1]]

with open(umat_file_name + '.DQT', 'w+') as new_material_file:
    for line in file_lines:
        new_material_file.write(line + '\n')
plt.show()
