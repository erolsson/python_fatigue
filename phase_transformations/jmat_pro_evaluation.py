from collections import namedtuple

import numpy as np

from scipy.optimize import fmin

import matplotlib
import matplotlib.pyplot as plt

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


def read_jmat_data(directory, cooling_rate, carbon_level):
    filename = directory + '/' + str(int(cooling_rate)) + 'C/jmat_pro_tehler_' + \
        str(carbon_level).replace('.', '_') + '.csv'

    column_names = {'temperature': 'T (C)',
                    'austenite':   'Phases vol%-AUSTENITE-' + str(float(cooling_rate)) + '(C/s)',
                    'ferrite':     'Phases vol%-FERRITE-' + str(float(cooling_rate)) + '(C/s)',
                    'martensite':  'Phases vol%-MARTENSITE-' + str(float(cooling_rate)) + '(C/s)',
                    'bainite':     'Phases vol%-BAINITE-' + str(float(cooling_rate)) + '(C/s)',
                    'expansion':   'Linear expansion (%)-  -' + str(float(cooling_rate)) + '(C/s)'}

    with open(filename, 'r') as csv_file:
        lines = csv_file.readlines()
        headers = lines[0].split(',')

    data = np.genfromtxt(filename, delimiter=',', skip_header=1, missing_values=0.)
    data[np.isnan(data)] = 0
    rows = data.shape[0]

    jmat_data = {}
    for name, header in column_names.iteritems():
        try:
            idx = headers.index(header)
            data_column = data[:, idx]
        except ValueError:
            data_column = np.zeros(rows)
        jmat_data[name] = data_column/100
    jmat_data['temperature'] *= 100
    return jmat_data


def austenite_expansion(par, carbon, temp):
    return par[0] + par[1]*carbon + par[2]*temp


def martensite_expansion(par, carbon, temp):
    return par[0] + par[1]*carbon + par[2]*carbon**2 + par[3]*temp + par[4]*temp*carbon + par[5]*temp**2 + \
        par[6]*carbon*temp**2 + par[7]*temp**3


class PhaseData:
    def __init__(self, name, expansion_function, num_params):
        self.num_params = num_params
        self.parameters = [None]*num_params
        self.name = name
        self.expansion_function = expansion_function

    def expansion(self, carbon, temp):
        return self.expansion_function(self.parameters, carbon, temp)


phase_data = {'austenite': PhaseData('austensite', austenite_expansion, 3),
              'martensite': PhaseData('martensite', austenite_expansion, 8)}


ExpansionPhaseData = namedtuple('ExpansionPhaseData', ['names', 'carbon', 'fractions', 'expansion', 'temperature'])


def residual(par, *data):
    r = 0
    used_params = 0
    for expansion_data_set in data[0]:
        expansion = 0 * expansion_data_set.temperature
        for phase, fraction in zip(expansion_data_set.names, expansion_data_set.fractions):
            c, t = expansion_data_set.carbon, expansion_data_set.temperature
            if phase_data[phase].parameters[0] is not None:
                expansion += phase_data[phase].expansion(c, t)*fraction
            else:
                phase_params = par[used_params:used_params + phase_data[phase].num_params]
                expansion += phase_data[phase].expansion_function(phase_params, c, t)*fraction

        r += np.sum((expansion_data_set.expansion - expansion)**2)
    return r


if __name__ == '__main__':
    # Processing austenite-martensite transformation 50C/s
    DataSet = namedtuple('DataSet', ['carbon_level', 'color'])
    data_sets = [DataSet(carbon_level=0.2, color='k'),
                 DataSet(carbon_level=0.36, color='b'),
                 DataSet(carbon_level=0.52, color='m'),
                 DataSet(carbon_level=0.65, color='r'),
                 DataSet(carbon_level=0.8, color='g')]

    austenite_data = []
    martensite_data = []
    for jmat_data_set in data_sets:
        data_set = read_jmat_data('data_jmat_pro_tehler', 50, jmat_data_set.carbon_level)
        plt.plot(data_set['temperature'], data_set['expansion'], jmat_data_set.color, lw=2)

        austenite = data_set['austenite']
        austenite_dataset = ExpansionPhaseData(names=['austenite'],
                                               carbon=jmat_data_set.carbon_level,
                                               fractions=[austenite[austenite == 1.]],
                                               expansion=data_set['expansion'][austenite == 1.],
                                               temperature=data_set['temperature'][austenite == 1.])
        austenite_data.append(austenite_dataset)
        martensite_dataset = ExpansionPhaseData(names=['austenite', 'martensite'],
                                                carbon=jmat_data_set.carbon_level,
                                                fractions=[data_set['austenite'], data_set['martensite']],
                                                expansion=data_set['expansion'],
                                                temperature=data_set['temperature'])

        print data_set['martensite']
        martensite_data.append(martensite_dataset)
    austenite_parameters = fmin(residual, [0.]*3, (austenite_data,))
    phase_data['austenite'].parameters = austenite_parameters
    martensite_parameters = fmin(residual, [0.]*8, (martensite_data,))

    print austenite_parameters
    print martensite_parameters


    plt.show()
