import glob
import os
import pickle

from collections import namedtuple

import numpy as np
from scipy.optimize import fmin

from materials.gear_materials import SteelData
from materials.gear_materials import SS2506MaterialTemplate

from multiprocesser.multiprocesser import multi_processer

from weakest_link.weakest_link_evaluator import WeakestLinkEvaluator
from weakest_link.weakest_link_evaluator import FEM_data


Simulation = namedtuple('Simulation', ['specimen', 'R', 'stress'])


def calc_pf_for_simulation(simulation, parameters):
    a800 = parameters[0]
    a1 = parameters[1]
    a2 = 0
    b = parameters[2]

    idx = np.argsort(np.abs(evaluated_findley_parameters - a800))[:2]

    # Loading Findley pickles for the found values
    findley_pickle_name = 'findley_' + simulation.specimen + '_R=' + str(int(simulation.R)) + '_s=' + \
                          str(int(simulation.stress)) + 'MPa.pkl'
    with open(findley_pickle_directory + 'a800=' + str(evaluated_findley_parameters[idx[0]]).replace('.', '_') + '/' +
              findley_pickle_name) as pickle_handle:
        findley_stress1 = pickle.load(pickle_handle)

    with open(findley_pickle_directory + 'a800=' + str(evaluated_findley_parameters[idx[1]]).replace('.', '_') + '/' +
              findley_pickle_name) as pickle_handle:
        findley_stress2 = pickle.load(pickle_handle)

    da = evaluated_findley_parameters[idx[1]] - evaluated_findley_parameters[idx[0]]
    ds = findley_stress2 - findley_stress1
    findley_stress = findley_stress1 + ds/da*(a800 - evaluated_findley_parameters[idx[0]])
    n = findley_stress.shape[0]

    with open(dante_pickle_directory + 'data_utmis_' + simulation.specimen + '.pkl') as pickle_handle:
        dante_data = pickle.load(pickle_handle)

    with open(pickle_directory_geometry + 'nodal_coordinates_' + simulation.specimen + '.pkl') as pickle_handle:
        nodal_positions = pickle.load(pickle_handle)

    findley_stress[nodal_positions[:, 0] > 11.] = 0

    steel_data = SteelData(HV=dante_data['HV'].reshape(n/8, 8))

    fem_data = FEM_data(stress=findley_stress.reshape(n/8, 8),
                        steel_data=steel_data,
                        nodal_positions=nodal_positions.reshape(n/8, 8, 3))

    fit_material = SS2506MaterialTemplate(a1, a2, b)
    size_factor = 4
    if simulation.R < 0:
        size_factor = 8
    wl_evaluator = WeakestLinkEvaluator(data_volume=fem_data, data_area=None, size_factor=size_factor)
    return wl_evaluator.calculate_pf(material=fit_material)


def residual(parameters, *data):
    simulation_list, = data
    job_list = [(calc_pf_for_simulation, (sim, parameters), {}) for sim in simulation_list]
    pf_wl = np.array(multi_processer(job_list, timeout=100, delay=0))
    r = (pf_wl - 0.5) ** 2
    # r[abs(pf_wl - 0.5) < 0.15] = 0
    print parameters, pf_wl, np.sum(r)
    return np.sum(r)


findley_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/stresses/findley/')
dante_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data'
                                            '/dante/')
pickle_directory_geometry = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/geometry/')
findley_parameter_directories = glob.glob(findley_pickle_directory + 'a800=*/')
findley_parameter_directories = [os.path.normpath(directory).split(os.sep)[-1]
                                 for directory in findley_parameter_directories]
evaluated_findley_parameters = [directory[5:] for directory in findley_parameter_directories]
evaluated_findley_parameters = [float(parameter.replace('_', '.')) for parameter in evaluated_findley_parameters]
evaluated_findley_parameters = np.array(sorted(evaluated_findley_parameters))

if __name__ == '__main__':

    par = np.array([1.9, 1260, 8.18])

    simulations = [Simulation(specimen='smooth', R=-1., stress=760.),
                   #Simulation(specimen='smooth', R=0., stress=424.),
                   Simulation(specimen='notched', R=-1., stress=439.),
                   Simulation(specimen='notched', R=0., stress=237.)]

    print fmin(residual, par, (simulations,))

