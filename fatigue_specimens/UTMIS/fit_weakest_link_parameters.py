from collections import namedtuple

import numpy as np
from scipy.optimize import fmin

from materials.gear_materials import SteelData
from materials.gear_materials import SS2506MaterialTemplate

from multiprocesser.multiprocesser import multi_processer

from weakest_link.weakest_link_evaluator import WeakestLinkEvaluator
from weakest_link.weakest_link_evaluator import FEM_data

from weakest_link_functions import dante_data
from weakest_link_functions import evaluated_findley_parameters
from weakest_link_functions import findley_data
from weakest_link_functions import geometry_data
from weakest_link_functions import Simulation


def calc_pf_for_simulation(simulation, parameters):
    a800 = parameters[0]
    a1 = parameters[1]
    a2 = 0
    b = parameters[2]

    idx = np.argsort(np.abs(evaluated_findley_parameters - a800))[:2]
    a800_levels = evaluated_findley_parameters[idx]

    # Loading Findley pickles for the found values
    findley_stress1 = findley_data[simulation.specimen][simulation.R][simulation.stress][a800_levels[0]]
    findley_stress2 = findley_data[simulation.specimen][simulation.R][simulation.stress][a800_levels[1]]

    da = evaluated_findley_parameters[idx[1]] - evaluated_findley_parameters[idx[0]]
    ds = findley_stress2 - findley_stress1
    findley_stress = findley_stress1 + ds/da*(a800 - evaluated_findley_parameters[idx[0]])
    print findley_stress
    n = findley_stress.shape[0]

    nodal_positions = geometry_data[simulation.specimen]

    findley_stress[nodal_positions[:, 0] > 11.] = 0

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


def residual(parameters, *data):
    simulation_list, = data
    job_list = [(calc_pf_for_simulation, (simulation, parameters), {}) for simulation in simulation_list]
    pf_wl = np.array(multi_processer(job_list, timeout=100, delay=0))
    r = (pf_wl - experimental_pf) ** 2
    r[abs(pf_wl - experimental_pf) < 0.1] = 0
    print '============================================================================================================'
    print 'parameters:\t\t', parameters
    print 'pf_experimental:\t', ' '.join(np.array_repr(pf_wl).replace('\n', '').replace('\r', '').split())
    print 'r_vec:\t\t\t', ' '.join(np.array_repr(r).replace('\n', '').replace('\r', '').split())
    print 'R:\t\t\t', np.sqrt(np.sum(r))/10
    return np.sum(r)


if __name__ == '__main__':
    par = np.array([0.8, 800, 12.])

    simulations = [Simulation(specimen='smooth', R=-1., stress=737., failures=1, run_outs=4),
                   Simulation(specimen='smooth', R=-1., stress=774., failures=4, run_outs=2),
                   Simulation(specimen='smooth', R=-1., stress=820., failures=3, run_outs=1),
                   Simulation(specimen='smooth', R=0., stress=425., failures=2, run_outs=3),
                   Simulation(specimen='smooth', R=0., stress=440., failures=4, run_outs=2),
                   Simulation(specimen='notched', R=-1., stress=427., failures=2, run_outs=4),
                   Simulation(specimen='notched', R=-1., stress=450., failures=5, run_outs=3),
                   Simulation(specimen='notched', R=0., stress=225., failures=2, run_outs=3),
                   Simulation(specimen='notched', R=0., stress=240., failures=2, run_outs=4),
                   Simulation(specimen='notched', R=0., stress=255., failures=4, run_outs=0)]
    experimental_pf = np.array([float(sim.failures) / (sim.failures + sim.run_outs) for sim in simulations])
    print fmin(residual, par, (simulations,))
