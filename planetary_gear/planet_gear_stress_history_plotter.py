import numpy as np
import pickle
import matplotlib.pyplot as plt

plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


for i, name in enumerate(['pos', 'neg']):
    plt.figure(i)
    stress_pickle_name = 'pickles/tooth_root_stresses/stresses_' + name + '_tooth_400_Nm.pkl'
    with open(stress_pickle_name) as stress_pickle:
        stress_data = pickle.load(stress_pickle)
    stress_data[:, 0] -= stress_data[0, 0]
    idx = np.argwhere(stress_data[:, 0] == 0)[1][0]
    print stress_data
    plt.plot(stress_data[idx:, 0], stress_data[idx:, 1], lw=2)
    plt.plot(stress_data[:idx, 0], stress_data[:idx, 1], lw=2)

plt.show()
