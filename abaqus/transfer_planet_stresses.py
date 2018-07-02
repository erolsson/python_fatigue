import os
from collections import namedtuple
from subprocess import Popen

from odbAccess import *
from abaqusConstants import *

from input_file_reader.input_file_functions import read_nodes_and_elements

from create_odb import create_odb
from create_odb import OdbInstance


def transfer_gear_stresses(from_odb_name, to_odb_name):
    Frame = namedtuple('Frame', ['step', 'number', 'time'])

    # inspect odb to find steps in frames
    simulation_odb = openOdb(from_odb_name, readOnly=True)
    step_names = [name for name in simulation_odb.steps.keys() if 'loading_tooth' in name]
    step_names = sorted(step_names)
    frames = []

    for step_name in step_names:
        t0 = simulation_odb.steps[step_name].total_time
        frames_in_step = simulation_odb.steps[step_name].frames
        for frame_number in range(len(frames_in_step)):
            frames.append(Frame(step=step_name, number=frame_number, time=t0 + frames_in_step[frame_number].frameValue))
    simulation_odb.close()

    write_odb = openOdb(to_odb_name, readOnly=True)
    if 'mechanical_stresses' in write_odb.steps:
        frame_counter = len(write_odb.steps['mechanical_stresses'].frames)
    else:
        frame_counter = 0
    write_odb.close()

    for frame in frames:
        process = Popen('abaqus viewer noGUI=_copy_planet_stress.py -- ' + from_odb_name + ' ' + to_odb_name + ' '
                        + frame.step + ' ' + str(frame.number) + ' ' + str(frame_counter) + ' ' + str(frame.time),
                        cwd=os.getcwd(), shell=True)
        process.wait()
        frame_counter += 1

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

    create_odb(odb_file_name=tooth_odb_file_name, instance_data=instances)

    # Importing stress history from the planet-sun simulations
    simulation_odb_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                          'input_files/planet_sun/planet_sun_400_Nm.odb'
    transfer_gear_stresses(simulation_odb_name, tooth_odb_file_name)

    simulation_odb_name = '/scratch/users/erik/python_fatigue/planetary_gear/' \
                          'input_files/planet_ring/planet_ring_400_Nm.odb'
    transfer_gear_stresses(simulation_odb_name, tooth_odb_file_name)
