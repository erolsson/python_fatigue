import numpy as np

import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})

data = np.genfromtxt('SS2506_data/jmat_pro_0_8_carbon.csv', delimiter=',', skip_header=1)
temperature = data[:, 0]
strain = data[:, 11]/100
plt.plot(temperature, strain)
martensite = data[:, 2]/100
austenite = data[:, 1]/100
heat_exp_austenite = (strain[-1] - strain[-10])/(temperature[-1] - temperature[-10])
print heat_exp_austenite
strain_austenite = heat_exp_austenite*(temperature - temperature[-1])*austenite

strain_martensite = (strain - strain_austenite)/martensite
print (strain_martensite[20] - strain_martensite[0])/(temperature[20] - temperature[0])
print temperature

plt.plot(temperature, strain - strain_austenite)
plt.plot(temperature, (strain - strain_austenite)/martensite)
plt.plot(temperature, strain_austenite)

plt.show()
