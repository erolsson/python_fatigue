import os
import sys

import pickle
import numpy as np

from materials.gear_materials import SS2506
from materials.gear_materials import SteelData

from multiaxial_fatigue.findley_evaluation_functions import evaluate_findley

mesh = '1x'
cd = float(sys.argv[1])

# residual_stress_multiplier = 0.572     # This should be removed later
residual_stress_multiplier = 1.     # This should be removed later
dante_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_' +
                                            mesh + '/dante/')