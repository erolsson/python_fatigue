import os
import re
from collections import namedtuple

import numpy as np


def read_nodes_and_elements(full_model_filename):
    nodes = []
    elements = []
    with open(full_model_filename) as full_model_file:
        lines = full_model_file.readlines()
        reading_nodes = False
        reading_elements = False

        for line in lines:
            if bool(re.search('node', line.split()[0], re.IGNORECASE)):
                reading_nodes = True
                reading_elements = False
            elif bool(re.search('element', line.split()[0], re.IGNORECASE)):
                reading_elements = True
                reading_nodes = False
            elif '*' in line.split()[0]:
                reading_nodes = False
                reading_elements = False
            elif reading_nodes:
                nodes.append(line.split(","))
            elif reading_elements:
                elements.append(line.split(","))
    nodal_data = np.zeros((len(nodes), 4))

    for i, node in enumerate(nodes):
        nodal_data[i, :] = node
    elements = np.array(elements, dtype=int)
    return nodal_data, elements


def get_elements_from_nodes(node_labels, all_elements):
    nodal_id_set = set(node_labels)
    # Find the elements corresponding to the model nodes
    element_data = []
    for element in all_elements:
        include = True
        for node in element[1:]:
            if int(node) not in nodal_id_set:
                include = False
        if include:
            element_data.append([int(e) for e in element])
    return np.array(element_data, dtype=int)


def create_quarter_model(full_model_file):
    nodal_data, elements = read_nodes_and_elements(full_model_file)
    # Only using nodes on positive z and positive z
    nodal_data = nodal_data[nodal_data[:, 1] >= -1e-5, :]
    nodal_data = nodal_data[nodal_data[:, 3] >= -1e-5, :]

    quarter_model_elements = get_elements_from_nodes(nodal_data[:, 0], elements)

    return nodal_data, quarter_model_elements


def write_sets(node_sets, element_sets):
    file_lines = ['** Include file for sets in a quarter model of a planetary gear for dante sim']

    def write_set_rows(data_to_write):
        data_line = ''
        counter = 0
        for item in data_to_write:
            data_line += str(int(item)) + ', '
            counter += 1
            if counter == 16 or item == data_to_write[-1]:
                file_lines.append(data_line[:-2])
                counter = 0
                data_line = ''

    for key, data in element_sets.iteritems():
        file_lines.append('*Elset, elset=' + key)
        write_set_rows(data)

    for key, data in node_sets.iteritems():
        file_lines.append('*Nset, nset=' + key)
        write_set_rows(data)
    return file_lines


def write_sets_file(filename, full_model_sets_file, nodal_data, element_data):
    exposed_surface = []
    exposed_nodes = []
    read_exposed_nodes = False
    read_exposed_surface = False

    nodal_id = np.array(nodal_data[:, 0], dtype=int)
    nodal_id_set = set(nodal_id)
    nodal_positions = nodal_data[:, 1:]
    element_id = element_data[:, 0]
    element_id_set = set(element_id)

    z0_nodes = nodal_id[nodal_positions[:, 2] < 1e-5]
    x0_nodes = nodal_id[nodal_positions[:, 0] < 1e-5]
    q = nodal_positions[:, 0] / nodal_positions[:, 1]
    x1_nodes = nodal_id[q > 0.999 * np.max(q)]

    with open(full_model_sets_file) as set_file:
        lines = set_file.readlines()
        for line in lines:
            if line.startswith('*Nset, nset=Exposed_Nodes'):
                read_exposed_nodes = True
                read_exposed_surface = False
            elif line.startswith('*Elset, elset=Exposed_Surface'):
                read_exposed_nodes = False
                read_exposed_surface = True
            elif line.startswith('*'):
                read_exposed_nodes = False
                read_exposed_surface = False
            elif read_exposed_nodes:
                nodes = line.split(',')
                for node in nodes:
                    if int(node) in nodal_id_set:
                        exposed_nodes.append(int(node))
            elif read_exposed_surface:
                elements = line.split(',')
                for element in elements:
                    if int(element) in element_id_set:
                        exposed_surface.append(int(element))

    x0_elements = []
    x1_elements = []
    for node_list, element_list in zip([x0_nodes, x1_nodes], [x0_elements, x1_elements]):
        for e in element_data:
            for node_label in e[1:]:
                if node_label in node_list:
                    element_list.append(e[0])

    node_sets = {'Monitor_Node': [73710, ],
                 'All_Nodes': sorted(list(nodal_id_set)),
                 'Exposed_Nodes': exposed_nodes,
                 'z0_nodes': z0_nodes,
                 'x0_nodes': x0_nodes,
                 'x1_nodes': x1_nodes}

    element_sets = {'All_elements': sorted(list(element_id_set)),
                    'GEARELEMS': sorted(list(element_id_set)),
                    'Exposed_surface': exposed_surface,
                    'x0_elements': sorted(x0_elements),
                    'x1_elements': sorted(x1_elements)}

    file_lines = write_sets(node_sets, element_sets)

    file_lines.append('*Surface, type = ELEMENT, name=Exposed_Surface, TRIM=YES')
    file_lines.append('\tExposed_Surface')

    file_lines.append('*Surface, type = ELEMENT, name=x0_Surface, TRIM=YES')
    file_lines.append('\tx0_elements')

    file_lines.append('*Surface, type = ELEMENT, name=x1_Surface, TRIM=YES')
    file_lines.append('\tx1_elements')

    with open(filename, 'w') as set_file:
        for line in file_lines:
            set_file.write(line + '\n')
        set_file.write('**EOF')


def write_geom_include_file(nodal_data, element_data, filename, simulation_type='Mechanical'):
    element_type = 'DC3D8'
    if simulation_type == 'Mechanical':
        element_type = 'C3D8'

    file_lines = ['*NODE']
    for node in nodal_data:
        file_lines.append('\t' + str(int(node[0])) + ', ' + str(node[1]) + ', ' + str(node[2]) + ', ' + str(node[3]))
    file_lines.append('*ELEMENT, TYPE=' + element_type)
    for element in element_data:
        element_string = [str(e) for e in element]
        element_string = ', '.join(element_string)
        file_lines.append('\t' + element_string)

    with open(filename, 'w') as inc_file:
        for line in file_lines:
            inc_file.write(line + '\n')
        inc_file.write('**EOF')


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

    quarter_nodes, quarter_elements = create_quarter_model('input_files/gear_models/planet_gear/dense_mesh.inc')

    write_sets_file(filename='input_files/dante_quarter/planetGear_sets.inc',
                    full_model_sets_file='input_files/gear_models/planet_gear/dense_mesh_sets.inc',
                    nodal_data=quarter_nodes,
                    element_data=quarter_elements)

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
