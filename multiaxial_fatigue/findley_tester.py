from __future__ import print_function

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

from findley_evaluation_functions import evaluate_findley

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

k = [0.65, 0.65]

load_hist = np.zeros((2, 2, 6))
load_hist[0, 0, 0] = -333
load_hist[0, 0, 2] = -278
load_hist[1, 0, 0] = 533
load_hist[1, 0, 2] = -270

load_hist[0, 1, 0] = -383
load_hist[0, 1, 2] = -313
load_hist[1, 1, 0] = 500
load_hist[1, 1, 2] = -184

# print(load_hist)
print(evaluate_findley(combined_stress=load_hist, a_cp=np.array(k), worker_run_out_time=8000,
                       num_workers=8, chunk_size=300, search_grid=1))

idx = 2
q = np.linspace(0, np.pi/2, 1000)
tau = np.multiply.outer((load_hist[:, :, 0] - load_hist[:, :, idx])/2, np.sin(2*q))
sn = np.multiply.outer(load_hist[:, :, 0], np.cos(q)**2) + np.multiply.outer(load_hist[:, :, idx], np.sin(q)**2)
print(tau.shape)
sn_max = np.max(sn, axis=0)
tau_amp = np.abs(tau[1, :, :] - tau[0, :, :])/2
plt.figure(0)
plt.plot(q/np.pi*180, tau_amp[0, :], 'b', lw=2)
plt.plot(q/np.pi*180, tau_amp[1, :], '--b', lw=2)

plt.plot(q/np.pi*180, sn_max[0, :], 'r', lw=2)
plt.plot(q/np.pi*180, sn_max[1, :], '--r', lw=2)

plt.figure(1)
plt.plot(q/np.pi*180, tau[0, 0, :], 'b', lw=2)
plt.plot(q/np.pi*180, tau[1, 0, :], '--b', lw=2)

plt.plot(q/np.pi*180, tau[0, 1, :], 'r', lw=2)
plt.plot(q/np.pi*180, tau[1, 1, :], '--r', lw=2)

plt.figure(2)
plt.plot(q/np.pi*180, sn[0, 0, :], 'b', lw=2)
plt.plot(q/np.pi*180, sn[1, 0, :], '--b', lw=2)

plt.plot(q/np.pi*180, sn[0, 1, :], 'r', lw=2)
plt.plot(q/np.pi*180, sn[1, 1, :], '--r', lw=2)



plt.figure(3)
plt.plot(q/np.pi*180, (tau_amp[0, :] + 0.65*sn_max[0, :])*(sn_max[0, :] > 0), 'b', lw=2)
plt.plot(q/np.pi*180, (tau_amp[1, :] + 0.65*sn_max[1, :])*(sn_max[1, :] > 0), '--b', lw=2)
plt.show()
