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
                    'pearlite':    'Phases vol%-PEARLITE-' + str(float(cooling_rate)) + '(C/s)',
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
    par[5:] = 0
    return par[0] + par[1]*carbon + par[2]*carbon**2 + par[3]*temp + par[4]*temp*carbon + par[5]*temp**2 + \
        par[6]*carbon*temp**2 + par[7]*temp**3


def bainite_expansion(par, carbon, temp):
    par[5] = 0
    par[3] = 0
    return par[0] + par[1]*carbon + par[2]*temp + par[3]*carbon*temp + par[4]*temp**2 + par[5]*carbon*temp**2


class PhaseData:
    def __init__(self, name, expansion_function, num_params):
        self.num_params = num_params
        self.parameters = [None]*num_params
        self.name = name
        self.expansion_function = expansion_function

    def expansion(self, carbon, temp):
        return self.expansion_function(self.parameters, carbon, temp)


phase_data = {'austenite': PhaseData('austensite', austenite_expansion, 3),
              'martensite': PhaseData('martensite', martensite_expansion, 8),
              'ferrite': PhaseData('ferrite', austenite_expansion, 3),
              'pearlite': PhaseData('pearlite', austenite_expansion, 3),
              'bainite': PhaseData('bainite', bainite_expansion, 6)}


ExpansionPhaseData = namedtuple('ExpansionPhaseData', ['names', 'carbon', 'fractions', 'expansion', 'temperature'])


def residual(par, *data):
    r = 0
    for expansion_data_set in data[0]:
        strain = 0 * expansion_data_set.temperature
        used_params = 0
        for phase, fraction in zip(expansion_data_set.names, expansion_data_set.fractions):
            c, t = expansion_data_set.carbon, expansion_data_set.temperature
            if phase_data[phase].parameters[0] is not None:
                strain += phase_data[phase].expansion(c, t)*fraction
            else:
                phase_params = par[used_params:used_params + phase_data[phase].num_params]
                strain += phase_data[phase].expansion_function(phase_params, c, t)*fraction
                used_params += phase_data[phase].num_params

        r += np.sum((expansion_data_set.expansion - strain)**2)/strain.shape[0]
    return r*1e9


def martensite_fraction(par, austenite, carbon, temperature):
    par = np.array(par)
    ms_temp = np.interp(carbon, [0.2, 0.5, 0.8], par[0:3])
    austenite_ms = np.interp(ms_temp, np.flip(temperature), np.flip(austenite))
    a = np.interp(carbon, [0.2, 0.5, 0.8], par[3:])
    martensite = 0*temperature
    martensite[temperature < ms_temp] = (1-np.exp(-a*(ms_temp - temperature[temperature < ms_temp])))*austenite_ms
    return martensite


def km_residual(par, *data):
    r = 0
    par[par < 0] = 0
    for expansion_data_set in data[0]:
        austenite = expansion_data_set.fractions[0]
        martensite = expansion_data_set.fractions[1]
        temperature = expansion_data_set.temperature

        r += np.sum((martensite_fraction(par, austenite, expansion_data_set.carbon, temperature) -
                     martensite)**2)
    return r*1e9


if __name__ == '__main__':
    # Processing austenite-martensite transformation 50C/s
    DataSet = namedtuple('DataSet', ['carbon_level', 'color'])
    data_sets = [DataSet(carbon_level=0.2, color='k'),
                 DataSet(carbon_level=0.36, color='b'),
                 DataSet(carbon_level=0.52, color='m'),
                 DataSet(carbon_level=0.65, color='r'),
                 DataSet(carbon_level=0.8, color='g')]

    austenite_data = []
    ferrite_data = []
    martensite_data = []
    bainite_data = []
    km_data = []
    for jmat_data_set in data_sets:
        data_set1 = read_jmat_data('data_jmat_pro_tehler', 1., jmat_data_set.carbon_level)
        data_set50 = read_jmat_data('data_jmat_pro_tehler', 50., jmat_data_set.carbon_level)

        plt.figure(0)
        plt.plot(data_set1['temperature'], data_set1['expansion'], jmat_data_set.color, lw=2)
        plt.figure(1)
        plt.plot(data_set50['temperature'], data_set50['expansion'], jmat_data_set.color, lw=2)

        austenite = data_set1['austenite']
        austenite_dataset = ExpansionPhaseData(names=['austenite'],
                                               carbon=jmat_data_set.carbon_level,
                                               fractions=[austenite[austenite == 1.]],
                                               expansion=data_set1['expansion'][austenite == 1.],
                                               temperature=data_set1['temperature'][austenite == 1.])
        austenite_data.append(austenite_dataset)
        phases = data_set1['austenite'] + data_set1['ferrite']
        data_indicies = phases == 1.
        ferrite_dataset = ExpansionPhaseData(names=['austenite', 'ferrite'],
                                             carbon=jmat_data_set.carbon_level,
                                             fractions=[data_set1['austenite'][data_indicies],
                                                        data_set1['ferrite'][data_indicies]],
                                             expansion=data_set1['expansion'][data_indicies],
                                             temperature=data_set1['temperature'][data_indicies])

        ferrite_data.append(ferrite_dataset)
        phases += data_set1['pearlite'] + data_set1['bainite']
        data_indicies = phases > 0.999
        bainite_dataset = ExpansionPhaseData(names=['austenite', 'ferrite', 'pearlite', 'bainite'],
                                             carbon=jmat_data_set.carbon_level,
                                             fractions=[data_set1['austenite'][data_indicies],
                                                        data_set1['ferrite'][data_indicies],
                                                        data_set1['pearlite'][data_indicies],
                                                        data_set1['bainite'][data_indicies]],
                                             expansion=data_set1['expansion'][data_indicies],
                                             temperature=data_set1['temperature'][data_indicies])
        bainite_data.append(bainite_dataset)
        martensite_dataset = ExpansionPhaseData(names=['austenite', 'ferrite', 'pearlite', 'bainite', 'martensite'],
                                                carbon=jmat_data_set.carbon_level,
                                                fractions=[data_set50['austenite'][data_indicies],
                                                           data_set50['ferrite'][data_indicies],
                                                           data_set50['pearlite'][data_indicies],
                                                           data_set50['bainite'][data_indicies],
                                                           data_set50['martensite'][data_indicies]],
                                                expansion=data_set50['expansion'][data_indicies],
                                                temperature=data_set50['temperature'][data_indicies])
        martensite_data.append(martensite_dataset)

        plt.figure(2)
        plt.plot(data_set50['temperature'], data_set50['martensite'], jmat_data_set.color, lw=2)

        km_dataset = ExpansionPhaseData(names=['austenite', 'martensite'],
                                        carbon=jmat_data_set.carbon_level,
                                        fractions=[data_set50['austenite'], data_set50['martensite']],
                                        expansion=data_set50['expansion'],
                                        temperature=data_set50['temperature'])
        km_data.append(km_dataset)

    austenite_parameters = fmin(residual, [0.]*3, (austenite_data,), maxfun=1e9, maxiter=1e9)
    phase_data['austenite'].parameters = austenite_parameters
    ferrite_parameters = fmin(residual, [0.]*3, (ferrite_data,), maxfun=1e9, maxiter=1e9)
    phase_data['ferrite'].parameters = ferrite_parameters
    phase_data['pearlite'].parameters = ferrite_parameters
    bainite_parameters = fmin(residual, [0.]*6, (bainite_data,), maxfun=1e9, maxiter=1e9)
    phase_data['bainite'].parameters = bainite_parameters
    martensite_parameters = fmin(residual, [0.]*8, (martensite_data,), maxfun=1e9, maxiter=1e9)
    phase_data['martensite'].parameters = martensite_parameters

    km_parameters = fmin(km_residual, [150, 250, 400, 0.04, 0.02, 0.01], (km_data,), maxfun=1e9, maxiter=1e9)

    print '==================================================================================='
    print ' *** Austenite parameters ***'
    print austenite_parameters
    print ' *** Ferrite parameters ***'
    print ferrite_parameters
    print ' *** Bainite parameters ***'
    print bainite_parameters
    print ' *** Martensite parameters ***'
    print martensite_parameters
    print '==================================================================================='
    print ' *** 0.2 % Carbon ***'
    print 'Ms temp:', km_parameters[0]
    print 'Mobility:', km_parameters[3]
    print ' *** 0.5 % Carbon ***'
    print 'Ms temp:', km_parameters[1]
    print 'Mobility:', km_parameters[4]
    print ' *** 0.8 % Carbon ***'
    print 'Ms temp:', km_parameters[2]
    print 'Mobility:', km_parameters[5]



    for jmat_data_set in data_sets:
        for rate, fig in zip([1., 50.], [0., 1]):
            plt.figure(fig)
            data_set = read_jmat_data('data_jmat_pro_tehler', rate, jmat_data_set.carbon_level)
            temperature = data_set['temperature']
            austenite = data_set['austenite']
            expansion = 0*temperature
            for phase in ['austenite', 'ferrite', 'pearlite', 'bainite', 'martensite']:
                fraction = data_set[phase]
                expansion += fraction*phase_data[phase].expansion(jmat_data_set.carbon_level, temperature)
                plt.plot(temperature, expansion, ':' + jmat_data_set.color, lw=1)
            plt.plot(temperature, expansion, '--' + jmat_data_set.color, lw=2)

        plt.figure(2)
        martensite = martensite_fraction(km_parameters, austenite, jmat_data_set.carbon_level, temperature)
        plt.plot(temperature, martensite, '--' + jmat_data_set.color, lw=2)

    plt.show()
