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
plt.figure(0)
thermal_expansion = 0*carbon_levels
for i, carbon_level in enumerate(carbon_levels):
    data_point = np.genfromtxt('heat_expansion_' + str(carbon_level).replace('.', '_'), delimiter=',')
    thermal_expansion[i] = (data_point[1, 1] - data_point[0, 1])/(data_point[1, 0] - data_point[0, 0])

plt.plot(carbon_levels, thermal_expansion, 's', ms=12)
carbon = np.linspace(0.002, 0.012, 1000, endpoint=True)
plt.plot(carbon, SS2506.thermal_expansion.Martensite(20, carbon))


# Trying an linear - exponential function
c0 = 0.0065
a1 = 1.6369e-5
a2 = - 2.1344e-3
b1 = a1 + a2*c0
b2 = -a2/(a1 + a2*c0)
f = 0*carbon
f[carbon <= c0] = a1 + a2*carbon[carbon <= c0]
f[carbon > c0] = b1*np.exp(-b2*(carbon[carbon > c0] - c0))
plt.plot(carbon, f)

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
plt.plot(data[:, 0], data[:, 1], 's', ms=12)
plt.plot(carbon, SS2506.ms_temperature(carbon))

plt.show()
