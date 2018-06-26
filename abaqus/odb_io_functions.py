from odbAccess import *
import numpy as np
from abaqusConstants import *


class CoordinateSystem:
    def __init__(self, name, origin, point1, point2, system_type=CYLINDRICAL):
        self.name = name

        self.origin = origin
        self.point1 = point1
        self.point2 = point2

        self.system_type = system_type


def read_field_from_odb(field_id, odb_file_name, element_set_name, step_name, frame_number, instance_name=None,
                        coordinate_system=None):
    odb = odbAcess.openOdb(odb_file_name, readOnly=True)
    if instance_name is None:
        instance_name = odb.rootAssembly.instances.keys()[0]
    element_set = odb.rootAssembly.instances[instance_name].elementSets[element_set_name]
    field = odb.steps[step_name].frames[frame_number].fieldOutputs[field_id].getSubset(region=element_set)
    field = field.getSubset(position=ELEMENT_NODAL)

    if coordinate_system is not None:
        if coordinate_system.name not in odb.rootAssembly.datumCsyses:
            transform_system = odb.rootAssembly.DatumCsysByThreePoints(name=coordinate_system.name,
                                                                       coordSysType=coordinate_system.type,
                                                                       origin=coordinate_system.origin,
                                                                       point1=coordinate_system.point1,
                                                                       point2=coordinate_system.point2)
        else:
            transform_system = odb.rootAssembly.datumCsyses[coordinate_system.name]
        field = field.getTransformedField(transform_system)

    field = field.values

    n1 = len(field)
    n2 = 1 if type(field[0].data) is float else len(field[0].data)

    data = np.zeros((n1, n2))
    for i, data_point in enumerate(field):
        data[i, :] = data_point.data

    odb.close()
    return data


def write_field_to_odb(field_data, field_id, odb_file_name, element_set_name, step_name, instance_name=None,
                       step_description='', frame_value=None, field_description='', invariants=None):
    odb = odbAcess.openOdb(odb_file_name, readOnly=False)

    if step_name not in odb.steps:
        step = odb.Step(name=step_name,  description=step_description, domain=TIME, timePeriod=1)
    else:
        step = odb.steps[step_name]

    if instance_name is None:
        instance = odb.rootAssembly.instances[odb.rootAssembly.instances.keys()[0]]
    else:
        instance = odb.rootAssembly.instances[instance_name]

    if element_set_name in odb.rootAssembly.elementSets.keys():
        elements = odb.rootAssembly.elementSets[element_set_name].elements
    else:
        elements = odb.rootAssembly.instances[instance_name].elementSets[element_set_name].elements
    element_numbers = []
    for e in elements:
        element_numbers.append(e.label)

    field_types = {1: SCALAR, 6: TENSOR_3D_FULL}

    if len(field_data.shape) == 1:
        field_data = field_data[:, np.newaxis]
    field_type = field_types[field_data.shape[1]]
    field_data_to_frame = tuple(field_data[:, :])
    if frame_value is None:
        frame_value = step.frames[-1].frameValue + 1.0
    frame = step.Frame(incrementNumber=len(step.frames)+1, frameValue=frame_value, description='stress components')

    if invariants is None:
        invariants = []
    if field_id in frame.fieldOutputs:
        field = frame.fieldOutputs[field_id]
    else:
        field = frame.FieldOutput(name=field_id, description=field_description, type=field_type,
                                  validInvariants=invariants)
    field.addData(position=ELEMENT_NODAL, instance=instance, labels=element_numbers, data=field_data_to_frame)
    odb.update()
    odb.save()
    odb.close()
