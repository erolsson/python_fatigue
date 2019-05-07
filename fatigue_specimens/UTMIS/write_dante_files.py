from collections import OrderedDict
from abaqusConstants import ELEMENT_NODAL, INTEGRATION_POINT

import numpy as np

from abaqus_files.odb_io_functions import read_field_from_odb
from materials.hardess_convertion_functions import HRC2HV


def write_dante_files(dante_odb, directory_to_write):
    stress, _, labels = read_field_from_odb('S', dante_odb, step_name='Tempering', frame_number=-1,
                                            position=INTEGRATION_POINT, get_position_numbers=True)

    hrc, labels, _ = read_field_from_odb('SDV_HARDNESS', dante_odb, step_name='Tempering', frame_number=-1,
                                         position=ELEMENT_NODAL, get_position_numbers=True)

    au, labels, _ = read_field_from_odb('SDV_AUSTENITE', dante_odb, step_name='Tempering', frame_number=-1,
                                        position=ELEMENT_NODAL, get_position_numbers=True)

    hv = HRC2HV(hrc)
    hv_data = OrderedDict()
    austenite_data = OrderedDict()
    for data, data_dict in zip([hv, au], [hv_data, austenite_data]):
        for i, label in enumerate(labels):
            if label not in data_dict:
                data_dict[label] = []
            data_dict[label].append(data[i])

    for file_name, data in zip(['hardness.dat', 'austenite.dat'],[hv_data, austenite_data]):
        with open(directory_to_write + '/' + file_name, 'w') as data_file:
            for instance in ['SPECIMEN_PART_POS', 'SPECIMEN_PART_NEG']:
                for i in range(len(data)):
                    value = sum(data[i+1])/len(data[i+1])
                    data_file.write(instance + '.' + str(i+1) + ', ' + str(value[0]) + '\n')

    with open(directory_to_write + '/residual_stresses_pos.dat', 'w') as stress_file:
        for i, label in enumerate(labels):
            line = str(label) + ", " + str(gp)
            for comp in stress[i, :]:
                line += ", " + str(comp)
            stress_file.write(line + '\n')
            gp += 1
            if gp == 9:
                gp = 1

