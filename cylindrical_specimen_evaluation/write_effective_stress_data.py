import sys

import cPickle as pickle

from collections import namedtuple

import numpy as np
import matplotlib.pyplot as plt

from materials.hardess_convertion_functions import HRC2HV
from materials.gear_materials import SteelData
from materials.gear_materials import SS2506
from cylindrical_specimen_evaluation.test_results import TestResults
from cylindrical_specimen_evaluation.test_results import Loading
from post_processing_functions import get_radial_data_from_pickle

from multiaxial_fatigue.findleyEvaluationFunctions import evaluateFindley


def create_load_sequence(stresses, factors, cycles):
    if not len(stresses) == len(factors) and len(stresses) == len(cycles):
        print "The number of stress states, factors and cycles must be the same"
        sys.exit(1)
    increments = len(cycles[0])
    for cycle in cycles:
        if not len(cycle) == increments:
            print "The number of increments must be the same for all cycles"
            sys.exit(1)
    rows, columns = stresses[0].shape
    stress_history = np.zeros((increments, rows, columns))
    for i in range(0, len(stresses)):
        for inc in range(0, increments):
            stress_history[inc, :, :] += stresses[i]*factors[i]*cycles[i][inc]
    return stress_history


class TestSeries:
    mech_directory = r'/home/erolsson/postDoc/cylindrical_specimen/FEMData/Mechanical/'
    r, unit_load = get_radial_data_from_pickle(mech_directory + 'unitLoad_line.pkl')
    _, unit_torque = get_radial_data_from_pickle(mech_directory + 'unitTorque_line.pkl')
    const_amp = np.array([1, 1])

    def __init__(self, sim_directory, hardness_adjustment=0):
        self.loadings = []

        # Read hardness
        _, self.hardness = get_radial_data_from_pickle(sim_directory + '/hardness_line.pkl')
        self.hardness = HRC2HV(self.hardness)
        _, self.residual_stress = get_radial_data_from_pickle(sim_directory + '/residualStresses_line.pkl')

        self.hardness = (self.hardness[0] + (self.hardness[-1] + hardness_adjustment)/self.hardness[-1] *
                         (self.hardness - self.hardness[0]))

        self.hardness = self.hardness.flatten()

    def get_stress_state(self, loading_data):
        amp_force = loading_data.Fa * np.array([-1, 1]) + loading_data.Fm * TestSeries.const_amp
        amp_torque = loading_data.Ma * np.array([-1, 1]) + loading_data.Mm * TestSeries.const_amp
        stress_state = create_load_sequence([TestSeries.unit_load, TestSeries.unit_torque, self.residual_stress],
                                            [1., 1., 1.],
                                            [amp_force, amp_torque, TestSeries.const_amp])
        return stress_state

    def hardness_line(self):
        pass


def create_findley_evaluation_data(sim_dict, loading_data):
    num_points = TestSeries.r.shape[0]
    stress_history = np.zeros((2, num_points*len(loading_data), 6))
    hardness = np.zeros(num_points*len(loading_data))
    for i, load_data in enumerate(loading_data):
        sim = sim_dict[load_data[0]]
        stress_history[:, i*num_points:(i+1)*num_points, :] = sim.get_stress_state(load_data[1])
        hardness[i*num_points:(i+1)*num_points] = sim.hardness
    steel_data = SteelData(HV=hardness)

    return stress_history, steel_data

if __name__ == '__main__':
    test_results = TestResults(r'/home/erolsson/postDoc/cylindrical_specimen/testResults.csv')
    test_results.adjust_runouts()
    number_of_cases = 0
    fem_directory = r'/home/erolsson/postDoc/cylindrical_specimen/FEMData/'

    simulations = {1: TestSeries(sim_directory=fem_directory + 'HeatTreatment1', hardness_adjustment=0),
                   4: TestSeries(sim_directory=fem_directory + 'HeatTreatment4', hardness_adjustment=-125),
                   5: TestSeries(sim_directory=fem_directory + 'HeatTreatment5', hardness_adjustment=-125)}

    excluded_loadings = {1: [(0, 0)], 4: 'all'}
    loadings_fit = []
    loadings_plot = []
    LoadSeries = namedtuple('LoadSeries', ['sm', 'tm', 'amplitude', 'min', 'max', 'inc'])
    load_series_plot = {1: [LoadSeries(sm=0, tm=0, amplitude='ta', min=300, max=550, inc=12.5),
                            LoadSeries(sm=200, tm=0, amplitude='ta', min=275, max=550, inc=12.5),
                            LoadSeries(sm=0, tm=0, amplitude='sa', min=400, max=800, inc=12.5)],
                        4: [LoadSeries(sm=0, tm=0, amplitude='ta', min=400, max=550, inc=12.5),
                            LoadSeries(sm=500, tm=0, amplitude='ta', min=250, max=400, inc=12.5)],
                        5: [LoadSeries(sm=0, tm=0, amplitude='ta', min=450, max=600, inc=12.5),
                            LoadSeries(sm=500, tm=0, amplitude='ta', min=275, max=400, inc=12.5)]}

    for ht, simulation in simulations.iteritems():
        load_cases = test_results.get_loadings(heat_treatment=ht)
        exclude = excluded_loadings.get(ht, [])
        if not exclude == 'all':
            for exclude_data in exclude:
                load_cases = load_cases[load_cases[:, exclude_data[0]] == exclude_data[1], :]
            loadings_fit += [(ht, Loading(*load_case)) for load_case in load_cases]
    load_history, steel_properties = create_findley_evaluation_data(simulations, loadings_fit)

    for ht, load_series_data in load_series_plot.iteritems():
        for load_series in load_series_data:
            amp_data = np.arange(load_series.min, load_series.max+load_series.inc, load_series.inc, )
            for amp in amp_data:
                data = {'sm': load_series.sm, 'tm': load_series.tm, 'sa': 0, 'ta': 0}

                data[load_series.amplitude] = amp
                loadings_plot.append((ht, Loading(**data)))
    loadings_plot

    findley_k = SS2506.findley_k(steel_properties)
    findley_stress = evaluateFindley(load_history, findley_k, workerRunOutTime=1000, chunkSize=200)
    findley_stress = findley_stress[:, 2].reshape((findley_stress.shape[0]/TestSeries.r.shape[0],
                                                   TestSeries.r.shape[0]))

    print findley_stress

    pickle_handle = open('findley_data_fit.pkl', 'w')
    pickle.dump(loadings_fit, pickle_handle)
    pickle.dump(findley_stress, pickle_handle)
    pickle_handle.close()

    load_history, steel_properties = create_findley_evaluation_data(simulations, loadings_plot)
    findley_k = SS2506.findley_k(steel_properties)
    findley_stress = evaluateFindley(load_history, findley_k, workerRunOutTime=1000, chunkSize=200)
    findley_stress = findley_stress[:, 2].reshape((findley_stress.shape[0] / TestSeries.r.shape[0],
                                                   TestSeries.r.shape[0]))

    print findley_stress

    plt.show()
