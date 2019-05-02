import os
import sys

from abaqus_files.odb_io_functions import read_field_from_odb

from abaqusConstants import INTEGRATION_POINT

specimen = sys.argv[-1]

dante_odb_path = '/scratch/users/erik/scania_gear_analysis/odb_files/heat_treatment/utmis_specimens/'

times = [75, 5, 30]
temps = [930, 840, 840]
carbon_levels = [1.1, 0.8, 0.8]
tempering = (200, 7200)
name = ''

for t, T, c in zip(times, temps, carbon_levels):
    name += str(t) + 'min' + str(T) + 'C' + str(c).replace('.', '') + 'wtC'
specimen_name = 'utmis_' + specimen
simulation_odb = os.path.expanduser('~/scania_gear_analysis/utmis_specimens_U925062/utmis_' + specimen
                                    + '_tempering_2h_' + str(tempering[0]) + '_cooldown_80C/'
                                    + specimen_name + '_' + name + '/Toolbox_Mechanical_utmis_'
                                    + specimen + '.odb')

stress, _, labels = read_field_from_odb('S', simulation_odb, step_name='Tempering', frame_number=-1,
                                        position=INTEGRATION_POINT, get_position_numbers=True)
print stress
