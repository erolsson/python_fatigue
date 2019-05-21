from collections import namedtuple
import os
import pickle

import numpy as np

from abaqus_files.odb_io_functions import read_field_from_odb

from input_file_reader.input_file_reader import InputFileReader

if __name__ == '__main__':
    pickle_path = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/mechanical_data/')
    mechanical_simulation_path = '/scratch/users/erik/scania_gear_analysis/abaqus/utmis_specimens_mechanical/'
    FEMSimulation = namedtuple('FEMSimulation', ['specimen', 'stress', 'R'])
    cycle_number = 2
    specimen_loads = {'smooth': {-1.: [737.], 0.: [425., 440.]},
                      'notched': {-1.: [427., 450.], 0.: [225., 240., 255.]}}
    simulations = []
    reader = InputFileReader()
    positions = None
    for specimen, data in specimen_loads.iteritems():
        for R, stress_levels in data.iteritems():
            simulations += [FEMSimulation(specimen=specimen, stress=s, R=R) for s in stress_levels]

    for simulation in simulations:
        stress_data = {}
        name = 'utmis_' + simulation.specimen + '_' + str(simulation.stress).replace('.', '_') + '_R='  \
               + str(int(simulation.R))
        print "writing data for odb", name
        odb_name = mechanical_simulation_path + 'utmis_' + simulation.specimen + '/' + name + '.odb'
        for level in ['min', 'max']:
            step_name = 'step_' + str(cycle_number) + '_' + level + '_load'
            stress, node_labels, _ = read_field_from_odb('S', odb_name, step_name, frame_number=-1,
                                                         element_set_name='EXPOSED_ELEMENTS',
                                                         instance_name='specimen_part_pos'.upper(),
                                                         get_position_numbers=True)
            n = stress.shape[0]
            stress_data[level] = np.zeros((2*n, 6))
            if positions is None:
                geom_file = 'utmis_' + simulation.specimen + '/utmis_' + simulation.specimen + '.inc'
                reader.read_input_file(geom_file)
                nodal_coords = reader.nodal_data
                positions = np.zeros((2*n, 3))
                for i, label in node_labels:
                    positions[i, :] = nodal_coords[label - 1, 1:]
                positions[n:, :] = positions[:n, :]
                positions[n:, 1] *= -1
            stress_data[level][:n, :] = stress
            stress_data[level][n:, :] = read_field_from_odb('S', odb_name, step_name, frame_number=-1,
                                                            element_set_name='EXPOSED_ELEMENTS',
                                                            instance_name='specimen_part_neg'.upper())
        with open(pickle_path + '_surface_stresses_' + name, 'w') as pickle_handle:
            pickle.dump(stress_data, pickle_handle)
            pickle.dump(positions, pickle_handle)
