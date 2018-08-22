import odbAccess
from abaqusConstants import NODAL, TIME

import numpy as np

from create_odb import OdbInstance
from create_odb import create_odb

from input_file_reader.input_file_functions import read_nodes_and_elements

from odb_io_functions import read_field_from_odb
from odb_io_functions import write_field_to_odb


def create_node_field_from_element_field(fields, odb_file_name, element_set_name, step_name, frame_number,
                                         instance_name):
    data_dict = {}
    for i, field in enumerate(fields):
        element_field, node_labels, _ = read_field_from_odb(field, odb_file_name, element_set_name=element_set_name,
                                                            step_name=step_name, frame_number=frame_number,
                                                            instance_name=instance_name, get_position_numbers=True)

        if i == 0:
            nodal_data = {node_label: {f: [] for f in fields} for node_label in node_labels}
        for field_value, node_label in zip(element_field, node_labels):
            nodal_data[node_label][field].append(field_value[0])
        data_dict[field] = np.zeros(len(nodal_data))
        for j, node_label in enumerate(sorted(nodal_data.keys())):
            data_array = nodal_data[node_label][field]
            data_dict[field][j] = sum(data_array)/len(data_array)
    return data_dict


def expansion(martensite, carbon, lower_bainite, upper_bainite):
    carb = carbon*100
    dv = (3.216 + 0.859*carb - 0.343*carb*carb)*martensite # (4.64-1.43*carb)*lower_bainite +
        #  (4.64-2.21*carb)*upper_bainite)
    # dv = 168*carbon*martensite + 78*carbon*lower_bainite + (-4.64+221*carbon)*austenite
    # dv = (3.216+85.9*carbon + 343*carbon*carbon)*martensite
    return dv/300


if __name__ == '__main__':
    mesh = '1x'
    dante_odb_filename = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/mesh_' + \
                         mesh + '/dante_results.odb'
    expansion_odb_filename = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/mesh_' + \
                             mesh + '/expansion.odb'

    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xpos.inc'
    nodes_pos, elements_pos = read_nodes_and_elements(input_file_name)

    instances = [OdbInstance(name='PART-1-1', nodes=nodes_pos, elements=elements_pos)]

    create_odb(odb_file_name=expansion_odb_filename, instance_data=instances)

    fields_to_process = ['SDV_Q_MARTENSITE', 'SDV_CARBON', 'SDV_AUSTENITE', 'SDV_LBAINITE', 'SDV_UBAINITE']
    # for cd in [0.5, 0.8, 1.1, 1.4]:
    for cd in [0.5]:
        dante_step_name = 'dante_results_' + str(cd).replace('.', '_')
        node_data = create_node_field_from_element_field(fields_to_process, dante_odb_filename, None,
                                                         dante_step_name, 0, 'tooth_right')
        for field_id, data in node_data.iteritems():
            write_field_to_odb(data, field_id, expansion_odb_filename, dante_step_name, position=NODAL,
                               instance_name='PART-1-1', frame_number=0)

        odb = odbAccess.openOdb(expansion_odb_filename)
        if 'expansion' + str(cd).replace('.', '_') not in odb.steps.keys():
            expansion_step = odb.Step(name='expansion' + str(cd).replace('.', '_'),
                                      description='', domain=TIME, timePeriod=1)
            expansion_step.Frame(incrementNumber=0, frameValue=0, description='')
            expansion_step.Frame(incrementNumber=1, frameValue=1., description='')
        else:
            expansion_step = odb.steps['expansion' + str(cd).replace('.', '_')]

        m = odb.steps[dante_step_name].frames[0].fieldOutputs['SDV_Q_MARTENSITE']
        c = odb.steps[dante_step_name].frames[0].fieldOutputs['SDV_CARBON']
        lb = odb.steps[dante_step_name].frames[0].fieldOutputs['SDV_LBAINITE']
        ub = odb.steps[dante_step_name].frames[0].fieldOutputs['SDV_UBAINITE']
        au = odb.steps[dante_step_name].frames[0].fieldOutputs['SDV_AUSTENITE']

        expansion_strain = expansion(m, c, lb, ub)
        start_frame = expansion_step.frames[0]
        end_frame = expansion_step.frames[1]

        start_frame.FieldOutput(name='NT11', field=0*expansion_strain)
        end_frame.FieldOutput(name='NT11', field=expansion_strain)
        odb.save()
        odb.close()
