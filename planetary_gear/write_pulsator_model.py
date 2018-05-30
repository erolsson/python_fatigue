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


class PlanetaryGearTooth:
    def __init__(self, instance_name, rotation, part_names):
        self.instance_name = instance_name
        self.rotation = rotation
        self.part_names = part_names

    def write_input(self):
        lines = []
        for part_idx, part_name in enumerate(self.part_names):
            lines += ['\t*Instance, name=' + self.instance_name + '_' + str(part_idx) + ', part=' + part_name,
                      '\t\t0.0, 0.0, 0.0',
                      '\t\t0.0, 0.0, 0.0, 0.0, 0.0, 1.0,' + str(self.rotation),
                      '\t*End Instance']
        return lines

if __name__ == '__main__':
    gear_model_dir = 'input_files/gear_models/planet_gear/'
    simulation_dir = 'input_files/pulsator_model/'

    number_of_teeth = 10

    teeth = []
    for i in range(number_of_teeth):
        teeth.append(PlanetaryGearTooth(instance_name='tooth' + str(i),
                                        rotation=18*i - 90. + 9,  # 9 degrees is a 1/2 tooth
                                        part_names=['coarse_tooth_pos', 'coarse_tooth_neg']))

    # Tooth number 1 is the interesting tooth for fatigue, give it a denser mesh and a different name
    teeth[1].instance_name = 'eval_tooth'
    teeth[1].part_names = ['dense_tooth_pos', 'dense_tooth_neg']
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
    file_lines.append('*Assembly, name=pulsator_model')

    for tooth in teeth:
        file_lines += tooth.write_input()

    # Writing the tie constraints at the mid lines of the teeth
    for i in range(number_of_teeth):
        file_lines.append('\t*Tie, name=tie_mid_tooth' + str(i))
        file_lines.append('\t\t' + teeth[i].instance_name +
                          '_0.x0_surface, ' + teeth[i].instance_name + '_1.x0_surface')

    file_lines.append('*End Assembly')
    with open('input_files/pulsator_model/pulsator_simulation.inp', 'w') as input_file:
        for line in file_lines:
            input_file.write(line + '\n')
