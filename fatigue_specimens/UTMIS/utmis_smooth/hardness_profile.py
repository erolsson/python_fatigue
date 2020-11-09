import os
import pickle

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

from python_fatigue.materials.hardess_convertion_functions import HRC2HV, HV2HRC

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

experimental_data = np.genfromtxt('hardness_profile', delimiter=',')
r_exp = experimental_data[:, 0]
hv_exp = experimental_data[:, 1]
plt.plot(r_exp, hv_exp, 'b', lw=2)

simulation_pickle = os.path.expanduser('~/utmis_specimens/smooth/heat_treatment_data/utmis_smooth_dante_path_y.pkl')
with open(simulation_pickle, 'rb') as pickle_handle:
    dante_data = pickle.load(pickle_handle, encoding='latin1')

r = r_exp
hv = np.interp(r_exp, dante_data['r'][:-1], HRC2HV(dante_data['SDV_HARDNESS'][:-1]).flatten())
c = np.interp(r_exp, dante_data['r'][:-1], dante_data['SDV_CARBON'][:-1].flatten())
a = np.interp(r_exp, dante_data['r'][:-1], dante_data['SDV_AUSTENITE'][:-1].flatten())
m = np.interp(r_exp, dante_data['r'][:-1], dante_data['SDV_T_MARTENSITE'][:-1].flatten())
plt.plot(r, hv, '--', lw=2)

plt.figure(2)
plt.plot(r, c, '--', lw=2)

plt.figure(3)
plt.plot(r, a, '--', lw=2)

r = r[c > 0.006]
hv = hv[c > 0.006]
hv_exp = hv_exp[c > 0.006]
a = a[c > 0.006]
m = m[c > 0.006]
c = c[c > 0.006]


hv_a = np.interp(c, [0.006, 0.008, 0.01], HRC2HV(np.array([29, 32, 35])))
hv_m = np.interp(c, [0.006, 0.008, 0.01], HRC2HV(np.array([59, 69, 72])))
hv1 = a*hv_a + m*hv_m
hv2 = (a/hv_a + m/hv_m)**-1
print(a+m)

plt.figure(100)
print(HV2HRC(818))
print(HV2HRC(272))
hrc_a = np.interp(c, [0.006, 0.008, 0.01], np.array([29, 32, 35]))
hrc_m = np.interp(c, [0.006, 0.008, 0.01], np.array([57, 68, 72]))
print(hv_a, hv_m)
print(m, a)
hrc1 = a*hrc_a + m*hrc_m
hrc2 = (a/hrc_a + m/hrc_m)**-1

plt.plot(r, HRC2HV(hrc1), '--')
plt.plot(r, hv_exp, lw=2)
plt.plot(r, hv, '--', lw=2)

plt.show()
