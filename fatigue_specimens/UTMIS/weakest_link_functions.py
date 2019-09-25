from collections import namedtuple
from collections import OrderedDict

import glob
import os
import pickle

import numpy as np

from materials.gear_materials import SteelData
from materials.gear_materials import SS2506MaterialTemplate

from multiprocesser.multiprocesser import multi_processer

from weakest_link.weakest_link_evaluator import WeakestLinkEvaluator
from weakest_link.weakest_link_evaluator import FEM_data

Simulation = namedtuple('Simulation', ['specimen', 'R', 'stress', 'failures', 'run_outs'])


_tempering = 200
_carbon = 0.8
_findley_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/stresses/findley'
                                               '_tempering_2h_' + str(_tempering) + '_' +
                                               str(_carbon).replace('.', '_') + 'C/')


def _get_evaluated_findley_parameters():

    findley_parameter_directories = glob.glob(_findley_pickle_directory + 'a800=*/')
    findley_parameter_directories = [os.path.normpath(directory).split(os.sep)[-1]
                                     for directory in findley_parameter_directories]
    _evaluated_findley_parameters = [directory[5:] for directory in findley_parameter_directories]
    _evaluated_findley_parameters = [float(parameter.replace('_', '.')) for parameter in _evaluated_findley_parameters]
    return np.array(sorted(_evaluated_findley_parameters))


def _get_findley_data():
    _findley_data = {'smooth': {0: {}, -1: {}},
                     'notched': {0: {}, -1: {}}}
    factor = {'smooth': 1., 'notched': 1.}
    _evaluated_findley_parameters = _get_evaluated_findley_parameters()
    for findley_parameter in _evaluated_findley_parameters:
        for specimen, specimen_data in _findley_data.iteritems():
            for load_ratio, load_ratio_data in specimen_data.iteritems():
                file_string = _findley_pickle_directory + 'a800=' + str(findley_parameter).replace('.', '_') + \
                                  '/findley_' + specimen + '_R=' + str(load_ratio) + '_s=*MPa.pkl'
                files = glob.glob(file_string)
                for filename in files:
                    stress = float(filename[len(file_string.split('*')[0]):-len(file_string.split('*')[1])])
                    if stress not in load_ratio_data:
                        load_ratio_data[stress] = OrderedDict()
                    with open(filename) as pickle_handle:

                        load_ratio_data[stress][findley_parameter] = pickle.load(pickle_handle)*factor[specimen]
    return _findley_data


def _get_dante_data():
    dante_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data'
                                                '/dante_tempering_2h_' + str(_tempering) + '_' +
                                                str(_carbon).replace('.', '_') + 'C/')
    data = {}
    for specimen in ['smooth', 'notched']:
        with open(dante_pickle_directory + 'data_utmis_' + specimen + '.pkl') as pickle_handle:
            data[specimen] = pickle.load(pickle_handle)

    return data


def _get_geometry_data():
    pickle_directory_geometry = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/geometry/')
    data = {}
    for specimen in ['smooth', 'notched']:
        with open(pickle_directory_geometry + 'nodal_coordinates_' + specimen + '.pkl') as pickle_handle:
            data[specimen] = pickle.load(pickle_handle)
    return data


def calc_pf_for_simulation(simulation, parameters):
    a800 = parameters[0]
    a1 = parameters[1]
    a2 = 0
    b = parameters[2]

    idx = np.argsort(np.abs(evaluated_findley_parameters - a800))[:2]
    a800_levels = evaluated_findley_parameters[idx]

    # Loading Findley pickles for the found values
    if a800 not in findley_data[simulation.specimen][simulation.R][simulation.stress]:
        findley_stress1 = findley_data[simulation.specimen][simulation.R][simulation.stress][a800_levels[0]]
        findley_stress2 = findley_data[simulation.specimen][simulation.R][simulation.stress][a800_levels[1]]

        da = evaluated_findley_parameters[idx[1]] - evaluated_findley_parameters[idx[0]]
        ds = findley_stress2 - findley_stress1
        findley_stress = findley_stress1 + ds / da * (a800 - evaluated_findley_parameters[idx[0]])
    else:
        findley_stress = findley_data[simulation.specimen][simulation.R][simulation.stress][a800]
    n = findley_stress.shape[0]
    nodal_positions = geometry_data[simulation.specimen]
    interesting_point = np.array([0., 2.5, 0])
    distance_to_monitor_node = 0 * nodal_positions + nodal_positions
    for i in range(3):
        distance_to_monitor_node[:, i] -= interesting_point[i]
    monitor_node_idx = np.argmin(np.sum(np.abs(distance_to_monitor_node), 1))

    findley_stress[nodal_positions[:, 0] > 11.] = 0
    findley_stress[nodal_positions[:, 2] > 1.] = 0
    print np.max(nodal_positions[:, 0])
    max_idx = np.argmax(findley_stress)
    print "The maximum findley stress for", simulation.specimen, "with load ratio", simulation.R, "and stress level",\
        simulation.stress, "is", findley_stress[max_idx], 'MPa and occurs at point', nodal_positions[max_idx]
    print '\tThe findley stress at interesting point is', findley_stress[monitor_node_idx], "MPa"

    steel_data = SteelData(HV=dante_data[simulation.specimen]['HV'].reshape(n/8, 8))

    fem_data = FEM_data(stress=findley_stress.reshape(n/8, 8),
                        steel_data=steel_data,
                        nodal_positions=nodal_positions.reshape(n/8, 8, 3))

    fit_material = SS2506MaterialTemplate(a1, a2, b)
    size_factor = 4
    if simulation.R < 0:
        size_factor = 8
    wl_evaluator = WeakestLinkEvaluator(data_volume=fem_data, data_area=None, size_factor=size_factor)
    return wl_evaluator.calculate_pf(material=fit_material)


def residual_fit(parameters, *data):
    simulation_list, lower_bound, upper_bound = data
    parameters = _check_parameter_bounds(parameters, lower_bound, upper_bound)

    experimental_pf = np.array([float(sim.failures) / (sim.failures + sim.run_outs) for sim in simulation_list])
    job_list = [(calc_pf_for_simulation, (simulation, parameters), {}) for simulation in simulation_list]
    pf_wl = np.array(multi_processer(job_list, timeout=100, delay=0))
    r = (pf_wl - experimental_pf) ** 2
    r[abs(pf_wl - experimental_pf) < 0.1] = 0
    print '============================================================================================================'
    print 'parameters:\t\t', parameters
    print 'pf_simulation:\t', ' '.join(np.array_repr(pf_wl).replace('\n', '').replace('\r', '').split())
    print 'r_vec:\t\t\t', ' '.join(np.array_repr(r).replace('\n', '').replace('\r', '').split())
    print 'R:\t\t\t', np.sqrt(np.sum(r))/10
    return np.sum(r)


def residual_plot(parameters, simulation_list):
    experimental_pf = np.array([float(sim.failures) / (sim.failures + sim.run_outs) for sim in simulation_list])
    pf_sim = np.array([calc_pf_for_simulation(simulation, parameters) for simulation in simulation_list])
    return np.sum((pf_sim - experimental_pf)**2)


def likelihood_function_plot(parameters, simulation_list):
    likelihood = 0
    for simulation in simulation_list:
        tol = 1e-6
        pf = calc_pf_for_simulation(simulation, parameters)
        if pf > 1 - tol:
            pf = 1 - tol
        if pf < tol:
            pf = tol

        likelihood -= np.log(pf)*simulation.failures
        likelihood -= np.log(1 - pf)*simulation.run_outs

    return likelihood


def likelihood_function_fit(parameters, *data):
    simulation_list, lower_bound, upper_bound = data
    parameters = _check_parameter_bounds(parameters, lower_bound, upper_bound)

    tol = 1e-6
    job_list = [(calc_pf_for_simulation, (simulation, parameters), {}) for simulation in simulation_list]
    pf_sim = np.array(multi_processer(job_list, timeout=100, delay=0))
    pf_sim[pf_sim < tol] = tol
    pf_sim[pf_sim > 1 - tol] = 1 - tol
    likelihood = 0
    for i, simulation in enumerate(simulation_list):

        likelihood -= np.log(pf_sim[i])*simulation.failures
        likelihood -= np.log(1 - pf_sim[i])*simulation.run_outs

    print '============================================================================================================'
    print 'parameters:\t\t', parameters
    print 'pf_simulation:\t', ' '.join(np.array_repr(pf_sim).replace('\n', '').replace('\r', '').split())

    print 'L:\t\t\t', likelihood
    return likelihood


def _check_parameter_bounds(parameters, lower_bound, upper_bound):
    parameters = np.array(parameters)
    lower_bound = np.array(lower_bound)
    upper_bound = np.array(upper_bound)

    parameters[parameters < lower_bound] = lower_bound[parameters < lower_bound]
    parameters[parameters > upper_bound] = upper_bound[parameters > upper_bound]
    return parameters


findley_data = _get_findley_data()
dante_data = _get_dante_data()
geometry_data = _get_geometry_data()
evaluated_findley_parameters = _get_evaluated_findley_parameters()


if __name__ == '__main__':
    _get_findley_data()
