from __future__ import print_function

import os

from odbAccess import openOdb
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

from python_fatigue.input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance

from odb_io_functions import read_field_from_odb
from odb_io_functions import write_field_to_odb
from odb_io_functions import flip_node_order

from python_fatigue.materials.hardess_convertion_functions import HRC2HV
from python_fatigue.input_file_reader.input_file_reader import InputFileReader
from python_fatigue.planetary_gear.gear_input_file_functions import create_quarter_model, mirror_quarter_model


def create_dante_step(from_odb_name, to_odb_name, results_step_name, from_step=None):
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

    if 'E' in scalar_variables:
        scalar_variables.remove('E')

    if 'S' in scalar_variables:
        scalar_variables.remove('S')

    data_dict = {}
    for scalar_variable in scalar_variables:
        print("reading variable", scalar_variable)
        data_dict[scalar_variable] = read_field_from_odb(scalar_variable, from_odb_name, step_name, -1)
    data_dict['S'] = read_field_from_odb('S', from_odb_name, step_name, -1)

    for scalar_field in scalar_variables:
        field = data_dict[scalar_field]
        write_field_to_odb(field_data=field, field_id=scalar_field, odb_file_name=to_odb_name,
                           step_name=results_step_name, instance_name='tooth_right', frame_number=0)
        field = flip_node_order(field, axis='z')
        write_field_to_odb(field_data=field, field_id=scalar_field, odb_file_name=to_odb_name,
                           step_name=results_step_name, instance_name='tooth_left', frame_number=0)

    stress = data_dict['S']
    write_field_to_odb(field_data=stress, field_id='S', odb_file_name=to_odb_name, step_name=results_step_name,
                       instance_name='tooth_right', frame_number=0,
                       invariants=[MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL])
    stress = flip_node_order(stress, axis='z')
    stress[:, 3:5] *= -1
    write_field_to_odb(field_data=data_dict['S'], field_id='S', odb_file_name=to_odb_name, step_name=results_step_name,
                       instance_name='tooth_left', frame_number=0,
                       invariants=[MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL])

    hv = HRC2HV(data_dict['SDV_HARDNESS'])
    write_field_to_odb(field_data=hv, field_id='HV', odb_file_name=to_odb_name, step_name=results_step_name,
                       instance_name='tooth_right', frame_number=0)
    hv = flip_node_order(hv, axis='z')
    write_field_to_odb(field_data=hv, field_id='HV', odb_file_name=to_odb_name, step_name=results_step_name,
                       instance_name='tooth_left', frame_number=0)

    bainite = data_dict['SDV_UBAINITE'] + data_dict['SDV_LBAINITE']
    write_field_to_odb(field_data=bainite, field_id='BAINITE', odb_file_name=to_odb_name, step_name=results_step_name,
                       instance_name='tooth_right', frame_number=0)
    bainite = flip_node_order(bainite, 'z')
    write_field_to_odb(field_data=bainite, field_id='BAINITE', odb_file_name=to_odb_name, step_name=results_step_name,
                       instance_name='tooth_left', frame_number=0)


if __name__ == '__main__':
    dante_odb_path = os.path.expanduser('~/scania_gear_analysis/odb_files/heat_treatment/mesh_1x/')
    simulation_directory = os.path.expanduser('~/scania_gear_analysis/heat_simulation_dante_3/carbon_potential/')

    input_file_name = os.path.expanduser('~/python_projects/python_fatigue/planetary_gear/'
                                         'input_files/quarter_tooth_tilt2.inp')
    reader = InputFileReader()
    reader.read_input_file(input_file_name)
    nodes_pos, elements_pos = reader.nodal_data, reader.elements['C3D8']
    nodes_neg, elements_neg = mirror_quarter_model(nodes_pos, elements_pos)

    instances = [OdbInstance(name='tooth_right', nodes=nodes_pos, elements=elements_pos),
                 OdbInstance(name='tooth_left', nodes=nodes_neg, elements=elements_neg)]

    odb_file_name = dante_odb_path + 'carbon_potential.odb'
    create_odb(odb_file_name=odb_file_name, instance_data=instances)

    for cd in [0.5, 0.8, 1.1, 1.4]:
        simulation_odb = simulation_directory + 'CD' + str(cd).replace('.', '') + '/'
        simulation_odb += 'Toolbox_Cooling_VBC_gear.odb'
        create_dante_step(from_odb_name=simulation_odb,
                          to_odb_name=odb_file_name,
                          results_step_name='dante_results_' + str(cd).replace('.', '_'),
                          from_step='cooling')
