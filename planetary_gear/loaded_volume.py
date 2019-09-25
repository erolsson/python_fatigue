import os
import pickle
import numpy as np

pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_1x/'
                                      + '/pulsator_stresses/')

with open(pickle_directory + 'pulsator_stresses_all_elements.pkl') as stress_pickle:
    stress_data = pickle.load(stress_pickle)

for force in sorted(stress_data['max_load'].keys()):
    s = stress_data['max_load'][force]

    p1 = s[:, 3]**2 + s[:, 4]**2 + s[:, 5]**2

    q = np.sum(s[:, 0:3], 1)/3
    p2 = (s[:, 0] - q)**2 + (s[:, 1] - q)**2 + (s[:, 2] - q)**2 + 2*p1
    p = np.sqrt(p2/6)
    B = np.copy(s)
    B[:, 0:3] -= np.outer(q, np.ones(3))

    r = (B[:, 0]*(B[:, 1]*B[:, 2] - B[:, 5]**2) - B[:, 3]*(B[:, 3]*B[:, 2] - B[:, 1]*B[:, 4])
         + B[:, 4]*(B[:, 3]*B[:, 5] - B[:, 1]*B[:, 4]))/2

    phi = np.arccos(r)/3
    phi[r <= -1] = np.pi/3
    phi[r >= 1] = 0.
    s1 = q + 2*p*np.cos(phi)
    print np.max(s1)
