import re
import numpy as np


class InputFileReader:
    def __init__(self):
        self.nodal_data = None
        self.elements = None

    def read_input_file(self, model_filename):
        nodes = []
        elements = []
        with open(model_filename) as full_model_file:
            lines = full_model_file.readlines()
            reading_nodes = False
            reading_elements = False

            for line in lines:
                if bool(re.search('node', line.split()[0], re.IGNORECASE)):
                    reading_nodes = True
                    reading_elements = False
                elif bool(re.search('element', line.split()[0], re.IGNORECASE)):
                    reading_elements = True
                    reading_nodes = False
                elif '*' in line.split()[0]:
                    reading_nodes = False
                    reading_elements = False
                elif reading_nodes:
                    nodes.append(line.split(","))
                elif reading_elements:
                    elements.append(line.split(","))
        self.nodal_data = np.zeros((len(nodes), 4))

        for i, node in enumerate(nodes):
            self.nodal_data[i, :] = node

        self.elements = np.array(elements, dtype=int)

    def write_geom_include_file(self, filename):
        element_type = 'DC3D8'
        if simulation_type == 'Mechanical':
            element_type = 'C3D8'

        file_lines = ['*NODE']
        for node in self.nodal_data:
            file_lines.append(
                '\t' + str(int(node[0])) + ', ' + str(node[1]) + ', ' + str(node[2]) + ', ' + str(node[3]))
        file_lines.append('*ELEMENT, TYPE=' + element_type)
        for element in self.element_data:
            element_string = [str(e) for e in element]
            element_string = ', '.join(element_string)
            file_lines.append('\t' + element_string)

        with open(filename, 'w') as inc_file:
            for line in file_lines:
                inc_file.write(line + '\n')
            inc_file.write('**EOF')

    def write_sets_file(self, filename):
        pass
