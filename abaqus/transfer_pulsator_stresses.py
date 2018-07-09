import os
from collections import namedtuple
from subprocess import Popen

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance


def transfer_gear_stresses(from_odb_name, to_odb_name):
    Frame = namedtuple('Frame', ['step', 'number', 'time'])
    frames = []
    loads = [30., 35., 40.]
    for load in loads:
        step_name = 'Pamp_' + str(load).replace('.', '_') + 'kN'
        frames.append(Frame(step=step_name + '_min', number=-1, time=0))
        frames.append(Frame(step=step_name + '_max', number=-1, time=1))

    for frame in frames:
        process = Popen('abaqus viewer noGUI=_copy_pulsator_stress.py -- ' + from_odb_name + ' ' + to_odb_name + ' '
                        + frame.step + ' ' + str(frame.number) + ' ' + frame.step[:-4],
                        cwd=os.getcwd(), shell=True)
        process.wait()

if __name__ == '__main__':
    input_file_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                      'input_files/planet_sun/planet_dense_geom_xpos.inc'
    nodes_pos, elements_pos = read_nodes_and_elements(input_file_name)

    instances = [OdbInstance(name='tooth_right', nodes=nodes_pos, elements=elements_pos)]

    tooth_odb_file_name = '/scratch/users/erik/scania_gear_analysis/odb_files/pulsator/pulsator_stresses.odb'

    create_odb(odb_file_name=tooth_odb_file_name, instance_data=instances)

    # Importing stress history from the planet-sun simulations
    simulation_odb_name = '/scratch/users/erik/scania_gear_analysis/odb_files/pulsator/pulsator_simulation.odb'
    transfer_gear_stresses(simulation_odb_name, tooth_odb_file_name)
