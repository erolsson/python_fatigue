from collections import namedtuple
from math import pi

from write_pulsator_model import GearTooth
from write_pulsator_model import write_include_files_for_tooth

from write_pulsator_model import write_tooth_part


def write_load_step(step_name, planet_torque=None, initial_inc=0.01):
    lines = ['*step, name=' + step_name + ', nlgeom=Yes',
             '\t*Static',
             '\t\t' + str(initial_inc) + ', 1., 1e-12, 1.']

    if planet_torque:
        lines.append('\t*Cload')
        lines.append('\t\tplanet_ref_node, 6, ' + str(-planet_torque*1000))
    lines.append('\t*Boundary, type=velocity, amplitude=sun_rotation')
    lines.append('\t\tsun_ref_node, 6, 6,' + str(-1./24.*2.*pi))
    lines.append('\t*Output, field')
    lines.append('\t\t*Element Output')
    lines.append('\t\t\tS')
    lines.append('\t\t*Node Output')
    lines.append('\t\t\tCF, RF, U')
    lines.append('*End step')
    return lines


if __name__ == '__main__':
    gear_model_dir = 'input_files/gear_models/'
    simulation_dir = 'input_files/planet_sun/'

    torque = 1500.

    Gear = namedtuple('Gear', ['number_of_teeth', 'teeth_to_model', 'teeth_array', 'position', 'rotation'])
    gears = {'planet': Gear(number_of_teeth=20, teeth_to_model=5, teeth_array=[], position=(0., 83.5, 0.),
                            rotation=188 - 5*360/20),
             'sun': Gear(number_of_teeth=24, teeth_to_model=5, teeth_array=[], position=(0., 0., 0.), rotation=0)}

    for name, gear in gears.iteritems():
        for i in range(gear.teeth_to_model):
            gear.teeth_array.append(GearTooth(instance_name=name + '_tooth' + str(i),
                                              rotation=(i+0.5)*360/gear.number_of_teeth + gear.rotation,
                                              part_names=[name + '_coarse_tooth_pos',
                                                          name + '_coarse_tooth_neg'],
                                              position=gear.position))

    # Tooth number 1 is the interesting tooth for fatigue, give it a denser mesh and a different name
    planet = gears['planet']
    planet.teeth_array[2].instance_name = 'eval_tooth'
    planet.teeth_array[1].part_names = ['planet_coarse_tooth_pos', 'planet_dense_tooth_neg']
    planet.teeth_array[2].part_names = ['planet_dense_tooth_pos', 'planet_dense_tooth_neg']
    planet.teeth_array[3].part_names = ['planet_dense_tooth_pos', 'planet_coarse_tooth_neg']

    for gear, mesh in zip(['sun', 'planet', 'planet'], ['coarse', 'coarse', 'dense']):
        mesh_dir = gear_model_dir + gear + '_gear/'
        write_include_files_for_tooth(full_model_file_name=mesh_dir + mesh + '_mesh_' + gear + '.inc',
                                      include_file_names=[simulation_dir + gear + '_' + mesh + '_geom_xpos.inc',
                                                          simulation_dir + gear + '_' + mesh + '_geom_xneg.inc'],
                                      full_set_file_name=mesh_dir + mesh + '_mesh_' + gear + '_sets.inc',
                                      set_include_file_name=simulation_dir + gear + '_' + mesh + '_geom_sets.inc')
    file_lines = ['*Heading',
                  '\tModel of a pulsator test of a planetary gear']
    for gear, mesh in zip(['sun', 'planet', 'planet'], ['coarse', 'coarse', 'dense']):
        for sign in ['pos', 'neg']:
            file_lines += write_tooth_part(name=gear + '_' + mesh + '_tooth_' + sign,
                                           inc_file=gear + '_' + mesh + '_geom_x' + sign + '.inc',
                                           set_file=gear + '_' + mesh + '_geom_sets.inc')

    file_lines.append('**')
    file_lines.append('*Material, name=SS2506')
    file_lines.append('\t*Elastic')
    file_lines.append('\t\t200E3, 0.3')
    file_lines.append('*Assembly, name=planet_sun_model')

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

    file_lines.append('*Surface interaction, name=frictionless_contact')
    #file_lines.append('*Contact pair, interaction=frictionless_contact')
    #file_lines.append('\tcontact_Surface_planet, contact_Surface_sun')

    # Lock everything except rotation around z-axis
    file_lines.append('*Boundary')
    file_lines.append('\tsun_ref_node, 1, 5')

    file_lines.append('*Boundary')
    file_lines.append('\tplanet_ref_node, 1, 5')

    file_lines.append('*Amplitude, name=sun_rotation')
    file_lines.append('\t0.0, 0.0')
    file_lines.append('\t1.0, 0.0')
    file_lines.append('\t2.0, 0.0')
    file_lines.append('\t3.0, 1.0')
    file_lines.append('\t4.0, 1.0')
    file_lines.append('\t5.0, 1.0')
    file_lines.append('\t6.0, 1.0')

    file_lines += write_load_step('Initiate_contact')
    file_lines += write_load_step('Apply_load', planet_torque=torque)
    for i in range(4):
        file_lines += write_load_step('loading_tooth_' + str(i+1), planet_torque=torque)

    with open(simulation_dir + 'planet_sun_' + str(int(torque)) + '_Nm.inp', 'w') as input_file:
        for line in file_lines:
            input_file.write(line + '\n')
