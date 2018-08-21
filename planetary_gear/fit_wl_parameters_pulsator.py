import pickle
from materials.gear_materials import SteelData
from collections import namedtuple

from scipy.optimize import fmin


def calc_pf_for_simulation(cd, load):
    findley_file_name = 'findley/pulsator/findley_CD=' + str(cd).replace('.', '_') + \
                        '_Pamp=' + str(load).replace('.', '_') + 'kN.pkl'
    with open(data_directory + findley_file_name) as findley_pickle:
        stress = pickle.load(findley_pickle)[:, 2]
    print np.max(stress)
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
    return wl_evaluator.calculate_pf()

def residual(par, simulation_list):
    for sim in simulation_list:

SimulationsToProcess = namedtuple('SimulationsToProcess', ['cd', 'load', 'pf_experimental'])
simulations = [SimulationsToProcess(cd=0.5, load=31., pf_experimental=0.50),
               SimulationsToProcess(cd=0.5, load=32., pf_experimental=0.75),

               SimulationsToProcess(cd=0.8, load=32., pf_experimental=0.40),
               SimulationsToProcess(cd=0.8, load=33., pf_experimental=0.60),

               SimulationsToProcess(cd=1.1, load=34., pf_experimental=0.50),
               SimulationsToProcess(cd=1.1, load=35., pf_experimental=0.75),

               SimulationsToProcess(cd=1.4, load=35., pf_experimental=0.50),
               SimulationsToProcess(cd=1.4, load=36., pf_experimental=0.75)]

