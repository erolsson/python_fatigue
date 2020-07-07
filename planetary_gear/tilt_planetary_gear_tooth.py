from __future__ import print_function

import os
import numpy as np

from python_fatigue.input_file_reader.input_file_reader import InputFileReader

reader = InputFileReader()
reader.read_input_file(os.path.expanduser('~/python_projects/python_fatigue/planetary_gear/input_files/Job-1.inp'))

r = np.sqrt(reader.nodal_data[:, 1]**2 + reader.nodal_data[:, 2]**2)
z_max = np.max(reader.nodal_data[:, 3])
r_max = np.max(r)
rel_z = reader.nodal_data[:, 3]/z_max
rel_r = (r - 31)/(r_max - 31)

angle = rel_z*12*np.pi/180
reader.nodal_data[rel_r >= 0, 3] -= np.tan(angle[rel_r >= 0])*(r[rel_r >= 0]-31.)
reader.write_geom_include_file(os.path.expanduser('~/python_projects/python_fatigue/planetary_gear/input_files/'
                                                  'quarter_tooth_1x_tilt.inp'))
reader.write_sets_file(os.path.expanduser('~/python_projects/python_fatigue/planetary_gear/input_files/'
                                          'quarter_tooth_1x_set.inp'))
print(np.max(r), np.min(r))

