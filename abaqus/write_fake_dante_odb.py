from odbAccess import *
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance

from odb_io_functions import read_field_from_odb
from odb_io_functions import write_field_to_odb
from odb_io_functions import cylindrical_system_z
from odb_io_functions import flip_node_order


def create_dante_step(results_odb_name, carbon_odb_name, stress_odb_name, results_step_name):
    f = read_field_from_odb(field_id='CONC', odb_file_name=carbon_odb_name, element_set_name='GEARELEMS',
                            step_name='Carburization-3', frame_number=-1)

    hardness = -1.95704040e+09*f**3 + 1.79113930e+07*f**2 + 5.50685403e+04*f + 2.27359677e+02
    write_field_to_odb(field_data=hardness, field_id='HV', odb_file_name=results_odb_name, step_name=results_step_name,
                       instance_name='tooth_right', frame_number=0)

    hardness = flip_node_order(hardness, axis='z')
    write_field_to_odb(field_data=hardness, field_id='HV', odb_file_name=results_odb_name, step_name=results_step_name,
                       instance_name='tooth_left', frame_number=0)

    stress = read_field_from_odb(field_id='S', odb_file_name=stress_odb_name, element_set_name='GEARELEMS',
                                 step_name='Equilibrium', frame_number=-1, coordinate_system=cylindrical_system_z)
    write_field_to_odb(field_data=stress, field_id='S', odb_file_name=results_odb_name, step_name=results_step_name,
                       instance_name='tooth_right', frame_number=0,
                       invariants=[MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL])

    stress = flip_node_order(stress, axis='z')
    stress[:, 3] *= -1
    write_field_to_odb(field_data=stress, field_id='S', odb_file_name=results_odb_name, step_name=results_step_name,
                       instance_name='tooth_left', frame_number=0,
                       invariants=[MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL])


if __name__ == '__main__':
    carbon_odb_path = '/scratch/users/erik/python_fatigue/planetary_gear/input_files/resolve_residual_stresses/'
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/fake_heat_treatment/'

    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xpos.inc'
    nodes_pos, elements_pos = read_nodes_and_elements(input_file_name)
    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xneg.inc'
    nodes_neg, elements_neg = read_nodes_and_elements(input_file_name)

    instances = [OdbInstance(name='tooth_right', nodes=nodes_pos, elements=elements_pos),
                 OdbInstance(name='tooth_left', nodes=nodes_neg, elements=elements_neg)]

    tooth_odb_file_name = dante_odb_path + 'dante_results_fake.odb'
    create_odb(odb_file_name=tooth_odb_file_name, instance_data=instances)

    for cd in ['0_5', '0_8', '1_1', '1_4']:
        create_dante_step(results_odb_name=tooth_odb_file_name,
                          carbon_odb_name=carbon_odb_path + 'Toolbox_Carbon_' + cd + '_quarter.odb',
                          stress_odb_name=dante_odb_path + 'residual_stresses_' + cd + '.odb',
                          results_step_name='dante_results_' + cd)
