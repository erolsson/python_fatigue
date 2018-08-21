import os
import pickle

from collections import namedtuple

import numpy as np
from scipy.optimize import fmin

from materials.gear_materials import SteelData
from materials.gear_materials import SS2506MaterialTemplate

from multiprocesser.multiprocesser import multi_processer

from weakest_link.weakest_link_gear import WeakestLinkEvaluatorGear
from weakest_link.weakest_link_gear import FEM_data


def calc_pf_for_simulation(cd, load, par):
    if par[1] < 0:
        par[1] *= -1

    fit_material = SS2506MaterialTemplate(par[0], par[1], 11.06e6)
    findley_file_name = 'findley/pulsator/findley_CD=' + str(cd).replace('.', '_') + \
                        '_Pamp=' + str(load).replace('.', '_') + 'kN.pkl'
    with open(data_directory + findley_file_name) as findley_pickle:
        stress = pickle.load(findley_pickle)
    n_vol = stress.shape[0]

    with open(data_directory + 'dante/data_' + str(cd).replace('.', '_') + '.pkl') as dante_pickle:
        dante_data = pickle.load(dante_pickle)
    steel_data_volume = SteelData(HV=dante_data['HV'].reshape(n_vol / 8, 8))

    with open(data_directory + 'geometry/nodal_positions.pkl') as position_pickle:
        position = pickle.load(position_pickle)

    fem_volume = FEM_data(stress=stress.reshape(n_vol / 8, 8),
                          steel_data=steel_data_volume,
                          nodal_positions=position.reshape(n_vol / 8, 8, 3))

    wl_evaluator = WeakestLinkEvaluatorGear(data_volume=fem_volume, data_area=None, size_factor=4)
    return wl_evaluator.calculate_pf(material=fit_material)


def residual(par, *data):
    simulation_list = data
    job_list = [(calc_pf_for_simulation, (sim.cd, sim.load, par), {}) for sim in simulation_list]
    pf_wl = multi_processer(job_list, timeout=100, delay=0)
    pf_target = [sim.pf_experimental for sim in simulation_list]
    res = np.sum((np.array(pf_wl) - np.array(pf_target))**2)
    print res, par, pf_wl
    return res


if __name__ == '__main__':
    mesh = '1x'
    data_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' + mesh + '/')
    SimulationsToProcess = namedtuple('SimulationsToProcess', ['cd', 'load', 'pf_experimental'])
    simulations = [SimulationsToProcess(cd=0.5, load=30., pf_experimental=0.25),
                   SimulationsToProcess(cd=0.5, load=33., pf_experimental=0.99),

                   SimulationsToProcess(cd=0.8, load=30., pf_experimental=0.01),
                   SimulationsToProcess(cd=0.8, load=34., pf_experimental=0.9),

                   SimulationsToProcess(cd=1.1, load=33., pf_experimental=0.1),
                   SimulationsToProcess(cd=1.1, load=36., pf_experimental=0.9),

                   SimulationsToProcess(cd=1.4, load=34., pf_experimental=0.1),
                   SimulationsToProcess(cd=1.4, load=37., pf_experimental=0.9)]

    print fmin(residual, [138, 0.76], tuple(simulations))
