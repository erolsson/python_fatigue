import numpy as np

from input_file_reader.input_file_functions import read_nodes_and_elements
from input_file_reader.input_file_functions import write_sets
from input_file_reader.input_file_functions import write_geom_include_file
from input_file_reader.input_file_functions import get_elements_from_nodes

from gear_input_file_functions import write_tooth_part
from gear_input_file_functions import write_include_files_for_tooth
from gear_input_file_functions import GearTooth


def write_load_step(step_name, force=None, initial_inc=0.01):
    lines = ['*step, name=' + step_name + ', nlgeom=Yes',
             '\t*Static',
             '\t\t' + str(initial_inc) + ', 1., 1e-12, 1.',
             '\t*CLoad',
             '\t\tjaw_ref_node, 1, -0.5']

    if force:
        lines.append('\t*CLoad')
        lines.append('\t\tjaw_ref_node, 2, ' + str(-force/2))
    lines.append('\t*Output, field')
    lines.append('\t\t*Element Output')
    lines.append('\t\t\tS')
    lines.append('\t\t*Node Output')
    lines.append('\t\t\tU')
    lines.append('*End step')
    return lines


def write_jaw_set_file(jaw_node_data, jaw_element_data, set_file_name):
    y = np.unique(jaw_node_data[:, 2])
    x_min = np.unique(jaw_node_data[:, 1])[0]
    y_min, y_max = y[0], y[-1]
    node_sets = {'x_min_nodes': jaw_node_data[jaw_node_data[:, 1] == x_min, 0],
                 'y_min_nodes': jaw_node_data[jaw_node_data[:, 2] == y_min, 0],
                 'y_max_nodes': jaw_node_data[jaw_node_data[:, 2] == y_max, 0],
                 'z0_nodes': jaw_node_data[jaw_node_data[:, 3] == 0.0, 0]}

    y_min_elements = []
    y_max_elements = []
    x_min_elements = []

    x_min_set = set(jaw_node_data[jaw_node_data[:, 1] == x_min, 0])
    y_min_set = set(jaw_node_data[jaw_node_data[:, 2] == y_min, 0])
    y_max_set = set(jaw_node_data[jaw_node_data[:, 2] == y_max, 0])

    for e in jaw_element_data:
        for n_label in e[1:]:
            for element_list, node_label_set in zip([x_min_elements, y_min_elements, y_max_elements],
                                                    [x_min_set, y_min_set, y_max_set]):
                if n_label in node_label_set:
                    element_list.append(e[0])

    element_sets = {'jaw_elements': np.unique(jaw_element_data[:, 0]),
                    'x_min_elements': np.unique(x_min_elements),
                    'y_min_elements': np.unique(y_min_elements),
                    'y_max_elements': np.unique(y_max_elements)}
    set_lines = write_sets(node_sets, element_sets)
    set_lines.append('*Surface, name=x_min_surface, trim=yes')
    set_lines.append('\tx_min_elements')
    set_lines.append('*Surface, name=y_min_surface, trim=yes')
    set_lines.append('\ty_min_elements')
    set_lines.append('*Surface, name=y_max_surface, trim=yes')
    set_lines.append('\ty_max_elements')
    with open(set_file_name, 'w') as set_file:
        for set_line in set_lines:
            set_file.write(set_line + '\n')


if __name__ == '__main__':
    geometry_file_name = os.path.expanduser('~/python_projects/python_fatigue/planetary_gear/input_files/'
                                            'quarter_tooth_tilt2.inp')
    simulation_dir = 'input_files/pulsator_model/'

    number_of_teeth = 10

    load_amplitudes = [30., 35., 40.]
    load_ratio = 0.1

    teeth = []
    for i in range(number_of_teeth):
        teeth.append(GearTooth(instance_name='tooth' + str(i),
                               rotation=(180/number_of_teeth)*i - 90. + (180/2/number_of_teeth),  # 9 degrees is a 1/2 tooth
                               part_names=['coarse_tooth_pos', 'coarse_tooth_neg']))

    # Tooth number 1 is the interesting tooth for fatigue, give it a denser mesh and a different name
    teeth[1].instance_name = 'eval_tooth'
    teeth[0].part_names = ['coarse_tooth_pos', 'dense_tooth_neg']
    teeth[1].part_names = ['dense_tooth_pos', 'dense_tooth_neg']
    teeth[2].part_names = ['dense_tooth_pos', 'coarse_tooth_neg']

    write_include_files_for_tooth(full_model_file_name=geometry_file_name,
                                  include_file_names=[simulation_dir + '_geom_xpos.inc',
                                                      simulation_dir + '_geom_xneg.inc'],
                                  full_set_file_name=gear_model_dir + mesh + '_mesh_planet_sets.inc',
                                  set_include_file_name=simulation_dir + mesh + '_geom_sets.inc')

    # Reading the pulsator jaw file
    jaw_nodes, jaw_elements = read_nodes_and_elements(gear_model_dir + '/pulsator_jaw.inp')
    # Adjusting so that the middle layer is at z=0
    z0 = np.min(np.abs(np.unique(jaw_nodes[:, 3])))
    jaw_nodes[:, 3] += z0
    jaw_nodes = jaw_nodes[jaw_nodes[:, 3] >= 0., :]

    # Swap x and y
    temp = jaw_nodes[:, 1].copy()
    jaw_nodes[:, 1] = jaw_nodes[:, 2]
    jaw_nodes[:, 2] = temp
    jaw_nodes[:, 2] *= -1

    jaw_elements = get_elements_from_nodes(jaw_nodes[:, 0], jaw_elements)
    write_geom_include_file(jaw_nodes, jaw_elements, filename=simulation_dir + 'pulsator_jaw_geom.inc')
    write_jaw_set_file(jaw_nodes, jaw_elements, simulation_dir + 'pulsator_jaw_sets.inc')

    file_lines = ['*Heading',
                  '\tModel of a pulsator test of a planetary gear']
    for mesh in ['coarse', 'dense']:
        for sign in ['pos', 'neg']:
            file_lines += write_tooth_part(name=mesh + '_tooth_' + sign,
                                           inc_file=mesh + '_geom_x' + sign + '.inc',
                                           set_file=mesh + '_geom_sets.inc')

    file_lines.append('*Part, name=pulsator_jaw_part')
    file_lines.append('\t*Include, input=pulsator_jaw_geom.inc')
    file_lines.append('\t*Include, input=pulsator_jaw_sets.inc')
    file_lines.append('\t*Solid Section, elset=jaw_elements, material=SS2506')
    file_lines.append('\t\t1.0')
    file_lines.append('*End Part')

    file_lines.append('**')
    file_lines.append('*Material, name=SS2506')
    file_lines.append('\t*Elastic')
    file_lines.append('\t\t200E3, 0.3')
    file_lines.append('*Assembly, name=pulsator_model')

    for tooth in teeth:
        file_lines += tooth.write_input()

    file_lines.append('\t*Instance, name=pulsator_jaw, part=pulsator_jaw_part')
    file_lines.append('\t*End Instance')

    # Writing the tie constraints at the mid lines of the teeth
    for i in range(number_of_teeth):
        file_lines.append('\t*Tie, name=tie_mid_tooth' + str(i))
        file_lines.append('\t\t' + teeth[i].instance_name +
                          '_0.x0_surface, ' + teeth[i].instance_name + '_1.x0_surface')

    # Writing tie constraints between the teeth
    for i in range(1, number_of_teeth):
        file_lines.append('\t*Tie, name=tie_inter_teeth_' + str(i-1) + '_' + str(i))
        file_lines.append('\t\t' + teeth[i-1].instance_name +
                          '_1.x1_surface, ' + teeth[i].instance_name + '_0.x1_surface')

    # Adding a kinematic coupling for the pulsator jaw
    file_lines.append('\t*Node, nset=jaw_ref_node')
    file_lines.append('\t\t999999, ' + str(np.min(jaw_nodes[:, 1])) + ',' + str(np.max(jaw_nodes[:, 2])) + ', 0.0')
    file_lines.append('\t*Nset, nset=pinned, instance=' + teeth[0].instance_name + '_0')
    file_lines.append('\t\t1241')
    file_lines.append('\t*Coupling, Constraint name=jaw_load_coupling, '
                      'ref node=jaw_ref_node, surface=Pulsator_jaw.y_max_surface')
    file_lines.append('\t\t*Kinematic')
    file_lines.append('*End Assembly')

    # Creating the contact between the pulsator jaw and the eval tooth in the vertical direction

    file_lines.append('*Surface interaction, name=frictionless_contact')
    file_lines.append('*Contact pair, interaction=frictionless_contact')
    file_lines.append('\teval_tooth_1.exposed_surface, Pulsator_jaw.y_min_surface')
    file_lines.append('*Contact pair, interaction=frictionless_contact')
    file_lines.append('\ttooth2_0.exposed_surface, Pulsator_jaw.x_min_surface')

    for tooth in teeth:
        file_lines.append('*Boundary')
        file_lines.append('\t' + tooth.instance_name + '_0.z0_nodes, 3, 3')
        file_lines.append('*Boundary')
        file_lines.append('\t' + tooth.instance_name + '_1.z0_nodes, 3, 3')

    file_lines.append('*Boundary')
    file_lines.append('\tpulsator_jaw.z0_nodes, 3, 3')

    file_lines.append('*Boundary')
    file_lines.append('\tpinned, 1, 1')

    file_lines.append('*Boundary')
    file_lines.append('\t' + teeth[0].instance_name + '_0.x1_nodes, 2, 2')
    file_lines.append('*Boundary')
    file_lines.append('\t' + teeth[-1].instance_name + '_1.x1_nodes, 2, 2')

    file_lines.append('*Boundary')
    file_lines.append('\tjaw_ref_node, 3, 6')

    initiate_contact_lines = write_load_step('Initiate_contact', initial_inc=1e-4, force=1.)
    initiate_contact_lines.insert(3, '\t*Controls, reset')
    initiate_contact_lines.insert(4, '\t*Controls, parameters=line search')
    initiate_contact_lines.insert(5, '\t\t5, , , , ')
    initiate_contact_lines.insert(6, '\t*Contact Controls, Stabilize')
    initiate_contact_lines.insert(7, '\t*Contact Interference, shrink')
    initiate_contact_lines.insert(8, '\t\teval_tooth_1.exposed_surface, Pulsator_jaw.y_min_surface')
    initiate_contact_lines.insert(9, '\t*Contact Interference, shrink')
    initiate_contact_lines.insert(10, '\t\ttooth2_0.exposed_surface, Pulsator_jaw.x_min_surface')

    file_lines += initiate_contact_lines

    for load_amp in load_amplitudes:
        mean_load = (1 + load_ratio)/(1-load_ratio)*load_amp
        file_lines += write_load_step('Pamp_' + str(load_amp).replace('.', '_') + 'kN_min',
                                      force=(mean_load-load_amp)*1000)

    for load_amp in load_amplitudes:
        mean_load = (1 + load_ratio)/(1-load_ratio)*load_amp
        file_lines += write_load_step('Pamp_' + str(load_amp).replace('.', '_') + 'kN_max',
                                      force=(mean_load+load_amp)*1000)

    with open('input_files/pulsator_model/pulsator_simulation.inp', 'w') as input_file:
        for line in file_lines:
            input_file.write(line + '\n')
