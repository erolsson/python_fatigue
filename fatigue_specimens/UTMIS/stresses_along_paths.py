import os
import pickle

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

pickle_path = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/mechanical_data/')


def get_stress_data(specimen_type, stress_ratio, stress_level):
    simulation_name = '/utmis_' + specimen_type + '_' + str(stress_level).replace('.', '_') + '_R=' \
                      + str(int(stress_ratio))
    data = {}
    for path_name in ['y', 'z1', 'z2']:
        with open(pickle_path + simulation_name + '_path_' + path_name + '.pkl') as pickle_file:
            stress_data = pickle.load(pickle_file)
        sa = np.abs(stress_data['max_load'][:, 1] - stress_data['min_load'][:, 1])/2
        sm = (stress_data['max_load'][:, 1] + stress_data['min_load'][:, 1])/2
        pos = stress_data['max_load'][:, 0]
        data[path_name] = {'sa': sa, 'sm': sm, 'pos': pos}
    return data


if __name__ == '__main__':
    specimen_loads = {'smooth': {-1.: [737.], 0.: [425., 440.]},
                      'notched': {-1.: [427., 450.], 0.: [225., 240., 255.]}}

    color = ['g', 'b', 'r']
    line = {'smooth': '--', 'notched': '-'}

    for R in [-1., 0.]:
        # plt.figure()
        for specimen in specimen_loads.keys():
            for i, stress in enumerate(specimen_loads[specimen][R]):
                stresses = get_stress_data(specimen, R, stress)
                for path in ['y', 'z1', 'z2']:
                    plt.plot(stresses[path]['sm'], stresses[path]['sa'], line[specimen] + color[i])

    plt.show()
