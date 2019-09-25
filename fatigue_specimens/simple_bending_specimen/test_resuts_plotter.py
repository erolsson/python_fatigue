import numpy as np

import matplotlib.pyplot as plt
import matplotlib.style

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

data = np.genfromtxt(r'D:\Aforsk2018\4pb.csv', delimiter=',', skip_header=1)

plt.semilogx(data[data[:, 2] < 2e6, 2],  data[data[:, 2] < 2e6, 1], 'x', ms=16, mew=2)
plt.semilogx(data[data[:, 2] >= 2e6, 2],  data[data[:, 2] >= 2e6, 1], 'o', ms=16, mew=2)
plt.ylim(350, 600)
plt.xlabel('Cycles')
plt.ylabel('Stress amplitude [MPa]')
plt.grid(True)
plt.tight_layout()
plt.savefig('bending_tests.png')
plt.show()
