from collections import namedtuple

from odbAccess import *
from abaqusConstants import *

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance

from odb_io_functions import read_field_from_odb
from odb_io_functions import write_field_to_odb
from odb_io_functions import CoordinateSystem


def transfer_gear_stresses(from_odb_name, to_odb_name):
    Frame = namedtuple('Frame', ['step', 'number'])
    planet_system = CoordinateSystem(name='planet_system', origin=(0., 83.5, 0.), point1=(0.0, 1.0, 0.0),
                                     point2=(1.0, 0.0, 0.0), system_type=CYLINDRICAL)
    # inspect odb to find steps in frames
    simulation_odb = openOdb(from_odb_name, readOnly=True)
    step_names = [name for name in simulation_odb.steps.keys() if 'loading_tooth' in name]
    step_names = sorted(step_names)
    frames = []

    for step_name in step_names:
        for frame_number in range(len(simulation_odb.steps[step_name].frames)):
            frames.append(Frame(step=step_name, number=frame_number))
    simulation_odb.close()

    for frame in frames:
        stress_data = read_field_from_odb('S', from_odb_name, 'GEARELEMS', frame.step, frame.number,
                                          instance_name='EVAL_TOOTH_0', coordinate_system=planet_system)
        write_field_to_odb(stress_data, 'S', to_odb_name, 'GEARELEMS', frame.step, instance_name='tooth_left')


if __name__ == '__main__':
    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xpos.inc'
    nodes_pos, elements_pos = read_nodes_and_elements(input_file_name)

    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xneg.inc'
    nodes_neg, elements_neg = read_nodes_and_elements(input_file_name)

    instances = [OdbInstance(name='tooth_right', nodes=nodes_pos, elements=elements_pos),
                 OdbInstance(name='tooth_left', nodes=nodes_neg, elements=elements_neg)]

    tooth_odb_file_name = '/scratch/users/erik/scania_gear_analysis/odb_files/planet_gear_stresses.odb'

    create_odb(odb_file_name=tooth_odb_file_name,
               instance_data=instances)

    # Importing stress history from the planet-sun simulations
    simulation_odb_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                          'input_files/planet_sun/planet_sun_400_Nm.odb'
    transfer_gear_stresses(simulation_odb_name, tooth_odb_file_name)
