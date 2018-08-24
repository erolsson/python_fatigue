from math import sin, pi, radians
import numpy as np
import matplotlib.pyplot as plt

plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}']
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
       'monospace': ['Computer Modern Typewriter']})


def profile(x, R, angle, height):
    y = 0*x + height[1]/2
    q = radians(angle)
    x1 = R * sin(pi / 2 - q)
    y1 = height[0] / 2 + R * (1 - np.cos(pi / 2 - q))
    d = height[1]/2 - y1
    x2 = x1 + d*np.tan(q)
    q1 = np.arcsin(x[x < x1]/R)
    y[x <= x2] = y1 + (x[x <= x2]-x1)/(x2 - x1)*d
    y[x <= x1] = height[0]/2 + R*(1-np.cos(q1))
    return y

t = 5.
R = 3.
h0 = 24.
h1 = 12
b1 = 45.
B2 = 6.5
P = 30E3
n = 1000
m = 1000
angle = 30
b2 = np.linspace(0, b1, n)

P1 = b2*P/(b1+b2)
P2 = b1*P/(b1+b2)
T = np.abs(P1-P2)
tau_mean = T/(t*h1)


X = np.outer(b2, np.linspace(0, 1, m))
M = -(np.outer(b2, np.ones(m)) - X)*np.outer(P2, np.ones(m)) + (b1 - X)*np.outer(P1, np.ones(m))
h = 2*profile(X, R, angle, [h1, h0])
Wb = t*h**2/6

s = M/Wb
sigma = np.max(s, 1)

X = np.linspace(0, B2, 1000)
P1 = B2*P/(b1+B2)
P2 = b1*P/(b1+B2)
M = -(B2 - X)*P2 + (b1 - X)*P1
plt.figure(2)
h = 2*profile(X, R, angle, [h1, h0])
Wb = t*h**2/6
plt.plot(X, M/Wb)


plt.figure(1)
plt.plot(b2, tau_mean, label=r'$\tau$')
plt.plot(b2, sigma, label=r'$\sigma$')
plt.xlabel('$b_2$ [mm]')
plt.ylabel('Stress [MPa]')
plt.legend(loc='best')
plt.show()
