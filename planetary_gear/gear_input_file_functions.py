import numpy as np

from input_file_reader.input_file_functions import write_geom_include_file
from input_file_reader.input_file_functions import read_nodes_and_elements
from input_file_reader.input_file_functions import get_elements_from_nodes
from input_file_reader.input_file_functions import write_sets


class GearTooth:
    def __init__(self, instance_name, rotation, part_names, position=(0., 0., 0.)):
        self.instance_name = instance_name
        self.rotation = rotation
        self.part_names = part_names
        self.pos = position

    def write_input(self):
        lines = []
        for part_idx, part_name in enumerate(self.part_names):
            lines += ['\t*Instance, name=' + self.instance_name + '_' + str(part_idx) + ', part=' + part_name,
                      '\t\t' + str(self.pos[0]) + ', ' + str(self.pos[1]) + ', ' + str(self.pos[2]),
                      '\t\t' + str(self.pos[0]) + ', ' + str(self.pos[1]) + ', ' + str(self.pos[2]) + ', ' +
                      str(self.pos[0]) + ', ' + str(self.pos[1]) + ', ' + str(self.pos[2] + 1.0) + ', ' +
                      str(self.rotation),
                      '\t*End Instance']
        return lines


def write_tooth_part(name, inc_file, set_file):
    lines = ['*Part, name=' + name,
             '\t*Include, Input=' + inc_file,
             '\t*Include, Input=' + set_file,
             '\t*Solid Section, elset=GEARELEMS, material=SS2506',
             '\t\t1.0',
             '*End Part']
    return lines


def write_include_files_for_tooth(full_model_file_name, include_file_names, full_set_file_name, set_include_file_name):
    # Generating a quarter tooth for the right part
    quarter_nodes, quarter_elements = create_quarter_model(full_model_file_name)
    write_geom_include_file(quarter_nodes, quarter_elements,
                            filename=include_file_names[0])

    write_sets_file(filename=set_include_file_name,
                    full_model_sets_file=full_set_file_name,
                    nodal_data=quarter_nodes,
                    element_data=quarter_elements)

    quarter_nodes, quarter_elements = mirror_quarter_model(quarter_nodes, quarter_elements)

    write_geom_include_file(quarter_nodes, quarter_elements,
                            filename=include_file_names[1])


def write_load_step(step_name, torque_gear_name='sun', applied_torque=None, planet_velocity=0.0, initial_inc=0.01):
    lines = ['*step, name=' + step_name + ', nlgeom=Yes',
             '\t*Static',
             '\t\t' + str(initial_inc) + ', 1., 1e-12, 1.']

    if applied_torque:
        lines.append('\t*Cload')
        lines.append('\t\t' + torque_gear_name + '_ref_node, 6, ' + str(applied_torque*1000))
    lines.append('\t*Boundary, type=velocity')
    lines.append('\t\tplanet_ref_node, 6, 6,' + str(planet_velocity))
    lines.append('\t*Output, field')
    lines.append('\t\t*Element Output')
    lines.append('\t\t\tS')
    lines.append('\t\t*Node Output')
    lines.append('\t\t\tCF, RF, U')
    lines.append('*End step')
    return lines


def write_gear_assembly(gears, assembly_name):
    file_lines = ['*Assembly, name=' + assembly_name]

    for gear in gears.itervalues():
        for tooth in gear.teeth_array:
            file_lines += tooth.write_input()

    # Combining surfaces to master contact and slave surfaces
    # Sun gear master due to coarser mesh
    for gear_idx, (name, gear) in enumerate(gears.iteritems()):
        for i in range(gear.teeth_to_model):
            file_lines.append('\t*Tie, name=tie_' + name + '_mid_tooth' + str(i))
            file_lines.append('\t\t' + gear.teeth_array[i].instance_name +
                              '_0.x0_surface, ' + gear.teeth_array[i].instance_name + '_1.x0_surface')

        # Writing tie constraints between the teeth
        for i in range(1, gear.teeth_to_model):
            file_lines.append('\t*Tie, name=tie_' + name + '_inter_teeth_' + str(i - 1) + '_' + str(i))
            file_lines.append('\t\t' + gear.teeth_array[i - 1].instance_name +
                              '_1.x1_surface, ' + gear.teeth_array[i].instance_name + '_0.x1_surface')

        exposed_surface_names = [tooth.instance_name + '_' + str(i) + '.Exposed_Surface'
                                 for tooth in gear.teeth_array for i in [0, 1]]

        file_lines.append('\t*Surface, name=contact_Surface_' + name + ', combine=union')
        for surface_name in exposed_surface_names:
            file_lines.append('\t\t' + surface_name)

        file_lines.append('\t*Surface, name=bc_Surface_' + name + ', combine=union')
        file_lines.append('\t\t' + gear.teeth_array[0].instance_name + '_0.x1_Surface')
        file_lines.append('\t\t' + gear.teeth_array[-1].instance_name + '_1.x1_Surface')

        # Adding coupling nodes
        file_lines.append('\t*Node, nset=' + name + '_ref_node')
        file_lines.append('\t\t' + str(900000+gear_idx) + ', ' + str(gear.position[0]) + ', ' + str(gear.position[1]) +
                          ', ' + str(gear.position[2]))
        file_lines.append('\t*Coupling, Constraint name=' + name + '_load_coupling, ' +
                          'ref node=' + name + '_ref_node, surface=bc_Surface_' + name)
        file_lines.append('\t\t*Kinematic')

    file_lines.append('*End Assembly')
    return file_lines


def create_quarter_model(full_model_file):
    nodal_data, elements = read_nodes_and_elements(full_model_file)
    # Only using nodes on positive z and positive z
    nodal_data = nodal_data[nodal_data[:, 1] >= -1e-5, :]
    nodal_data = nodal_data[nodal_data[:, 3] >= -1e-5, :]

    quarter_model_elements = get_elements_from_nodes(nodal_data[:, 0], elements)

    return nodal_data, quarter_model_elements


def mirror_quarter_model(nodes, elements):
    # Generating a quarter tooth for the left part
    nodes[:, 1] *= -1

    # Swapping the nodes in the z-direction to get correct ordering of the nodes
    temp_connectivity = elements[:, 5:].copy()
    elements[:, 5:] = elements[:, 1:5]
    elements[:, 1:5] = temp_connectivity
    return nodes, elements


def write_sets_file(filename, full_model_sets_file, nodal_data, element_data, monitor_node=None):
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

    node_sets = {'All_Nodes': sorted(list(nodal_id_set)),
                 'Exposed_Nodes': exposed_nodes,
                 'z0_nodes': z0_nodes,
                 'x0_nodes': x0_nodes,
                 'x1_nodes': x1_nodes}

    if monitor_node:
        node_sets['Monitor_Node'] = [monitor_node, ]

    element_sets = {'All_elements': sorted(list(element_id_set)),
                    'GEARELEMS': sorted(list(element_id_set)),
                    'Exposed_surface': exposed_surface,
                    'x0_elements': np.unique(x0_elements),
                    'x1_elements': np.unique(x1_elements)}

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
