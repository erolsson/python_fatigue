from materials.gear_materials import SS2506

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

carbon_levels = np.array([0.002, 0.0036, 0.0052, 0.0065])

# Fitting the heat expansion
fig = plt.figure(0)
thermal_expansion = 0*carbon_levels
for i, carbon_level in enumerate(carbon_levels):
    data_point = np.genfromtxt('heat_expansion_' + str(carbon_level).replace('.', '_'), delimiter=',')
    thermal_expansion[i] = (data_point[1, 1] - data_point[0, 1])/(data_point[1, 0] - data_point[0, 0])

thermal_expansion = np.array([1.2678425108258802e-05,
                              9.683202737506953e-06,
                              4.559703619264866e-06,
                              1.92910537738129e-06])

plt.plot(carbon_levels, thermal_expansion, 's', ms=12, label='KTH Thesis')
par = np.polyfit(carbon_levels[0:3], thermal_expansion[0:3], 1)
carbon = np.linspace(0.002, 0.012, 1000, endpoint=True)
print par
plt.plot(0.008, 1.17e-5, 's', ms=12, label='JMAT PRO')
# plt.plot(carbon, SS2506.thermal_expansion.Martensite(20, carbon))


f = 1.3e-5 - 4.3e-6*carbon*100 + 2*2.9e-9*200 + 2*1.4e-9*carbon*100*200 + 3*1.091e-12*200**2
plt.plot(carbon, f, label=r'Dante 200 $^{\circ}$C')

f = 1.3e-5 - 4.3e-6*carbon*100 + 2*2.9e-9*20 + 2*1.4e-9*carbon*100*20 + 3*1.091e-12*20**2
plt.plot(carbon, f, label=r'Dante 20 $^{\circ}$C')

plt.plot(carbon, 1.3e-5*(1-carbon/0.01), label='Dante EO 1st')
# plt.plot(carbon, 1.5214e-5 - 1.2678e-5*carbon/0.01, label='Dante EO 2nd')

fig.set_size_inches(12., 6., forward=True)
ax = plt.subplot(111)
box = ax.get_position()
ax.set_position([0.15, 0.12, 0.57, box.height])
legend = ax.legend(numpoints=1, loc='upper left', bbox_to_anchor=(1., 1.035))
plt.gca().add_artist(legend)
plt.xlabel('Carbon')
plt.ylabel(r'Heat Expansion [$\mathrm{K}^{-1}$]')
plt.ylim(0, 0.000015)
plt.savefig(r'heat_expansion.png')

# Fitting parameter a in Koistinen-Marburger equation
plt.figure(1)
data = np.zeros((5, 2))
data[0:4, :] = np.genfromtxt('koistinen_marburger_a', delimiter=',')
data[4, 0] = 0.008
data[4, 1] = -np.log(0.01)/(176+91)   # Point from Erland
carbon_levels = data[:, 0]

plt.plot(data[:, 0], data[:, 1], 's', ms=12)
plt.plot(carbon, 4.8405e-2 - 4.3710*carbon)

# Trying an linear - exponential function
par = np.polyfit(carbon_levels, np.log(data[:, 1]), 1)
f = np.exp(par[1])*np.exp(par[0]*carbon)
print np.exp(par[1]), par[0]
plt.plot(carbon, f)

# Fitting ms-temperature
plt.figure(2)
data = np.zeros((9, 2))
data[0:8, :] = np.genfromtxt('ms_temperature', delimiter=',')
data[8, 0] = 0.008
data[8, 1] = 176+273.15
plt.plot(data[:, 0], data[:, 1] - 273.15, 's', ms=12)
plt.plot(carbon, SS2506.ms_temperature(carbon) - 273.15)
plt.plot([0.002, 0.0036, 0.0052, 0.0065, 0.008], [348.532, 317.2, 266.175, 215.2, 164.19], 'o', ms=12)

plt.show()
