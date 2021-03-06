from collections import namedtuple

import odbAccess
import numpy as np

from abaqusConstants import INTEGRATION_POINT, ELEMENT_NODAL, NODAL, CYLINDRICAL, CENTROID, ELEMENT_FACE, TIME
from abaqusConstants import SCALAR, TENSOR_3D_FULL


CoordinateSystem = namedtuple('CoordinateSystem', ['name', 'origin', 'point1', 'point2', 'system_type'])
cylindrical_system_z = CoordinateSystem(name='cylindrical', origin=(0., 0., 0.), point1=(1., 0., 0.),
                                        point2=(0., 1., 0.), system_type=CYLINDRICAL)


def read_field_from_odb(field_id, odb_file_name, step_name, frame_number, element_set_name=None, instance_name=None,
                        coordinate_system=None, rotating_system=False, position=ELEMENT_NODAL,
                        get_position_numbers=False, get_frame_value=False):
    odb = odbAccess.openOdb(odb_file_name, readOnly=False)

    if instance_name is None:
        if len(odb.rootAssembly.instances) == 1:
            element_base = odb.rootAssembly.instances[odb.rootAssembly.instances.keys()[0]]
        else:
            raise ValueError('odb has multiple instances, please specify an instance')
    else:
        element_base = odb.rootAssembly.instances[instance_name]
    if element_set_name is None:
        if 'ALL_ELEMENTS' not in element_base.elementSets:
            elements = element_base.elements
            element_base.ElementSet(name='ALL_ELEMENTS', elements=elements)
        element_set = element_base.elementSets['ALL_ELEMENTS']
    else:
        element_set = element_base.elementSets[element_set_name]

    if frame_number == -1:
        frame_number = len(odb.steps[step_name].frames) - 1
    field = odb.steps[step_name].frames[frame_number].fieldOutputs[field_id].getSubset(position=position)
    field = field.getSubset(region=element_set)
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

        if rotating_system:
            deformation_field = odb.steps[step_name].frames[frame_number].fieldOutputs['U']
            field = field.getTransformedField(transform_system, deformationField=deformation_field)
        else:
            field = field.getTransformedField(transform_system)
    field = field.values

    # ToDo: raise exception if field is empty
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


def write_field_to_odb(field_data, field_id, odb_file_name, step_name, instance_name=None, set_name=None,
                       step_description='', frame_number=None, frame_value=None, field_description='', invariants=None,
                       position=ELEMENT_NODAL):
    odb = odbAccess.openOdb(odb_file_name, readOnly=False)

    if step_name not in odb.steps:
        step = odb.Step(name=step_name, description=step_description, domain=TIME, timePeriod=1)
    else:
        step = odb.steps[step_name]

    if instance_name is None:
        instance = odb.rootAssembly.instances[odb.rootAssembly.instances.keys()[0]]
    else:
        instance = odb.rootAssembly.instances[instance_name]

    if position in [INTEGRATION_POINT, CENTROID, ELEMENT_NODAL, ELEMENT_FACE]:
        if set_name:
            objects = instance.elementSets[set_name].elements
        else:
            objects = instance.elements
    elif position == NODAL:
        if set_name:
            objects = instance.nodeSets[set_name].nodes
        else:
            objects = instance.nodes

    object_numbers = []
    for obj in objects:
        object_numbers.append(obj.label)

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
        frame = step.Frame(incrementNumber=len(step.frames)+1, frameValue=frame_value, description='')
    else:
        frame = step.frames[frame_number]

    if invariants is None:
        invariants = []
    if field_id in frame.fieldOutputs:
        field = frame.fieldOutputs[field_id]
    else:
        field = frame.FieldOutput(name=field_id, description=field_description, type=field_type,
                                  validInvariants=invariants)
    field.addData(position=position, instance=instance, labels=object_numbers, data=field_data_to_frame)
    odb.update()
    odb.save()
    odb.close()


def get_nodal_coordinates_from_node_set(odb_file_name, node_set_name, instance_name=None):
    odb = odbAccess.openOdb(odb_file_name, readOnly=True)
    if instance_name:
        node_set = odb.rootAssembly.instances[instance_name]
    else:
        node_set = odb.rootAssembly.nodeSets[node_set_name]
    node_dict = {}
    for node in node_set.nodes:
        node_dict[node.label] = node.coordinates
    odb.close()
    return node_dict


def flip_node_order(data, axis):      # ToDo implement flip around x and y axis as well
    if axis == 'z':
        for i in range(data.shape[0]/8):
            temp_data = np.copy(data[8*i:8*i+8])
            data[8*i:8*i+4] = temp_data[4:]
            data[8*i+4:8*i+8] = temp_data[:4]
    return data


def add_node_set(odb_file_name, node_set_name, labels, instance_name=None):
    odb = odbAccess.openOdb(odb_file_name, readOnly=False)
    if instance_name:
        base = odb.rootAssembly.instances[instance_name]
    else:
        base = odb.rootAssembly
    print base.nodeSets
    if node_set_name not in base.nodeSets:
        base.NodeSetFromNodeLabels(name=node_set_name, nodeLabels=labels)
    odb.save()
    odb.close()


def add_element_set(odb_file_name, element_set_name, labels, instance_name=None):
    odb = odbAccess.openOdb(odb_file_name, readOnly=False)
    if instance_name:
        base = odb.rootAssembly.instances[instance_name]
    else:
        if len(odb.rootAssembly.instances) == 1:
            base = odb.rootAssembly.instances[odb.rootAssembly.instances.keys()[0]]
        else:
            raise ValueError('odb has multiple instances, please specify an instance')
    if element_set_name not in base.elementSets:
        base.ElementSetFromElementLabels(name=element_set_name, elementLabels=labels)
    odb.save()
    odb.close()
