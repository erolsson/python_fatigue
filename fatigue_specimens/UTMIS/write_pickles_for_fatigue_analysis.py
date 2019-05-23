from collections import namedtuple
import os
import pickle

import numpy as np

from abaqus_files.odb_io_functions import add_element_set
from abaqus_files.odb_io_functions import read_field_from_odb

from abaqus_files.write_nodal_coordinates import get_list_from_set_file

from input_file_reader.input_file_reader import InputFileReader

from create_sets_for_fatigue_evaluation import create_sets_for_fatigue_evaluation

pickle_path = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/mechanical_data/')
mechanical_simulation_path = '/scratch/users/erik/scania_gear_analysis/abaqus/utmis_specimens_mechanical/'

FEMSimulation = namedtuple('FEMSimulation', ['specimen', 'stress', 'R'])
cycle_number = 2
specimen_loads = {'smooth': {-1.: [737., 774., 820.], 0.: [425., 440.]},
                  'notched': {-1.: [427., 450.], 0.: [225., 240., 255.]}}

element_set_name = 'fatigue_volume_elements'

if __name__ == '__main__':
    create_sets_for_fatigue_evaluation()
    simulations = []
    reader = InputFileReader()
    positions = {'smooth': None, 'notched': None}
    for specimen, data in specimen_loads.iteritems():
        for R, stress_levels in data.iteritems():
            simulations += [FEMSimulation(specimen=specimen, stress=s, R=R) for s in stress_levels]

    for simulation in simulations:
        name = 'utmis_' + simulation.specimen + '_' + str(simulation.stress).replace('.', '_') + '_R='  \
               + str(int(simulation.R))

        element_labels = get_list_from_set_file('utmis_' + simulation.specimen + '/' +
                                                element_set_name + '_' + simulation.specimen + '.inc')
        print "The element set", element_set_name, "has ", len(element_labels), "elements"

        print "writing data for odb", name

        odb_name = mechanical_simulation_path + 'utmis_' + simulation.specimen + '/' + name + '.odb'
        add_element_set(odb_name, element_set_name, element_labels, instance_name='SPECIMEN_PART_POS')
        add_element_set(odb_name, element_set_name, element_labels, instance_name='SPECIMEN_PART_NEG')
        simulation_data = {'S': None, 'HV': None, 'pos': None}
        HV_pos, node_labels, _ = read_field_from_odb('FV1', odb_name, 'relax', frame_number=-1,
                                                     element_set_name=element_set_name,
                                                     instance_name='specimen_part_pos'.upper(),
                                                     get_position_numbers=True)

        HV_neg = read_field_from_odb('FV1', odb_name, 'relax', frame_number=-1,
                                     element_set_name=element_set_name,
                                     instance_name='specimen_part_pos'.upper())

        n = HV_pos.shape[0]
        simulation_data['S'] = np.zeros((2, 2*n, 6))
        simulation_data['HV'] = np.zeros((2*n, 1))
        simulation_data['HV'][:n] = HV_pos
        simulation_data['HV'][n:] = HV_neg

        if positions[simulation.specimen] is None:
            geom_file = 'utmis_' + simulation.specimen + '/utmis_' + simulation.specimen + '.inc'
            reader.read_input_file(geom_file)
            nodal_coords = reader.nodal_data
            pos = np.zeros((2*n, 3))
            for i, label in enumerate(node_labels):
                pos[i, :] = nodal_coords[label - 1, 1:]
            pos[n:, :] = pos[:n, :]
            pos[n:, 1] *= -1
            positions[simulation.specimen] = pos

        simulation_data['pos'] = positions[simulation.specimen]
        for step, level in enumerate(['min', 'max']):
            step_name = 'step_' + str(cycle_number) + '_' + level + '_load'
            stress = read_field_from_odb('S', odb_name, step_name, frame_number=-1, element_set_name=element_set_name,
                                         instance_name='specimen_part_pos'.upper())

            simulation_data['S'][step, :n, :] = stress
            simulation_data['S'][step, n:, :] = read_field_from_odb('S', odb_name, step_name, frame_number=-1,
                                                                    element_set_name=element_set_name,
                                                                    instance_name='specimen_part_neg'.upper())

        with open(pickle_path + 'fatigue_pickle_' + name + '.pkl') as pickle_handle:
            pickle.dump(simulation_data, pickle_handle)
