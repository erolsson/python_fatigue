import os
from collections import namedtuple

import numpy as np


def create_quarter_model():
    nodes = []
    elements = []
    with open('input_files/full_gear/planetGear.inc') as full_model_file:
        lines = full_model_file.readlines()
        reading_nodes = False
        reading_elements = False

        for line in lines:
            if 'Node' in line.split()[0]:
                reading_nodes = True
                reading_elements = False
            elif 'Element' in line.split()[0]:
                reading_elements = True
                reading_nodes = False
            elif '*' in line.split()[0]:
                reading_nodes = False
                reading_elements = False
            elif reading_nodes:
                nodes.append(line.split(","))
            elif reading_elements:
                elements.append(line.split(","))

    nodal_id = np.zeros(len(nodes), dtype=int)
    nodal_positions = np.zeros((len(nodes), 3))

    for i, node in enumerate(nodes):
        nodal_id[i] = node[0]
        nodal_positions[i, :] = node[1:]

    # Only using nodes on positive z and positive z
    nodal_id = nodal_id[nodal_positions[:, 0] >= 0]
    nodal_positions = nodal_positions[nodal_positions[:, 0] >= 0, :]

    nodal_id = nodal_id[nodal_positions[:, 2] >= 0]
    nodal_positions = nodal_positions[nodal_positions[:, 2] >= 0, :]

    nodal_id_set = set(nodal_id)
    element_id_set = set()
    # Find the elements corresponding to the model nodes

    model_elements = []
    for element in elements:
        include = True
        for node in element[1:]:
            if int(node) not in nodal_id_set:
                include = False
        if include:
            element_id_set.add(int(element[0]))
            model_elements.append([int(e) for e in element])

    exposed_surface = []
    exposed_nodes = []
    read_exposed_nodes = False
    read_exposed_surface = False

    z0_nodes = nodal_id[nodal_positions[:, 2] < 1e-5]
    x0_nodes = nodal_id[nodal_positions[:, 0] < 1e-5]
    q = nodal_positions[:, 0]/nodal_positions[:, 1]
    x1_nodes = nodal_id[q > 0.999*np.max(q)]

    with open('input_files/full_gear/planetGear_Sets.inc') as set_file:
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

    node_sets = {'Monitor_Node': [73710, ],
                 'All_Nodes': sorted(list(nodal_id_set)),
                 'Exposed_Nodes': exposed_nodes,
                 'z0_nodes': z0_nodes,
                 'x0_nodes': x0_nodes,
                 'x1_nodes': x1_nodes}

    element_sets = {'All_elements': sorted(list(element_id_set)),
                    'GEARELEMS': sorted(list(element_id_set)),
                    'Exposed_surface': exposed_surface}

    file_lines = ['** Include file for sets in a quarter model of a planetary gear for dante sim']

    def write_set_rows(data_to_write):
        data_line = ''
        counter = 0
        for item in data_to_write:
            data_line += str(item) + ', '
            counter += 1
            if counter == 16 or item is data_to_write[-1]:
                file_lines.append(data_line[:-2])
                counter = 0
                data_line = ''

    for key, data in element_sets.iteritems():
        file_lines.append('*Elset, elset=' + key)
        write_set_rows(data)

    for key, data in node_sets.iteritems():
        file_lines.append('*Nset, nset=' + key)
        write_set_rows(data)

    file_lines.append('*Surface, type = ELEMENT, name=Exposed_Surface, TRIM=YES')
    file_lines.append('\tExposed_Surface')

    with open('input_files/dante_quarter/planetGear_sets.inc', 'w') as set_file:
        for line in file_lines:
            set_file.write(line + '\n')
        set_file.write('**EOF')

    nodal_data = []
    for i, n in enumerate(nodal_id):
        nodal_data.append('\t' + str(n) + ', ' + str(nodal_positions[i, 0]) + ', ' + str(nodal_positions[i, 1]) +
                          ', ' + str(nodal_positions[i, 2]))
    element_data = []
    for element in model_elements:
        line = '\t'
        for label in element:
            line += str(label) + ', '
        element_data.append(line[:-2])
    return nodal_data, element_data


def write_model_files(sim_data, nodal_data, element_data):
    def write_geom_include_file(simulation_type):
        element_type = 'DC3D8'
        if simulation_type == 'Mechanical':
            element_type = 'C3D8'

        file_lines = ['*Heading',
                      '\tInclude file of a quarter of a planetary gear tooth',
                      '*NODE']
        for node in nodal_data:
            file_lines.append(node)
        file_lines.append('*ELEMENT, TYPE=' + element_type)
        for element in element_data:
            file_lines.append(element)

        with open('Toolbox_' + simulation_type + '_' + str(sim_data.CD).replace('.', '_') +
                  '_quarter_geo.inc', 'w') as inc_file:
            for line in file_lines:
                inc_file.write(line + '\n')
            inc_file.write('**EOF')

    def write_input_files():
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

        def write_generic_data(simulation_type):
            file_lines = []
            with open('../generic_' + simulation_type + '_file.txt') as generic_file:
                for line in generic_file:
                    line = line.replace('\n', '')
                    line = line.replace('ENTER_GEOM_INC_HERE',
                                        'Toolbox_' + simulation_type + '_' + str(sim_data.CD).replace('.', '_') +
                                        '_quarter_geo.inc')
                    file_lines.append(line)
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

        write_carburization_step('Heating', 0, 5400, 0.5)
        total_time = 5400.
        step_nr = 1
        for t, carb in zip(sim_data.times, sim_data.carbon):
            write_carburization_step('Carburization - ' + str(step_nr), total_time, total_time + t * 60, carb)
            step_nr += 1
            total_time += t * 60

        # Add remaining data to the thermal and mechanical file
        for lines, name in [(thermal_lines, 'Thermal'), (mechanical_lines, 'Mechanical')]:
            with open('../end_' + name + '_file.txt') as end_file:
                end_lines = end_file.readlines()
                for line in end_lines:
                    line = line.replace('/scratch/sssnks/VBC_Fatigue/VBC_v6/VBC_fatigue_0_5/', '')
                    line = line.replace('0_5_v6', str(sim_data.CD).replace('.', '_') + '_quarter')
                    line = line.replace('\n', '')
                    lines.append(line)

        for lines, name in [(carbon_lines, 'Carbon'), (thermal_lines, 'Thermal'), (mechanical_lines, 'Mechanical')]:
            with open('Toolbox_' + name + '_' + str(sim_data.CD).replace('.', '_') + '_quarter.inp', 'w') as inp_file:
                for line_to_write in lines:
                    inp_file.write(line_to_write + '\n')
                inp_file.write('**EOF')

    start_dir = os.getcwd()
    sim_directory = 'input_files/dante_quarter/VBC_fatigue_' + str(sim_data.CD).replace('.', '_')
    if not os.path.isdir(sim_directory):
        os.makedirs(sim_directory)

    # Entering the directory where files should be written
    os.chdir(sim_directory)
    write_geom_include_file('Carbon')
    write_geom_include_file('Thermal')
    write_geom_include_file('Mechanical')
    write_input_files()

    # Going back to main directory
    os.chdir(start_dir)

if __name__ == '__main__':
    quarter_nodes, quarter_elements = create_quarter_model()

    Simulation = namedtuple('Simulation', ['CD', 'times', 'temperatures', 'carbon'])
    simulations = [Simulation(CD=0.5, times=[75., 5., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8)),
                   Simulation(CD=0.8, times=[135., 30., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8)),
                   Simulation(CD=1.1, times=[370., 70., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8)),
                   Simulation(CD=1.4, times=[545., 130., 60.], temperatures=(930., 930., 840.), carbon=(1.1, 0.8, 0.8))]
    for sim in simulations:
        write_model_files(sim, quarter_nodes, quarter_elements)
