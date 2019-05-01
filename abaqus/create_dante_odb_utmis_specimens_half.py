from odbAccess import *
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

import os

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance

from odb_io_functions import read_field_from_odb
from odb_io_functions import write_field_to_odb
from odb_io_functions import flip_node_order

from materials.hardess_convertion_functions import HRC2HV


def create_dante_step(from_odb_name, to_odb_name, results_step_name, from_step=None):
    # Inspect the odb to get available data
    # Inspect the odb to get available data
    from_odb = openOdb(from_odb_name, readOnly=False)
    if from_step is None:
        step_name, _ = from_odb.steps.items()[-1]
    else:
        step_name = from_step
    scalar_variables = from_odb.steps[step_name].frames[-1].fieldOutputs.keys()
    from_odb.close()
    if 'NT11' in scalar_variables:
        scalar_variables.remove('NT11')

    if 'U' in scalar_variables:
        scalar_variables.remove('U')

    if 'S' in scalar_variables:
        scalar_variables.remove('S')

    data_dict = {}
    for scalar_variable in scalar_variables:
        print "reading variable", scalar_variable
        data_dict[scalar_variable] = read_field_from_odb(scalar_variable, from_odb_name, step_name, -1)
    data_dict['S'] = read_field_from_odb('S', from_odb_name, step_name, -1)
    data_dict['HV'] = HRC2HV(data_dict['SDV_HARDNESS'])
    scalar_variables.append('S')

    for scalar_variable in scalar_variables:
        field = data_dict[scalar_variable]
        write_field_to_odb(field_data=field, field_id=scalar_variable, odb_file_name=to_odb_name,
                           step_name=results_step_name, instance_name='specimen_part_pos', frame_number=0)
        field = flip_node_order(field, axis='z')
        write_field_to_odb(field_data=field, field_id=scalar_variable, odb_file_name=to_odb_name,
                           step_name=results_step_name, instance_name='specimen_part_neg', frame_number=0)

    stress = data_dict['S']
    write_field_to_odb(field_data=stress, field_id='S', odb_file_name=to_odb_name, step_name=results_step_name,
                       instance_name='specimen_part_pos', frame_number=0,
                       invariants=[MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL])
    stress = flip_node_order(stress, axis='z')
    stress[:, 3] *= -1
    stress[:, 5] *= -1
    write_field_to_odb(field_data=stress, field_id='S', odb_file_name=to_odb_name, step_name=results_step_name,
                       instance_name='specimen_part_neg', frame_number=0,
                       invariants=[MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL])


if __name__ == '__main__':
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/utmis_specimens/'

    times = [75, 5, 30]
    temps = [930, 840, 840]
    carbon_levels = [1.1, 0.8, 0.8]
    tempering = (200, 7200)
    name = ''

    for t, T, c in zip(times, temps, carbon_levels):
        name += str(t) + 'min' + str(T) + 'C' + str(c).replace('.', '') + 'wtC'

    if not os.path.isdir(dante_odb_path):
        os.makedirs(dante_odb_path)
    for specimen in ['smooth', 'notched']:
        specimen_name = 'utmis_' + specimen
        input_file_name = '/scratch/users/erik/python_fatigue/fatigue_specimens/UTMIS/utmis_' + specimen + \
                          '/utmis_' + specimen + '.inc'
        nodes_pos, elements_pos = read_nodes_and_elements(input_file_name)
        nodes_neg, elements_neg = read_nodes_and_elements(input_file_name)
        nodes_neg[:, 2] *= -1

        elements_neg[:, 1:5], elements_neg[:, 5:9] = elements_pos[:, 5:9], elements_pos[:, 1:5].copy()

        instances = [OdbInstance(name='specimen_part_pos', nodes=nodes_pos, elements=elements_pos),
                     OdbInstance(name='specimen_part_neg', nodes=nodes_neg, elements=elements_neg)]
        odb_file_name = dante_odb_path + 'utmis_' + specimen + 'half.odb'
        create_odb(odb_file_name=odb_file_name, instance_data=instances)

        simulation_odb = os.path.expanduser('~/scania_gear_analysis/utmis_specimens_U925062/' + specimen
                                            + '_tempering_2h_' + str(tempering[0]) + '_cooldown_80C/'
                                            + specimen_name + '_' + name + 'Toolbox_Mechanical_utmis_'
                                            + specimen + 'odb')
        create_dante_step(simulation_odb, odb_file_name,
                          'dante_results_tempering_2h_')
