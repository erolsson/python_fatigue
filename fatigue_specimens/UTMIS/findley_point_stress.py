import os
import pickle


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
    fig = 0
    for carb in [0.75, 0.8]:
        for temp in [180, 200]:
            plt.figure(fig)
            simulation_pickle = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/'
                                                   'utmis_smoothdante_path_tempering_2h_' + str(temp) + '_' +
                                                   str(carb).replace('.', '_') + 'C' + '.pkl')
            with open(simulation_pickle, 'r') as pickle_handle:
                dante_data = pickle.load(pickle_handle)

            s_res = dante_data['S'][0]
            label = 'Temp ' + str(temp) + 'C=' + str(carb)

            plt.plot([s_res, s_res+430*1.03], [760*1.03, 430*1.03], '-gx', ms=12)

            simulation_pickle = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data/'
                                                   'utmis_notcheddante_path_tempering_2h_' + str(temp) + '_' +
                                                   str(carb).replace('.', '_') + 'C' + '.pkl')
            with open(simulation_pickle, 'r') as pickle_handle:
                dante_data = pickle.load(pickle_handle)

            s_res = dante_data['S'][0]

            plt.plot([s_res, s_res+250*1.89], [440*1.89, 250*1.89], '-rx', ms=12)
            fig += 1

            plt.text(0, 400, label)

    plt.show()
