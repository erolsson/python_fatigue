from collections import namedtuple

from write_pulsator_model import GearTooth
from write_pulsator_model import write_include_files_for_tooth

from write_pulsator_model import write_tooth_part

if __name__ == '__main__':
    gear_model_dir = 'input_files/gear_models/'
    simulation_dir = 'input_files/planet_sun/'

    Gear = namedtuple('Gear', ['name', 'number_of_teeth', 'teeth_to_model', 'teeth_array'])

    gears = [Gear(name='planet', number_of_teeth=20, teeth_to_model=5, teeth_array=[]),
             Gear(name='sun', number_of_teeth=24, teeth_to_model=5, teeth_array=[])]

    for gear in gears:
        for i in range(gear.teeth_to_model):
            gear.teeth_array.append(GearTooth(instance_name=gear.name + '_tooth' + str(i),
                                              rotation=(i+0.5)*360/gear.number_of_teeth,
                                              part_names=[gear.name + '_coarse_tooth_pos',
                                                          gear.name + '_coarse_tooth_neg']))

    # Tooth number 1 is the interesting tooth for fatigue, give it a denser mesh and a different name
    gears[0].teeth_array[2].instance_name = 'eval_tooth'
    gears[0].teeth_array[2].part_names = ['coarse_tooth_pos', 'dense_tooth_neg']
    gears[0].teeth_array[1].part_names = ['dense_tooth_pos', 'dense_tooth_neg']
    gears[0].teeth_array[3].part_names = ['dense_tooth_pos', 'coarse_tooth_neg']

    for gear, mesh in zip(['sun', 'planet', 'planet'], ['coarse', 'coarse', 'dense']):
        mesh_dir = gear_model_dir + gear + '_gear/'
        write_include_files_for_tooth(full_model_file_name=mesh_dir + mesh + '_mesh_' + gear + '.inc',
                                      include_file_names=[simulation_dir + gear + '_' + mesh + '_geom_xpos.inc',
                                                          simulation_dir + gear + '_' + mesh + '_geom_xneg.inc'],
                                      full_set_file_name=mesh_dir + mesh + '_mesh_' + gear + '_sets.inc',
                                      set_include_file_name=simulation_dir + gear + '_' + mesh + '_geom_sets.inc')
    file_lines = ['*Heading',
                  '\tModel of a pulsator test of a planetary gear']
    for mesh in ['coarse', 'dense']:
        for sign in ['pos', 'neg']:
            file_lines += write_tooth_part(name=mesh + '_tooth_' + sign,
                                           inc_file=mesh + '_geom_x' + sign + '.inc',
                                           set_file=mesh + '_geom_sets.inc')
