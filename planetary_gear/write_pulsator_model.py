from write_input_for_dante import create_quarter_model
from write_input_for_dante import write_geom_include_file
from write_input_for_dante import write_sets_file


def write_tooth_part(lines, name, inc_file, set_file):
    lines.append('*PART, NAME=' + name)
    lines.append('\t*Include, Input=' + inc_file)
    lines.append('\t*Include, Input=' + set_file)
    lines.append('*End Part')


def write_include_files_for_tooth(full_model_file_name, include_file_names, full_set_file_name, set_include_file_name):
    # Generating a quarter tooth for the right part
    quarter_nodes, quarter_elements = create_quarter_model(full_model_file_name)
    write_geom_include_file(quarter_nodes, quarter_elements,
                            filename=include_file_names[0])

    write_sets_file(filename=set_include_file_name,
                    full_model_sets_file=full_set_file_name,
                    nodal_data=quarter_nodes,
                    element_data=quarter_elements)

    # Generating a quarter tooth for the left part
    quarter_nodes[:, 1] *= -1

    # Swapping the nodes in the z-direction to get correct ordering of the nodes
    temp_connectivity = quarter_elements[:, 5:].copy()
    quarter_elements[:, 5:] = quarter_elements[:, 1:5]
    quarter_elements[:, 1:5] = temp_connectivity

    write_geom_include_file(quarter_nodes, quarter_elements,
                            filename=include_file_names[1])

if __name__ == '__main__':
    gear_model_dir = 'input_files/gear_models/planet_gear/'
    simulation_dir = 'input_files/pulsator_model/'

    for mesh in ['coarse', 'dense']:
        write_include_files_for_tooth(full_model_file_name=gear_model_dir + mesh + '_mesh.inc',
                                      include_file_names=[simulation_dir + mesh + '_geom_xpos.inc',
                                                          simulation_dir + mesh + '_geom_xneg.inc'],
                                      full_set_file_name=gear_model_dir + mesh + '_mesh_sets.inc',
                                      set_include_file_name=simulation_dir + mesh + '_geom_sets.inc')

    file_lines = ['*Heading',
                  '\tModel of a pulsator test of a planetary gear']
    for mesh in ['coarse', 'dense']:
        for sign in ['pos', 'neg']:
            write_tooth_part(file_lines, name=mesh + '_tooth_' + sign,
                             inc_file=mesh + '_geom_x' + sign + '.inc',
                             set_file=mesh + '_geom_sets.inc')

    file_lines.append('**')
    file_lines.append('*Assembly')

    with open('input_files/pulsator_model/pulsator_simulation.inp', 'w') as input_file:
        for line in file_lines:
            input_file.write(line + '\n')
