from collections import namedtuple

from write_pulsator_model import GearTooth

if __name__ == '__main__':
    gear_model_dir = 'input_files/gear_models/planet_gear/'
    simulation_dir = 'input_files/pulsator_model/'

    Gear = namedtuple('Gear', ['name', 'number_of_teeth', 'teeth_to_model', 'teeth_array'])

    gears = [Gear(name='planet', number_of_teeth=5, teeth_array=[]),
             Gear(name='sun', number_of_teeth=5, teeth_array=[])]



    planet_teeth = []
    sun_teeth = []
    for i in range(number_of_teeth_planet):
        planet_teeth.append(GearTooth(instance_name='planet_tooth' + str(i),
                            rotation=18*i - 0.+9,  # 9 degrees is a 1/2 tooth
                            part_names=['planet_coarse_tooth_pos', 'planaet_coarse_tooth_neg']))

    for i in range(number_of_teeth_sun):
        sun_teeth.append(GearTooth(instance_name='Sun_tooth' + str(i),
                            rotation=18*i - 0.+9,  # 9 degrees is a 1/2 tooth
                            part_names=['sun_coarse_tooth_pos', 'sun_coarse_tooth_neg']))


    # Tooth number 1 is the interesting tooth for fatigue, give it a denser mesh and a different name
    teeth[1].instance_name = 'eval_tooth'
    teeth[0].part_names = ['coarse_tooth_pos', 'dense_tooth_neg']
    teeth[1].part_names = ['dense_tooth_pos', 'dense_tooth_neg']
    teeth[2].part_names = ['dense_tooth_pos', 'coarse_tooth_neg']
