import numpy as np


class TestResults:
    def __init__(self, file_name):
        self.data = np.genfromtxt(file_name, delimiter=',')

    def adjust_runouts(self):
        self.data[self.data[:, -1] > 2E6, -1] = 2E6

    def get_test_results(self):
        results = {}
        for result in self.data:
            cycles = result[1]
            load = result[0]
            if load in results:
                if cycles < 2E6:
                    results[load]['failures'] = np.append(results[load]['failures'], cycles)
                else:
                    results[load]['survivors'] = np.append(results[load]['survivors'], cycles)
            else:
                if cycles < 2E6:
                    data_point = {'failures': np.array([cycles]), 'survivors': np.array([])}
                else:
                    data_point = {'failures': np.array([]), 'survivors': np.array([cycles])}
                results[load] = data_point
        # Counting the number of failed and survived specimens on each load level
        for amp in results.keys():
            results[amp]['number_failures'] = results[amp]['failures'].shape[0]
            results[amp]['number_survivals'] = results[amp]['survivors'].shape[0]
            results[amp]['failure_probability'] = (float(results[amp]['number_failures']) /
                                                   (results[amp]['failures'] + results[amp]['number_survivals']))
            results[amp]['survival_probability'] = (float(results[amp]['number_survivals']) /
                                                    (
                                                    results[amp]['number_failures'] + results[amp]['number_survivals']))
        return results
