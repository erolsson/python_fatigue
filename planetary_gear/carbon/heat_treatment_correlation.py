import pickle
import matplotlib.pyplot as plt

case_depths = [0.5, 0.8, 1.1, 1.4]
color = ['r', 'b', 'g', 'k']

for case_depth, c in zip(case_depths, color):
    with open('../pickles/tooth_root_data/data' + str(case_depth).replace('.', '_') + '.pkl') as pickle_handle:
        flank_data = pickle.load(pickle_handle)
        root_data = pickle.load(pickle_handle)
    plt.figure(0)
    plt.plot(flank_data[:, 1], flank_data[:, 4], c, lw=2)
    plt.plot(root_data[:, 1], root_data[:, 4], '--' + c, lw=2)

    plt.figure(1)
    plt.plot(flank_data[:, 1], flank_data[:, 2], c, lw=2)
    plt.plot(root_data[:, 1], root_data[:, 2], '--' + c, lw=2)

plt.show()
