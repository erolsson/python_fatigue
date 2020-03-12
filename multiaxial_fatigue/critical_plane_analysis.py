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

k = 0.675
sF = 624

sm_max = sF/k
sm_min = -2000
sm = np.linspace(sm_min, sm_max)
sa = 2*(np.sqrt(sF**2 + k**2*sF**2 - k*sF*sm) - k*sF)
plt.plot(sm, sa, lw=2)
plt.plot([sm_min, 0], [-sm_min, 0], '--k')

plt.plot([-330, -170], [910, 790], 'bx', ms=16, mew=2)
plt.plot([0, 424], [760, 424], 'rx', ms=16, mew=2)
plt.show()
