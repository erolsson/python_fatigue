from collections import OrderedDict

import glob
import os
import pickle

import numpy as np


def _get_evaluated_findley_parameters():
    findley_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/stresses/findley/')
    findley_parameter_directories = glob.glob(findley_pickle_directory + 'a800=*/')
    findley_parameter_directories = [os.path.normpath(directory).split(os.sep)[-1]
                                     for directory in findley_parameter_directories]
    _evaluated_findley_parameters = [directory[5:] for directory in findley_parameter_directories]
    _evaluated_findley_parameters = [float(parameter.replace('_', '.')) for parameter in _evaluated_findley_parameters]
    return np.array(sorted(_evaluated_findley_parameters))


def _get_findley_data():
    findley_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/stresses/findley/')
    _findley_data = {'smooth': {0: {}, -1: {}},
                     'notched': {0: {}, -1: {}}}

    _evaluated_findley_parameters = _get_evaluated_findley_parameters()
    for findley_parameter in _evaluated_findley_parameters:
        for specimen, specimen_data in _findley_data.iteritems():
            for load_ratio, load_ratio_data in specimen_data.iteritems():
                file_string = findley_pickle_directory + 'a800=' + str(findley_parameter).replace('.', '_') + \
                                  '/findley_' + specimen + '_R=' + str(load_ratio) + '_s=*MPa.pkl'
                files = glob.glob(file_string)
                for filename in files:
                    stress = float(filename[len(file_string.split('*')[0]):-len(file_string.split('*')[1])])
                    if stress not in load_ratio_data:
                        load_ratio_data[stress] = OrderedDict()
                    with open(filename) as pickle_handle:
                        load_ratio_data[stress][findley_parameter] = pickle.load(pickle_handle)

    return _findley_data


def _get_dante_data():
    dante_pickle_directory = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/heat_treatment_data'
                                                '/dante/')
    data = {}
    for specimen in ['smooth', 'notched']:
        with open(dante_pickle_directory + 'data_utmis_' + specimen + '.pkl') as pickle_handle:
            data[specimen] = pickle.load(pickle_handle)
    return data


def _get_geometry_data():
    pickle_directory_geometry = os.path.expanduser('~/scania_gear_analysis/pickles/utmis_specimens/geometry/')
    data = {}
    for specimen in ['smooth', 'notched']:
        with open(pickle_directory_geometry + 'nodal_coordinates_' + specimen + '.pkl') as pickle_handle:
            data[specimen] = pickle.load(pickle_handle)
    return data


findley_data = _get_findley_data()
dante_data = _get_dante_data()
geometry_data = _get_geometry_data()
evaluated_findley_parameters = _get_evaluated_findley_parameters()


if __name__ == '__main__':
    _get_findley_data()
