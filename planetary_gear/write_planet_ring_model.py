import sys

from collections import namedtuple
from math import pi

from write_pulsator_model import GearTooth


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
