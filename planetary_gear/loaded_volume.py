import os
import pickle

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from weakest_link.integration_methods import gauss_integration_3d

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/tooth_root_fatigue_analysis/mesh_1x/'
                                      + '/pulsator_stresses/')

with open(pickle_directory + 'pulsator_stresses_all_elements.pkl') as stress_pickle:
    stress_data = pickle.load(stress_pickle)

load_levels = np.array(sorted(stress_data['max_load'].keys()))
max_stress = 0*load_levels
for j, force in enumerate(load_levels):
    s = stress_data['max_load'][force]*(1 - 1/(1 + (1-0.1)/(1+0.1)))

    p1 = s[:, 3]**2 + s[:, 4]**2 + s[:, 5]**2

    q = np.sum(s[:, 0:3], 1)/3
    p2 = (s[:, 0] - q)**2 + (s[:, 1] - q)**2 + (s[:, 2] - q)**2 + 2*p1
    p = np.sqrt(p2/6)
    B = np.copy(s)
    B[:, 0:3] -= np.outer(q, np.ones(3))
    B /= np.outer(p, np.ones(6))
    r = (B[:, 0]*(B[:, 1]*B[:, 2] - B[:, 5]**2) - B[:, 3]*(B[:, 3]*B[:, 2] - B[:, 5]*B[:, 4])
         + B[:, 4]*(B[:, 3]*B[:, 5] - B[:, 1]*B[:, 4]))/2

    phi = np.arccos(r)/3
    phi[r <= -1] = np.pi/3
    phi[r >= 1] = 0.
    s1 = q + 2*p*np.cos(phi)
    max_stress[j] = np.max(s1)
    stress_levels = np.linspace(0, np.max(s1, 0), 100)
    n = len(s1)
    positions = stress_data['pos']
    positions = positions.reshape(n/8, 8, 3)
    v = 0*stress_levels
    for i, s_th in enumerate(stress_levels):
        s = 0*s1
        s[s1 > s_th] = 1.
        v[i] = gauss_integration_3d(s.reshape(n/8, 8), positions)

    plt.figure(0)
    plt.plot(stress_levels/stress_levels[-1]*100, v*4, label='$P_{amp}$ = ' + str(int(force)) + ' kN', lw=2)


plt.grid(True)
plt.xlabel('Percent of maximum stress')
plt.ylabel(r'Loaded Volume [$\textrm{mm}^3$]')
plt.legend(loc='best')
plt.tight_layout()
plt.savefig('loaded_volume.png')
plt.xlim(80, 100)
plt.ylim(0, 15)
plt.legend(loc='best')
plt.tight_layout()
plt.savefig('loaded_volume_zoom.png')

plt.figure(1)
plt.plot(load_levels, max_stress, '-kx', lw=2, ms=12, mew=2)
plt.xlabel('Force amplitude, $P_{amp}$ [kN]')
plt.ylabel('Maximum stress amplitude [MPa]')
plt.grid(True)
plt.tight_layout()
plt.savefig('force-stress.png')

plt.show()
