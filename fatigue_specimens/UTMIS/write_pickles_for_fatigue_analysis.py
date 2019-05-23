from collections import namedtuple
import os
import pickle

import numpy as np

from abaqus_files.odb_io_functions import add_element_set
from abaqus_files.odb_io_functions import read_field_from_odb

from abaqus_files.write_nodal_coordinates import get_list_from_set_file

from input_file_reader.input_file_reader import InputFileReader

from create_sets_for_fatigue_evaluation import create_sets_for_fatigue_evaluation

from abaqusConstants import ELEMENT_NODAL

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
        add_element_set(mechanical_simulation_path + name + '.odb', element_set_name, element_labels,
                        instance_name='PART')

        print "writing data for odb", name
        odb_name = mechanical_simulation_path + 'utmis_' + simulation.specimen + '/' + name + '.odb'
        stress_data = None
        for step, level in enumerate(['min', 'max']):
            step_name = 'step_' + str(cycle_number) + '_' + level + '_load'
            stress, node_labels, element_labels = read_field_from_odb('S', odb_name, step_name, frame_number=-1,
                                                                      element_set_name=element_set_name,
                                                                      instance_name='specimen_part_pos'.upper(),
                                                                      get_position_numbers=True)

            print read_field_from_odb('FV1', odb_name, step_name, frame_number=-1,
                                      element_set_name=element_set_name,
                                      instance_name='specimen_part_pos'.upper(),
                                      get_position_numbers=True)
            fghghff
            n = stress.shape[0]
            if stress_data is None:
                stress_data = np.zeros((2, 2*n, 6))
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
            stress_data[step, :n, :] = stress
            stress_data[step, n:, :] = read_field_from_odb('S', odb_name, step_name, frame_number=-1,
                                                           element_set_name=element_set_name,
                                                           instance_name='specimen_part_neg'.upper())


