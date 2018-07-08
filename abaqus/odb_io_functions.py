from collections import namedtuple

import odbAccess
import numpy as np

from abaqusConstants import *


CoordinateSystem = namedtuple('CoordinateSystem', ['name', 'origin', 'point1', 'point2', 'system_type'])
cylindrical_system_z = CoordinateSystem(name='cylindrical', origin=(0., 0., 0.), point1=(0., 1., 0.),
                                        point2=(1., 0., 0.), system_type=CYLINDRICAL)


def read_field_from_odb(field_id, odb_file_name, element_set_name, step_name, frame_number, instance_name=None,
                        coordinate_system=None, position=ELEMENT_NODAL, get_position_numbers=False,
                        get_frame_value=False):
    odb = odbAccess.openOdb(odb_file_name, readOnly=True)
    if instance_name is None:
        instance_name = odb.rootAssembly.instances.keys()[0]
    element_set = odb.rootAssembly.instances[instance_name].elementSets[element_set_name]
    if frame_number == -1:
        frame_number = len(odb.steps[step_name].frames) - 1
    field = odb.steps[step_name].frames[frame_number].fieldOutputs[field_id].getSubset(region=element_set)
    field = field.getSubset(position=position)
    frame_value = odb.steps[step_name].frames[frame_number].frameValue
    if coordinate_system is not None:
        if coordinate_system.name not in odb.rootAssembly.datumCsyses:
            transform_system = odb.rootAssembly.DatumCsysByThreePoints(name=coordinate_system.name,
                                                                       coordSysType=coordinate_system.system_type,
                                                                       origin=coordinate_system.origin,
                                                                       point1=coordinate_system.point1,
                                                                       point2=coordinate_system.point2)
        else:
            transform_system = odb.rootAssembly.datumCsyses[coordinate_system.name]
        deformation_field = odb.steps[step_name].frames[frame_number].fieldOutputs['U']
        field = field.getTransformedField(transform_system, deformationField=deformation_field)

    field = field.values

    n1 = len(field)
    n2 = 1 if type(field[0].data) is float else len(field[0].data)

    data = np.zeros((n1, n2))
    node_labels = []
    element_labels = []
    for i, data_point in enumerate(field):
        data[i, :] = data_point.data
        if position in [NODAL, ELEMENT_NODAL]:
            node_labels.append(data_point.nodeLabel)
        elif position in [INTEGRATION_POINT, CENTROID, ELEMENT_NODAL, ELEMENT_FACE]:
            element_labels.append(data_point.elementLabel)
    odb.close()

    if not get_position_numbers and not get_frame_value:
        return data
    elif not get_position_numbers:
        return data, frame_value
    elif not get_frame_value:
        return data, node_labels, element_labels
    else:
        return data, frame_value, node_labels, element_labels


def write_field_to_odb(field_data, field_id, odb_file_name, step_name, instance_name=None, element_set_name=None,
                       step_description='', frame_number=None, frame_value=None, field_description='', invariants=None,
                       position=ELEMENT_NODAL):
    odb = odbAccess.openOdb(odb_file_name, readOnly=False)

    if step_name not in odb.steps:
        step = odb.Step(name=step_name,  description=step_description, domain=TIME, timePeriod=1)
    else:
        step = odb.steps[step_name]

    if instance_name is None:
        if element_set_name:
            elements = odb.rootAssembly.elementSets[element_set_name].elements
        else:
            elements = odb.rootAssembly.elements
        instance = odb.rootAssembly.instances[odb.rootAssembly.instances.keys()[0]]
    else:
        instance = odb.rootAssembly.instances[instance_name]
        if element_set_name:
            elements = odb.rootAssembly.instances[instance_name].elementSets[element_set_name].elements
        else:
            elements = odb.rootAssembly.instances[instance_name].elements

    element_numbers = []
    for e in elements:
        element_numbers.append(e.label)

    field_types = {1: SCALAR, 6: TENSOR_3D_FULL}

    if len(field_data.shape) == 1:
        field_data = field_data[:, np.newaxis]
    field_type = field_types[field_data.shape[1]]
    field_data_to_frame = tuple(field_data[:, :])
    if frame_value is None:
        if len(step.frames) > 0:
            frame_value = step.frames[len(step.frames)-1].frameValue + 1.0
        else:
            frame_value = 0.

    if frame_number is None or len(step.frames) == 0 or len(step.frames) <= frame_number:
        frame = step.Frame(incrementNumber=len(step.frames)+1, frameValue=frame_value, description='stress components')
    else:
        frame = step.frames[frame_number]

    if invariants is None:
        invariants = []
    if field_id in frame.fieldOutputs:
        field = frame.fieldOutputs[field_id]
    else:
        field = frame.FieldOutput(name=field_id, description=field_description, type=field_type,
                                  validInvariants=invariants)
    field.addData(position=position, instance=instance, labels=element_numbers, data=field_data_to_frame)
    odb.update()
    odb.save()
    odb.close()


def flip_node_order(data, axis):      # ToDo implement flip around x and y axis as well
    if axis == 'z':
        for i in range(data.shape[0]/8):
            temp_data = np.copy(data[8*i:8*i+8])
            data[8*i:8*i+4] = temp_data[8*i+4:]
            data[8*i+4:8*i+8] = temp_data[:8*i+4:]
    return data
