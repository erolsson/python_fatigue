from collections import namedtuple
import os
import shutil

from case_hardening_toobox import CaseHardeningToolbox
from case_hardening_toobox import write_geometry_files_for_dante

tempering = (180, 7200)  # Tempering temperature and time

Simulation = namedtuple('Simulation', ['CD', 'times', 'temperatures', 'carbon', 'tempering'])

# Simulations to generate files for
simulations = [Simulation(CD=0.5, times=[75., 5., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8),
                          tempering=tempering),
               Simulation(CD=0.8, times=[135., 30., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8),
                          tempering=tempering)]

current_directory = os.getcwd()
for specimen_name in ['utmis_gear']:
    simulation_directory = specimen_name + '/'
    write_geometry_files_for_dante('../planetary_gear/input_files/gear_models/utmis_gear/tooth_part_model_file.inp',
                                   simulation_directory, specimen_name)

    shutil.copyfile('data_files/diffusivity_2506.inc', simulation_directory + '/diffusivity_2506.inc')
    shutil.copyfile('data_files/interaction_properties.inc', simulation_directory + '/interaction_properties.inc')
    shutil.copyfile('../planetary_gear/input_files/gear_models/quarter_gear_tooth_bc.inc',
                    simulation_directory + '/' + specimen_name + '_BC.inc')
    for simulation in simulations:

        toolbox_writer = CaseHardeningToolbox(name=specimen_name,
                                              include_file_name=specimen_name)
        toolbox_writer.include_file_directory = '../'
        toolbox_writer.diffusion_file = 'diffusivity_2506.inc'
        toolbox_writer.interaction_property_file = 'interaction_properties.inc'
        toolbox_writer.heating_data.carbon = 0.5
        toolbox_writer.heating_data.time = 90.
        toolbox_writer.heating_data.temperature = 930.

        toolbox_writer.quenching_data.time = 3600.
        toolbox_writer.quenching_data.temperature = 120.

        toolbox_writer.tempering_data.temperature = simulation.tempering[0]
        toolbox_writer.tempering_data.time = simulation.tempering[1]

        toolbox_writer.add_carburization_steps(times=simulation.times, temperatures=simulation.temperatures,
                                               carbon_levels=simulation.carbon)
        directory_name = simulation_directory + '/' + specimen_name + '_' + str(simulation.CD).replace('.', '_')

        if not os.path.isdir(directory_name):
            os.makedirs(directory_name)
        os.chdir(directory_name)
        toolbox_writer.write_files()
        os.chdir(current_directory)
