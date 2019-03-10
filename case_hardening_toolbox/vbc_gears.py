from collections import namedtuple
import os
import shutil

from input_file_reader.input_file_functions import write_geom_include_file

from diffusitivity import write_diffusion_file

from materials.gear_materials import SS2506

from planetary_gear.gear_input_file_functions import create_quarter_model
from planetary_gear.gear_input_file_functions import write_sets_file

from case_hardening_toobox import CaseHardeningToolbox

if __name__ == '__main__':
    mesh = '1x'
    simulation_directory = os.path.expanduser('~/scania_gear_analysis/VBC_gear'
                                              '/dante_quarter_1x_tempering_180C_80C_cool/')
    include_file_directory = simulation_directory + 'include_files'

    if not os.path.isdir(include_file_directory):
        os.makedirs(include_file_directory)

    # writes the necessary geometry files and set files to include_file_directory

    quarter_nodes, quarter_elements = create_quarter_model('../planetary_gear/input_files/gear_models/planet_gear/mesh_'
                                                           + mesh + '/mesh_planet.inc')

    element_label_mapping = {}
    for i, element in enumerate(quarter_elements, 1):
        element_label_mapping[element[0]] = i

    monitor_node = {'1x': 60674, '2x': 143035, '3x': 276030}
    write_sets_file(filename=include_file_directory + '/VBC_quarter_sets.inc',
                    full_model_sets_file='../planetary_gear/input_files/gear_models/planet_gear/mesh_' + mesh +
                                         '/planet_sets.inc',
                    nodal_data=quarter_nodes,
                    element_data=quarter_elements,
                    monitor_node=monitor_node[mesh],
                    element_label_mapping=element_label_mapping)

    for i, element in enumerate(quarter_elements, 1):
        element[0] = i

    write_geom_include_file(quarter_nodes, quarter_elements, simulation_type='Carbon',
                            filename=include_file_directory + '/Toolbox_Carbon_VBC_quarter_geo.inc')
    write_geom_include_file(quarter_nodes, quarter_elements, simulation_type='Thermal',
                            filename=include_file_directory + '/Toolbox_Thermal_VBC_quarter_geo.inc')
    write_geom_include_file(quarter_nodes, quarter_elements, simulation_type='Mechanical',
                            filename=include_file_directory + '/Toolbox_Mechanical_VBC_quarter_geo.inc')

    bc_file = '../planetary_gear/input_files/gear_models/planet_gear/planetGear_BC.inc'
    shutil.copyfile(bc_file, include_file_directory + '/' + 'VBC_quarter_BC.inc')

    current_directory = os.getcwd()
    tempering = (180, 7200)

    Simulation = namedtuple('Simulation', ['CD', 'times', 'temperatures', 'carbon', 'tempering'])
    simulations = [Simulation(CD=0.5, times=[75., 5., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8),
                              tempering=tempering),
                   Simulation(CD=0.8, times=[135., 30., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8),
                              tempering=tempering),
                   Simulation(CD=1.1, times=[370., 70., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8),
                              tempering=tempering),
                   Simulation(CD=1.4, times=[545., 130., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8),
                              tempering=tempering)]

    for simulation in simulations:
        inc_file_directory = os.path.relpath(include_file_directory,
                                             simulation_directory + 'VBC_fatigue_' +
                                             str(simulation.CD).replace('.', '_'))
        toolbox_writer = CaseHardeningToolbox(name=str(simulation.CD).replace('.', '_') + '_quarter',
                                              include_file_name='VBC_quarter',
                                              include_file_directory=inc_file_directory)

        toolbox_writer.diffusion_file = 'diffusivity_2506.inc'
        toolbox_writer.interaction_property_file = 'interaction_properties.inc'
        toolbox_writer.heating_data.carbon = 0.5
        toolbox_writer.heating_data.time = 90.
        toolbox_writer.heating_data.temperature = 930.

        toolbox_writer.quenching_data.time = 3600.
        toolbox_writer.quenching_data.temperature = 120.

        toolbox_writer.cooldown_data.temperature = 80

        toolbox_writer.material = 'U925063'

        toolbox_writer.tempering_data.temperature = simulation.tempering[0]
        toolbox_writer.tempering_data.time = simulation.tempering[1]

        toolbox_writer.add_carburization_steps(times=simulation.times, temperatures=simulation.temperatures,
                                               carbon_levels=simulation.carbon)
        directory_name = simulation_directory + '/VBC_fatigue_' + str(simulation.CD).replace('.', '_')

        if not os.path.isdir(directory_name):
            os.makedirs(directory_name)
        os.chdir(directory_name)
        toolbox_writer.write_files()
        os.chdir(current_directory)

    write_diffusion_file(include_file_directory + '/diffusivity_2506.inc', SS2506)
    shutil.copyfile('data_files/interaction_properties.inc', include_file_directory + '/interaction_properties.inc')
