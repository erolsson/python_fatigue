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


fatigue_limits = {'Smooth': {-1.: 760., 0.: 424.}, 'Notched': {-1.: 439, 0.: 237}}

test_data = np.genfromtxt('test_results_utmis.csv', delimiter=',', usecols=(0, 1, 2))
specimen_types = np.genfromtxt('test_results_utmis.csv', delimiter=',', usecols=(3,), dtype='S')
for specimen_type, color in zip(['Smooth', 'Notched'], ['r', 'b']):
    test_data_type = test_data[specimen_types == specimen_type, :]
    for ratio, symbol in zip([0., -1.], ['x', 's']):
        test_data_set = test_data_type[test_data_type[:, 2] == ratio]
        run_outs = test_data_set[test_data_set[:, 1] >= 2e6]
        failures = test_data_set[test_data_set[:, 1] < 2e6]
        plt.semilogx(run_outs[:, 1], run_outs[:, 0]/fatigue_limits[specimen_type][ratio],
                     color + 'o', ms=12, mew=2, mfc='w', mec=color)
        plt.semilogx(failures[:, 1], failures[:, 0]/fatigue_limits[specimen_type][ratio],
                     color + symbol, ms=12, mew=2, mfc='w', mec=color)

plt.show()
