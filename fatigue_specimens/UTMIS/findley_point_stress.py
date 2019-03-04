import os
import pickle

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

if __name__ == '__main__':
    sm = np.linspace(-400, 200, 1000)
    fig = 0
    for carb, temp in [(0.75, 180), (0.8, 180), (0.8, 200)]:
        plt.figure(fig)
        simulation_pickle = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/'
                                               'oil60/utmis_smoothdante_path_tempering_2h_' + str(temp) + '_' +
                                               str(carb).replace('.', '_') + 'C' + '.pkl')
        with open(simulation_pickle, 'r') as pickle_handle:
            dante_data = pickle.load(pickle_handle)

        s_res_smooth = dante_data['S'][0]*0
        label = 'Temp ' + str(temp) + 'C=' + str(carb)

        plt.plot([s_res_smooth, s_res_smooth+430*1.03], [760*1.03, 430*1.03], '-gx', ms=12)

        simulation_pickle = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/'
                                               'oil60/utmis_notcheddante_path_tempering_2h_' + str(temp) + '_' +
                                               str(carb).replace('.', '_') + 'C' + '.pkl')
        with open(simulation_pickle, 'r') as pickle_handle:
            dante_data = pickle.load(pickle_handle)

        s_res_notched = dante_data['S'][0]*0

        plt.plot([s_res_notched, s_res_notched+250*1.89], [440*1.89, 250*1.89], '-rx', ms=12)
        fig += 1
        print s_res_smooth, s_res_notched

        k = 1.3
        sF = 580 * (k + np.sqrt(1 + k ** 2)) / 2
        print sF
        sa = 2 * (-k * sF + np.sqrt(sF ** 2 + k ** 2 * sF ** 2 - k * sF * sm))
        plt.plot(sm, sa)

        k = 1.3
        sF = 560 * (k + np.sqrt(1 + k ** 2)) / 2
        print sF
        sa = 2 * (-k * sF + np.sqrt(sF ** 2 + k ** 2 * sF ** 2 - k * sF * sm))
        plt.plot(sm, sa)

        plt.text(0, 400, label)

    plt.show()
