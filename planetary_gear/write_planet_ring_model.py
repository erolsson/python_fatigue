import sys
from collections import namedtuple
from math import pi

from gear_input_file_functions import GearTooth
from gear_input_file_functions import write_include_files_for_tooth
from gear_input_file_functions import write_tooth_part
from gear_input_file_functions import write_gear_assembly
from gear_input_file_functions import write_load_step


if __name__ == '__main__':
    gear_model_dir = 'input_files/gear_models/'
    simulation_dir = 'input_files/planet_ring/'

    torque = float(sys.argv[1])

    Gear = namedtuple('Gear', ['number_of_teeth', 'teeth_to_model', 'teeth_array', 'position', 'rotation'])
    gears = {'planet': Gear(number_of_teeth=20, teeth_to_model=5, teeth_array=[], position=(0., 83.5, 0.),
                            rotation=188 - 5*360/20),
             'ring': Gear(number_of_teeth=66, teeth_to_model=5, teeth_array=[], position=(0., 0., 0.), rotation=0)}

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

    for gear, mesh in zip(['ring', 'planet', 'planet'], ['coarse', 'coarse', 'dense']):
        mesh_dir = gear_model_dir + gear + '_gear/'
        write_include_files_for_tooth(full_model_file_name=mesh_dir + mesh + '_mesh_' + gear + '.inc',
                                      include_file_names=[simulation_dir + gear + '_' + mesh + '_geom_xpos.inc',
                                                          simulation_dir + gear + '_' + mesh + '_geom_xneg.inc'],
                                      full_set_file_name=mesh_dir + mesh + '_mesh_' + gear + '_sets.inc',
                                      set_include_file_name=simulation_dir + gear + '_' + mesh + '_geom_sets.inc')
    file_lines = ['*Heading',
                  '\tModel of a meshing between a sun gear and a planetary gear']
    for gear, mesh in zip(['ring', 'planet', 'planet'], ['coarse', 'coarse', 'dense']):
        for sign in ['pos', 'neg']:
            file_lines += write_tooth_part(name=gear + '_' + mesh + '_tooth_' + sign,
                                           inc_file=gear + '_' + mesh + '_geom_x' + sign + '.inc',
                                           set_file=gear + '_' + mesh + '_geom_sets.inc')

    file_lines.append('**')
    file_lines.append('*Material, name=SS2506')
    file_lines.append('\t*Elastic')
    file_lines.append('\t\t200E3, 0.3')

    file_lines += write_gear_assembly(gears, assembly_name='planet_sun_assembly')

    file_lines.append('*Surface interaction, name=frictionless_contact')
    file_lines.append('*Contact pair, interaction=frictionless_contact, type=surface to surface')
    file_lines.append('\tcontact_Surface_planet, contact_Surface_ring')

    # Lock everything except rotation around z-axis
    file_lines.append('*Boundary')
    file_lines.append('\tsun_ref_node, 1, 5')

    file_lines.append('*Boundary')
    file_lines.append('\tplanet_ref_node, 1, 5')

    # Adding the z-symmetry BC
    for gear in gears.itervalues():
        for tooth in gear.teeth_array:
            file_lines.append('*Boundary')
            file_lines.append('\t' + tooth.instance_name + '_0.z0_nodes, 3, 3')
            file_lines.append('*Boundary')
            file_lines.append('\t' + tooth.instance_name + '_1.z0_nodes, 3, 3')

    file_lines.append('*Amplitude, name=sun_rotation, time=total time')
    file_lines.append('\t0.0, 0.0')
    file_lines.append('\t1.0, 0.0')
    file_lines.append('\t2.0, 0.0')
    file_lines.append('\t3.0, 1.0')
    file_lines.append('\t4.0, 2.0')
    file_lines.append('\t5.0, 3.0')
    file_lines.append('\t6.0, 4.0')

    initiate_contact_lines = write_load_step('Initiate_contact')
    initiate_contact_lines.insert(3, '\t*Controls, reset')
    initiate_contact_lines.insert(4, '\t*Controls, parameters=line search')
    initiate_contact_lines.insert(5, '\t\t5, , , , ')
    initiate_contact_lines.insert(6, '\t*Contact Controls, Stabilize')
    initiate_contact_lines.insert(7, '\t*Contact Interference, shrink')
    initiate_contact_lines.insert(8, '\t\tcontact_Surface_planet, contact_Surface_ring')
    file_lines += initiate_contact_lines
    torque_ratio = float(gears['ring'].number_of_teeth) / gears['planet'].number_of_teeth
    file_lines += write_load_step('Apply_load', applied_torque=torque*torque_ratio)

    for i in range(4):
        file_lines += write_load_step('loading_tooth_' + str(i+1), applied_torque=torque*torque_ratio,
                                      planet_velocity=1./20*2*pi)

    with open(simulation_dir + 'planet_ring_' + str(int(torque)) + '_Nm.inp', 'w') as input_file:
        for line in file_lines:
            input_file.write(line + '\n')
