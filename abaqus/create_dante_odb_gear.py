from odbAccess import *
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

import glob
import pickle

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance
from odb_io_functions import write_field_to_odb
from odb_io_functions import flip_node_order

from materials.hardess_convertion_functions import HRC2HV


def create_dante_step(odb_name, pickle_directory, results_step_name):
    pickle_files = glob.glob(pickle_directory + '/*.pkl')
    data_dict = {}
    stress_file = [filename for filename in pickle_files if '_S.pkl' in filename][0]
    simulation_name = stress_file[:-5]
    for pickle_file in pickle_files:
        prefix = pickle_file[len(simulation_name):-4]
        with open(pickle_file, 'r') as pickle_handle:
            pickle.load(pickle_handle)
            pickle.load(pickle_handle)
            data_dict[prefix] = pickle.load(pickle_handle)

    scalar_fields = data_dict.keys()
    scalar_fields.remove('S')

    for scalar_field in scalar_fields:
        field = data_dict[scalar_field]
        write_field_to_odb(field_data=field, field_id=scalar_field, odb_file_name=odb_name,
                           step_name=results_step_name, instance_name='tooth_right', frame_number=0)
        field = flip_node_order(field, axis='z')
        write_field_to_odb(field_data=field, field_id=scalar_field, odb_file_name=odb_name,
                           step_name=results_step_name, instance_name='tooth_left', frame_number=0)

    stress = data_dict['S']
    write_field_to_odb(field_data=stress, field_id='S', odb_file_name=odb_name, step_name=results_step_name,
                       instance_name='tooth_right', frame_number=0,
                       invariants=[MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL])
    stress = flip_node_order(stress, axis='z')
    stress[:, 3:5] *= -1
    write_field_to_odb(field_data=data_dict['S'], field_id='S', odb_file_name=odb_name, step_name=results_step_name,
                       instance_name='tooth_left', frame_number=0,
                       invariants=[MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL])

    hv = HRC2HV(data_dict['SDV_HARDNESS'])
    write_field_to_odb(field_data=hv, field_id='HV', odb_file_name=odb_name, step_name=results_step_name,
                       instance_name='tooth_right', frame_number=0)
    hv = flip_node_order(hv, axis='z')
    write_field_to_odb(field_data=hv, field_id='HV', odb_file_name=odb_name, step_name=results_step_name,
                       instance_name='tooth_left', frame_number=0)


if __name__ == '__main__':
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/mesh_1x/'
    base_pickle_directory = '/scratch/users/erik/scania_gear_analysis/pickles/heat_treatment/mesh_1x/fem_results/'
    base_pickle_directory += 'tempering_2h_180C_20190129/'

    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xpos.inc'
    nodes_pos, elements_pos = read_nodes_and_elements(input_file_name)
    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xneg.inc'
    nodes_neg, elements_neg = read_nodes_and_elements(input_file_name)

    instances = [OdbInstance(name='tooth_right', nodes=nodes_pos, elements=elements_pos),
                 OdbInstance(name='tooth_left', nodes=nodes_neg, elements=elements_neg)]

    odb_file_name = dante_odb_path + 'dante_results_tempering_2h_180C.odb_20190129'
    create_odb(odb_file_name=odb_file_name, instance_data=instances)

    for cd in [0.5, 0.8, 1.1, 1.4]:
        create_dante_step(odb_name=odb_file_name,
                          pickle_directory=base_pickle_directory + 'case_depth_' + str(cd).replace('.', '_'),
                          results_step_name='dante_results_' + str(cd).replace('.', '_'))