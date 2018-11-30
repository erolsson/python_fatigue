import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

from materials.gear_materials import SS2506

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def write_dilatometer_file(carbon, cooling_rate, start_temp=400, end_temp=22, file_name=None, figure=None):
    pass


def write_transformation_strain_file(carbon, direcory='', num_points=15):

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
        print alpha
        for t, a in zip(temperature, alpha):
            file_lines.append(str(t) + '\t' + str(a))

    for phase_name in ['Austenite'] + phases:
        write_thermal_expansion_section(phase_name)

    with open(direcory + 'TRSTRN.CTL', 'w') as ctl_file:
        for line in file_lines:
            ctl_file.write(line + '\n')


if __name__ == '__main__':
    write_transformation_strain_file(carbon=0.0043)

