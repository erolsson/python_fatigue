import cPickle as pickle


def get_point_stress_from_pickle(file_name):
    pickle_handle = open(file_name, 'rb')
    stress = pickle.load(pickle_handle)
    pickle_handle.close()
    return stress[-1:, 3:9]


def get_radial_data_from_pickle(file_name):
    pickle_handle = open(file_name, 'rb')
    data = pickle.load(pickle_handle)
    return data[:, 0], data[:, 3:]


def get_axial_data_from_pickle(file_name):
    pickle_handle = open(file_name, 'rb')
    data = pickle.load(pickle_handle)
    return data[:, 0], data[:, 1], data[:, 3:]
