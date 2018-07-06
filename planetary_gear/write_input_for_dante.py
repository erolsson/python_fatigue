import os
from collections import namedtuple

from input_file_reader.input_file_functions import write_geom_include_file

from gear_input_file_functions import create_quarter_model
from gear_input_file_functions import write_sets_file


def write_input_files(sim_data):
    def write_carburization_step(step_name, t1, t2, carbon):
        carbon_lines.append('*STEP,NAME=' + step_name + ', INC=10000')
        carbon_lines.append('\t' + step_name + ' - Total time: ' + str(t1) + ' - ' +
                            str(t2) + 's, Carbon: ' + str(carbon) + '%')
        carbon_lines.append('*MASS DIFFUSION, DCMAX=0.001')
        carbon_lines.append('\t0.2,  ' + str(t2 - t1) + ', 1e-05,  10000')
        carbon_lines.append('*TEMPERATURE, AMPLITUDE=TEMP_AMPLITUDE')
        carbon_lines.append('\tAll_Nodes')
        carbon_lines.append('*BOUNDARY')
        carbon_lines.append('\tEXPOSED_NODES, 11, 11, ' + str(carbon / 100))
        carbon_lines.append('*MONITOR, NODE=monitor_node, DOF=11, FREQ=1')
        carbon_lines.append('*Output, field, frequency=1')
        carbon_lines.append('*Node Output')
        carbon_lines.append('\tNNC, NT')
        carbon_lines.append('*Element Output, directions=YES')
        carbon_lines.append('\tCONC')
        carbon_lines.append('*Element Output, directions=YES,  POSITION=NODES')
        carbon_lines.append('\tCONC')
        carbon_lines.append('*End Step')

        thermal_lines.append('*STEP,NAME=' + step_name + ', INC=10000')
        thermal_lines.append('*HEAT TRANSFER, DELTMX=10.0, END=PERIOD')
        thermal_lines.append('\t0.01,  ' + str(t2 - t1) + ', 1e-05,  10000')
        thermal_lines.append('*CONTROLS, PARAMETERS = LINE SEARCH')
        thermal_lines.append('\t6,')
        thermal_lines.append('*CONTROLS, PARAMETERS = TIME INCREMENTATION')
        thermal_lines.append('\t20, 30')
        thermal_lines.append('*CONTROLS, FIELD = TEMPERATURE, PARAMETERS = FIELD')
        thermal_lines.append('\t0.05, 0.05')
        thermal_lines.append('*SFILM, OP = NEW, AMPLITUDE=TEMP_AMPLITUDE')
        thermal_lines.append('\tEXPOSED_SURFACE, F, 1.000000, FURNACE')
        thermal_lines.append('*MONITOR, NODE = MONITOR_NODE, DOF=11, FREQ=1')
        thermal_lines.append('*RESTART, WRITE, FREQ=1000')
        thermal_lines.append('**')
        thermal_lines.append('*OUTPUT, FIELD, FREQ=200')
        thermal_lines.append('*ELEMENT OUTPUT')
        thermal_lines.append('\tSDV1, SDV21, SDV34, SDV47, SDV60, SDV73, SDV86, HFL')
        thermal_lines.append('*OUTPUT, FIELD, FREQ=10')
        thermal_lines.append('*NODE OUTPUT')
        thermal_lines.append('\tNT')
        thermal_lines.append('**')
        thermal_lines.append('*EL FILE, FREQUENCY=0')
        thermal_lines.append('*NODE FILE, FREQUENCY=1')
        thermal_lines.append('\tNT')
        thermal_lines.append('*EL PRINT, FREQ=0')
        thermal_lines.append('*NODE PRINT, FREQ=0')
        thermal_lines.append('**')
        thermal_lines.append('**')
        thermal_lines.append('*END STEP')

        mechanical_lines.append('*STEP,NAME=' + step_name + ', INC=10000')
        mechanical_lines.append('Mechanical simulation')
        mechanical_lines.append('**')
        mechanical_lines.append('*STATIC')
        mechanical_lines.append('\t0.01, 5800, 1e-05, 10000')
        mechanical_lines.append('*TEMPERATURE, FILE=Toolbox_Thermal_' + str(sim_data.CD).replace('.', '_') +
                                '_quarter.odb, BSTEP=' + str(step_idx) + ', ESTEP=' + str(step_idx))
        mechanical_lines.append('** Add convergence control parameters')
        mechanical_lines.append('*CONTROLS, PARAMETERS = LINE  SEARCH')
        mechanical_lines.append('\t6,')
        mechanical_lines.append('*CONTROLS, PARAMETERS = TIME INCREMENTATION')
        mechanical_lines.append('20, 30')
        mechanical_lines.append('*CONTROLS, FIELD = DISPLACEMENT, PARAMETERS = FIELD')
        mechanical_lines.append('\t0.05, 0.05')
        mechanical_lines.append('**')
        mechanical_lines.append('** Add output variables')
        mechanical_lines.append('*RESTART, WRITE, FREQ = 1000')
        mechanical_lines.append('*MONITOR, NODE = MONITOR_NODE, DOF = 1, FREQ = 1')
        mechanical_lines.append('**')
        mechanical_lines.append('*OUTPUT, FIELD, FREQ = 10')
        mechanical_lines.append('*ELEMENT OUTPUT, directions = YES')
        mechanical_lines.append('\tS')
        mechanical_lines.append('**')
        mechanical_lines.append('*OUTPUT, FIELD, FREQ = 10')
        mechanical_lines.append('*ELEMENT OUTPUT')
        mechanical_lines.append('\tSDV1, SDV2, SDV5, SDV21, SDV34, SDV47, SDV60, SDV73, SDV86, SDV99')
        mechanical_lines.append('*OUTPUT, FIELD, FREQ = 10')
        mechanical_lines.append('*NODE OUTPUT')
        mechanical_lines.append('\tNT, U')
        mechanical_lines.append('*END  STEP')

    def write_generic_data(simulation_type):
        file_lines = []
        with open('input_files/dante_quarter/generic_' + simulation_type + '_file.txt') as generic_file:
            for generic_line in generic_file:
                generic_line = generic_line.replace('\n', '')
                file_lines.append(generic_line)
        return file_lines

    carbon_lines = write_generic_data('Carbon')
    thermal_lines = write_generic_data('Thermal')
    mechanical_lines = write_generic_data('Mechanical')

    for line_set in [carbon_lines, thermal_lines]:
        total_time = 5400.
        line_set.append('*AMPLITUDE, NAME=TEMP_AMPLITUDE, TIME=TOTAL TIME, VALUE=ABSOLUTE')
        for t, temp in zip(sim_data.times, sim_data.temperatures):
            line_set.append('\t ' + str(total_time + 60.) + ', \t ' + str(temp))
            total_time += t * 60
            line_set.append('\t ' + str(total_time) + ', \t ' + str(temp))
        line_set.append('**')
    step_idx = 1
    write_carburization_step('Heating', 0, 5400, 0.5)
    step_idx = 2
    total_time = 5400.
    step_nr = 1
    for t, carb in zip(sim_data.times, sim_data.carbon):
        write_carburization_step('Carburization - ' + str(step_nr), total_time, total_time + t * 60, carb)
        step_nr += 1
        step_idx += 1
        total_time += t * 60

    # Add remaining data to the thermal and mechanical file
    for lines, name in [(thermal_lines, 'Thermal'), (mechanical_lines, 'Mechanical')]:
        with open('input_files/dante_quarter/end_' + name + '_file.txt') as end_file:
            end_lines = end_file.readlines()
            for line in end_lines:
                line = line.replace('/scratch/sssnks/VBC_Fatigue/VBC_v6/VBC_fatigue_0_5/', '')
                line = line.replace('0_5_v6', str(sim_data.CD).replace('.', '_') + '_quarter')
                line = line.replace('\n', '')
                lines.append(line)

    # Write the input files
    for lines, name in [(carbon_lines, 'Carbon'), (thermal_lines, 'Thermal'), (mechanical_lines, 'Mechanical')]:
        with open('input_files/dante_quarter/VBC_fatigue_' + str(sim_data.CD).replace('.', '_') + '/Toolbox_' +
                  name + '_' + str(sim_data.CD).replace('.', '_') + '_quarter.inp', 'w') as inp_file:
            for line_to_write in lines:
                inp_file.write(line_to_write + '\n')
            inp_file.write('**EOF')

if __name__ == '__main__':
    sim_directory = 'input_files/dante_quarter/'
    Simulation = namedtuple('Simulation', ['CD', 'times', 'temperatures', 'carbon'])
    simulations = [Simulation(CD=0.5, times=[75., 5., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8)),
                   Simulation(CD=0.8, times=[135., 30., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8)),
                   Simulation(CD=1.1, times=[370., 70., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8)),
                   Simulation(CD=1.4, times=[545., 130., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8))]

    quarter_nodes, quarter_elements = create_quarter_model('input_files/gear_models/planet_gear/dense_mesh_planet.inc')

    write_sets_file(filename='input_files/dante_quarter/planetGear_Sets.inc',
                    full_model_sets_file='input_files/gear_models/planet_gear/dense_mesh_planet_sets.inc',
                    nodal_data=quarter_nodes,
                    element_data=quarter_elements,
                    monitor_node=60674)

    write_geom_include_file(quarter_nodes, quarter_elements, simulation_type='Carbon',
                            filename='input_files/dante_quarter/Toolbox_Carbon_quarter_geo.inc')
    write_geom_include_file(quarter_nodes, quarter_elements, simulation_type='Thermal',
                            filename='input_files/dante_quarter/Toolbox_Thermal_quarter_geo.inc')
    write_geom_include_file(quarter_nodes, quarter_elements, simulation_type='Mechanical',
                            filename='input_files/dante_quarter/Toolbox_Mechanical_quarter_geo.inc')

    for sim in simulations:
        if not os.path.isdir(sim_directory + 'VBC_fatigue_' + str(sim.CD).replace('.', '_')):
            os.makedirs(sim_directory + 'VBC_fatigue_' + str(sim.CD).replace('.', '_'))
        write_input_files(sim)
