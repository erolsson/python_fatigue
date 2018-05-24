import numpy as np

import matplotlib.pyplot as plt
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

diffusion_data = np.genfromtxt('diffusitivity.inc', delimiter=',')
d = diffusion_data[:, 0]
conc = diffusion_data[:, 1]
temp = diffusion_data[:, 2]

temp_levels = np.unique(temp)
x = np.arange(0.002, 0.015, 0.0005)
new_data = np.zeros((x.shape[0]*temp_levels.shape[0], 3))

for temp_idx, level in enumerate(temp_levels):
    plt.plot(conc[temp == level], d[temp == level], lw=2)
    coeff = np.polyfit(conc[temp == level], d[temp == level], 2)

    x = np.arange(0.002, 0.015, 0.0005)
    y = np.polyval(coeff, x)
    plt.plot(x, y, '--')

    new_data[temp_idx*x.shape[0]:(temp_idx+1)*x.shape[0], 0] = y
    new_data[temp_idx*x.shape[0]:(temp_idx+1)*x.shape[0], 1] = x
    new_data[temp_idx*x.shape[0]:(temp_idx+1)*x.shape[0], 2] = level

# Write the material include file
file_lines = ['** Include file defining material properties for carbon diffusion',
              '*Material, name=U92506',
              '\t*Density',
              '\t\t7.83e-6',
              '\t*Diffusivity']

for i in range(new_data.shape[0]):
    file_lines.append('\t\t' + str(new_data[i, 0]) + ',\t' + str(new_data[i, 1]) + ',\t' + str(new_data[i, 2]))

file_lines.append('\t*Solubility')
file_lines.append('\t\t1.')

with open('SS2506.inc', 'w') as material_file:
    for line in file_lines:
        material_file.write(line + '\n')
    material_file.write('**EOF')

plt.show()
