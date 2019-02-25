from collections import namedtuple
import os
import shutil

from case_hardening_toobox import CaseHardeningToolbox
from case_hardening_toobox import write_geometry_files_for_dante

from diffusitivity import write_diffusion_file

from materials.gear_materials import SS2506

Simulation = namedtuple('Simulation', ['simulation_directory', 'times', 'temperatures', 'carbon', 'tempering'])

current_directory = os.getcwd()
specimen_name = 'utmis_gear'
simulations = [Simulation(simulation_directory=specimen_name + '_two_stage',
                          times=[60., 30], temperatures=[930., 840.], carbon=[1.1, 0.8], tempering=(200, 7200))]

# This is the main directory where all simulation folders will be placed
simulation_directory = os.path.expanduser('~/scania_gear_analysis/abaqus/' + specimen_name + '_tempering_2h_200C/')

# In this directory all common files for all heat treatment simulations will be placed
include_file_directory = simulation_directory + 'include_files/'

# This file contains all nodes, elements and sets to be further processed by the script
geometry_file_name = '../planetary_gear/input_files/gear_models/utmis_gear/tooth_part_model_file.inp'

# All included files will be named after this like include_file_name_geo.inc or include_file_name_sets.inc
include_file_name = specimen_name

# Path to interaction property file, should not be changed
interaction_property_file = 'data_files/interaction_properties.inc'

# Name of the diffusion file, will be created in include_file_directory
diffusion_file_name = 'diffusivity.inc'

# Material, needs a python dict with material composition to generate the diffusion file
material = SS2506

# Dante material name, list of valid dante materials, check dante_path/DANTEDB3_6/STD and dante_path/DANTEDB3_6/USR
dante_material = 'U925062'

# writes the necessary geometry files and set files to include_file_directory
write_geometry_files_for_dante(geometry_data_file=geometry_file_name,
                               directory_to_write=include_file_directory,
                               dante_include_file_name=include_file_name,
                               str_to_remove_from_set_names='')

# Path to the boundary conditions file, copied to the include_file_directory
bc_file = '../planetary_gear/input_files/gear_models/quarter_gear_tooth_bc.inc'
shutil.copyfile(bc_file, include_file_directory + '/' + include_file_name + '_BC.inc')

# Copying the interaction property file to the include file directory
shutil.copyfile(interaction_property_file, include_file_directory + '/interaction_properties.inc')

for simulation in simulations:
    inc_file_directory = os.path.relpath(include_file_directory, simulation_directory + simulation.simulation_directory)
    toolbox_writer = CaseHardeningToolbox(name=specimen_name,
                                          include_file_name=specimen_name,
                                          include_file_directory=inc_file_directory)

    toolbox_writer.diffusion_file = diffusion_file_name
    toolbox_writer.interaction_property_file = 'interaction_properties.inc'
    toolbox_writer.heating_data.carbon = 0.5
    toolbox_writer.heating_data.time = 90.
    toolbox_writer.heating_data.temperature = 930.

    toolbox_writer.quenching_data.time = 3600.
    toolbox_writer.quenching_data.temperature = 120.

    toolbox_writer.tempering_data.temperature = simulation.tempering[0]
    toolbox_writer.tempering_data.time = simulation.tempering[1]
    toolbox_writer.material = dante_material

    toolbox_writer.add_carburization_steps(times=simulation.times, temperatures=simulation.temperatures,
                                           carbon_levels=simulation.carbon)
    directory_name = simulation_directory + '/' + simulation.simulation_directory

    if not os.path.isdir(directory_name):
        os.makedirs(directory_name)
    os.chdir(directory_name)
    toolbox_writer.write_files()
    os.chdir(current_directory)

write_diffusion_file(filename=include_file_directory + diffusion_file_name,
                     material=material)
