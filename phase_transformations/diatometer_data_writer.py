import os
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

from phase_transformation_functions import dilatormeter_experiment

from materials.gear_materials import SS2506

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def write_transformation_strain_file(carbon, num_points=15):

    temperature = np.linspace(0, 700, num_points, endpoint=True)
    file_lines = ['# TRSTRN & CTE for "' + SS2506.name + ',"' + '%04.2f' % (carbon*100) +
                  '%C; Max 20 lines per "phase, "FIXED FORMAT']

    phases = ['Ferrite', 'Pearlite', 'Bainite', 'Martensite']

    def write_trstrn_section(phase):
        file_lines.append('# TRSTRN ' + phase)
        file_lines.append(str(num_points))
        e_austenite = SS2506.transformation_strain.Austenite(temperature, carbon)
        e_phase = getattr(SS2506.transformation_strain, phase)(temperature, carbon)
        for t, e in zip(temperature, e_phase-e_austenite):
            file_lines.append(str(t) + '\t' + str(e))

    for phase_name in phases:
        write_trstrn_section(phase_name)

    file_lines.append('## COEFFICIENT OF THERMAL EXPANSION')

    def write_thermal_expansion_section(phase):
        file_lines.append('# CTE ' + phase)
        file_lines.append(str(num_points))
        alpha = getattr(SS2506.thermal_expansion, phase)(temperature, carbon)
        for t, a in zip(temperature, alpha):
            file_lines.append(str(t) + '\t' + str(a))

    for phase_name in ['Austenite'] + phases:
        write_thermal_expansion_section(phase_name)

    file_lines.append('## END OF FILE')

    with open('TRSTRN.CTL', 'w') as ctl_file:
        for line in file_lines:
            ctl_file.write(line + '\n')


def write_dilatometer_data_strain_file(carbon, cooling_rate=50., numpoints=500, start_temp=400, end_temp=20):
    file_lines = ['SS2506  Continuous cooling martensite + Others (C=' + '%04.2f' % (carbon*100) + '%)',
                  'Project 2018',
                  '0.77	    Mn',
                  '0.28	    Si',
                  '0.42	    Ni',
                  '0.46	    Cr',
                  '0.19	    Mo',
                  '0.03	    S',
                  '0.00	    Co',
                  '0.048	Cu',
                  '0.009	P',
                  '0.028	Al',
                  'NUMBER	OF	DATA	IN	THIS	SET',
                  '1',
                  '950C_' + str(int(cooling_rate)) + 'C-Cooling_1.DAT	   (1)',
                  '%04.2f' % (carbon*100),
                  str(numpoints) + '\t3',
                  '1 ' + str(numpoints),
                  'Temperature Strain  DATA (Sample-1-1 000C; ' + str(int(cooling_rate)) + 'C/s)']

    temperature = np.linspace(start_temp, end_temp, numpoints, endpoint=False)
    t_end = (start_temp - end_temp)/cooling_rate
    time = np.linspace(0, t_end, numpoints, endpoint=False)

    strain = dilatormeter_experiment(temperature, carbon)
    strain = strain - strain[0]

    for (t, temp, e) in zip(time, temperature, strain):
        file_lines.append(str(t) + '\t' + str(temp) + '\t' + str(e))

    file_lines.append('END OF FILE')
    file_name = 'SS2506_continuous_cooling_martensite_C=' + str(carbon * 100).replace('.', '_')[0:4] + '.dat'
    with open(file_name, 'w') as dlatometer_file:
        for line in file_lines:
            dlatometer_file.write(line + '\n')


def write_ms_temperature_file(carbon):
    ms_temperature = SS2506.ms_temperature(carbon) - 273.15
    with open('ms_temperature.dat', 'w') as ms_file:
        for ms, c in zip(ms_temperature, carbon):
            ms_file.write('%04.2f' % (c*100) + '%\t' + str(ms) + '\n')


if __name__ == '__main__':
    if not os.path.isdir('SS2506_data'):
        os.makedirs('SS2506_data')
    os.chdir('SS2506_data')

    carbon_contents = np.arange(0.008, 0.009, 0.001)
    write_ms_temperature_file(carbon_contents)

    for carbon_content in carbon_contents:
        dir_name = 'carbon_' + str(carbon_content).replace('.', '_')[0:5]
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        os.chdir(dir_name)
        write_transformation_strain_file(carbon=carbon_content)
        write_dilatometer_data_strain_file(carbon=carbon_content, cooling_rate=50, end_temp=120)
        os.chdir('..')
