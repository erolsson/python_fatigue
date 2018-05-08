from collections import namedtuple

import numpy as np


class Loading:
    force_factor = 27.825
    torque_factor = 42.25

    def __init__(self, sa, sm, ta, tm):
        self.sa, self.sm = sa, sm
        self.ta, self.tm = ta, tm

    @property
    def Fa(self):
        return Loading.force_factor * self.sa

    @property
    def Fm(self):
        return Loading.force_factor * self.sm

    @property
    def Ma(self):
        return Loading.torque_factor * self.ta

    @property
    def Mm(self):
        return Loading.torque_factor * self.tm


class TestResults:
    def __init__(self, file_name):
        self.data = np.genfromtxt(file_name, delimiter=',', skip_header=1)[:, :-1]

    def adjust_runouts(self):
        self.data[self.data[:, -1] > 2E6, -1] = 2E6
        
    def get_test_results(self, heat_treatment, amp='ta', sm=0, tm=0):
        data = self.data[self.data[:, 1] == heat_treatment]
        data = data[data[:, 4] == sm]
        data = data[data[:, 8] == tm]
        amp_col = 6
        if amp != 'ta':
            amp_col = 2
        data = data[data[:, amp_col] != 0]
        results = {}
        for result in data:
            cycles = result[-1]
            load = result[amp_col]
            if results in load:
                if cycles < 2E6:
                    results[load]['failures'] = np.append(results[load]['failures'], cycles)
                else:
                    results[load]['survivors'] = np.append(results[load]['survivors'], cycles)
            else:
                if cycles < 2E6:
                    data_point = {'failures': np.array([cycles]), 'survivors': np.array([])}
                else:
                    data_point = {'failures': np.array([]), 'survivors': np.array([cycles])}
                data_point['loadData'] = result[3:10:2]*1000
                results[load] = data_point
        
        # Counting the number of failed and survived specimens on each load level
        for amp in results.keys():
            results[amp]['number_failures'] = results[amp]['failures'].shape[0]
            results[amp]['number_survivors'] = results[amp]['survivors'].shape[0]
            results[amp]['failure_probability'] = (float(results[amp]['number_failures']) /
                                                   (results[amp]['number_failures']+results[amp]['number_survivors']))
            results[amp]['survival_probability'] = (float(results[amp]['number_survivors']) /
                                                    (results[amp]['number_failures']+results[amp]['number_survivors']))
        return results

    def get_results_for_heat_treatment(self, heat_treatment):
        data = self.data[self.data[:, 1] == heat_treatment]
        results = {}
        loads = np.array([])
        for result in data:
            load = result[3:10:2]
            load_str = np.array_str(load)
            cycles = result[-1]
            print load_str
            if results in load_str:
                if cycles < 2E6:
                    results[load_str]['failures'] = np.append(results[load_str]['failures'], cycles)
                else:
                    results[load_str]['survivors'] = np.append(results[load_str]['survivors'], cycles)
            else:
                loads = np.vstack([loads, load]) if loads.size else load
                if cycles < 2E6:
                    data_point = {'failures': np.array([cycles]), 'survivors': np.array([])}
                else:
                    data_point = {'failures': np.array([]), 'survivors': np.array([cycles])}
                results[load_str] = data_point
        number_of_tests = loads.shape[0]
        nf = np.zeros(number_of_tests)
        ns = np.zeros(number_of_tests)
        number_of_failures = []
        number_of_survivors = []

        for i, load in enumerate(loads):
            load_str = np.array_str(load)
            number_of_failures.append(results[load_str]['failures'])
            number_of_survivors.append(results[load_str]['survivors'])
            nf[i] = len(number_of_failures[-1])
            ns[i] = len(number_of_survivors[-1])
        return loads*1000, nf, ns, number_of_failures, number_of_survivors

    def get_loadings(self, heat_treatment):
        return np.unique(self.data[self.data[:, 1] == heat_treatment, 2:10:2], axis=0)

