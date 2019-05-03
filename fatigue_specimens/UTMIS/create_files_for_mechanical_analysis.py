import os
import sys

from input_file_reader.input_file_reader import InputFileReader

# specimen = sys.argv[-1]
specimen = 'smooth'
stress_level = '820'


def write_mechanical_input_file(geom_include_file, directory, load):
    input_file_reader = InputFileReader()
    input_file_reader.read_input_file(geom_include_file)
    input_file_reader.write_geom_include_file(directory + '/include_files/geom_pos.inc')
    input_file_reader.nodal_data[:, 2] *= -1
    load_nodes = input_file_reader.set_data['nset']['Specimen_load_nodes']
    load_pos = input_file_reader.nodal_data[load_nodes[0]-1, 1:3]
    for e_data in input_file_reader.elements.values():
        n = e_data.shape[1] - 1
        e_data[:, n/2+1:n+1], e_data[:, 1:n/2+1] = e_data[:, 1:n/2+1], e_data[:, n/2+1:n+1].copy()
    input_file_reader.write_geom_include_file(directory + '/include_files/geom_neg.inc')
    input_file_reader.write_sets_file(directory + '/include_files/set_data.inc',
                                      str_to_remove_from_setname='SPECIMEN_',
                                      surfaces_from_element_sets=[('YSYM_SURFACE', 'YSYM_ELEMENTS')])
    file_lines = ['*Heading',
                  '\tMechanical model for the fatigue specimen utmis_ ' + specimen]

    def write_part(part_sign):
        lines = ['*Part, name=' + 'specimen_part_' + part_sign,
                 '\t*Include, Input=include_files/geom_' + part_sign + '.inc',
                 '\t*Include, Input=include_files/set_data.inc',
                 '\t*Solid Section, elset=ALL_ELEMENTS, material=SS2506',
                 '\t\t1.0',
                 '*End Part']
        return lines

    file_lines += write_part('pos')
    file_lines += write_part('neg')

    file_lines.append('**')
    file_lines.append('*Material, name=SS2506')
    file_lines.append('\t*Elastic')
    file_lines.append('\t\t200E3, 0.3')

    file_lines.append('*Assembly, name=pulsator_model')
    for sign in ['pos', 'neg']:
        file_lines.append('\t*Instance, name=specimen_part_' + sign + ' , part=specimen_part_' + sign)
        file_lines.append('\t*End Instance')

    file_lines.append('\t*Tie, name=y_plane')
    file_lines.append('\t\tspecimen_part_pos.ysym_surface, specimen_part_neg.ysym_surface')

    file_lines.append('\t*Node, nset=load_node')
    file_lines.append('\t\t999999, ' + str(load_pos[0]) + ',' + str(2*load_pos[1]) + ', 0.0')

    file_lines.append('\t*Surface, name=load_surface, Type=Node')
    file_lines.append('\t\tspecimen_part_pos.load_nodes')
    file_lines.append('\t*Coupling, Constraint name=load_node_coupling, '
                      'ref node=jaw_ref_node, surface=load_surface')
    file_lines.append('\t\t*Kinematic')

    file_lines.append('*End Assembly')
    for sign in ['pos', 'neg']:
        file_lines.append('*Boundary')
        file_lines.append('\tspecimen_part_' + sign + '.x_sym_nodes,\tXSYMM')
        file_lines.append('\tspecimen_part_' + sign + '.z_sym_nodes,\tZSYMM')

    file_lines.append('*Boundary')
    file_lines.append('\tspecimen_part_neg.support_nodes,\t2')

    file_lines.append('*Boundary')
    file_lines.append('\tload_node,\t1')
    file_lines.append('\tload_node,\t3,6')

    with open(directory + '/utmis_' + specimen + '_' + load + '.inp', 'w') as input_file:
        for line in file_lines:
            input_file.write(line + '\n')


if __name__ == '__main__':
    dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/utmis_specimens/'
    simulation_directory = os.path.expanduser('~/scania_gear_analysis/abaqus/utmis_specimens/utmis_' + specimen)
    geom_filename = 'utmis_' + specimen + '/utmis_' + specimen + '.inc'
    times = [75, 5, 30]
    temps = [930, 840, 840]
    carbon_levels = [1.1, 0.8, 0.8]
    tempering = (200, 7200)
    name = ''

    if not os.path.isdir(simulation_directory):
        os.makedirs(simulation_directory)
    if not os.path.isdir(simulation_directory + '/include_files'):
        os.makedirs(simulation_directory + '/include_files')

    for t, T, c in zip(times, temps, carbon_levels):
        name += str(t) + 'min' + str(T) + 'C' + str(c).replace('.', '') + 'wtC'
    specimen_name = 'utmis_' + specimen
    heat_treatment_odb = os.path.expanduser('~/scania_gear_analysis/utmis_specimens_U925062/utmis_' + specimen
                                            + '_tempering_2h_' + str(tempering[0]) + '_cooldown_80C/'
                                            + specimen_name + '_' + name + '/Toolbox_Mechanical_utmis_'
                                            + specimen + '.odb')
    write_mechanical_input_file(geom_filename, simulation_directory, stress_level)
    # write_dante_files(heat_treatment_odb, simulation_directory)
