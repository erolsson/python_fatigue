import numpy as np

import matplotlib
import matplotlib.pyplot as plt

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}", r"\usepackage{gensymb}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

oil_data = []

with open('data_files/interaction_properties.inc') as interaction_prop_file:
    reading_oil_data = False
    for line in interaction_prop_file.readlines():
        if reading_oil_data:
            oil_data.append(line.strip().split(','))
        if line.rstrip() == '*FILM PROPERTY, NAME=QUENCHWAY125B_Used_0mps':
            reading_oil_data = True
        elif line.startswith('*'):
            reading_oil_data = False

oil_data = [[float(word.strip()) for word in line] for line in oil_data]
oil_data = np.array(oil_data)

plt.plot(oil_data[:, 1], oil_data[:, 0], 'k', lw=2)
plt.xlabel(r'Temperature [ $\degree$C]')
plt.ylabel(r'Heat Transfer Coefficient [W/$\mathrm{mm}^2$]')
plt.tight_layout()
plt.savefig('QenchwayB.png')
plt.show()
