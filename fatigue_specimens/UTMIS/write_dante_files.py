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

    with open(directory_to_write + '/hardening_data_pos.dat', 'w') as data_file:
        for i in range(len(hv_data)):
            hv = sum(hv_data[i+1])/len(hv_data[i+1])[0]
            austenite = sum(austenite_data[i + 1])/len(austenite_data[i + 1])[0]
            data_file.write(str(i+i) + ', ' + str(hv) + ', ' + str(austenite) + '\n')

    gp = 1
    with open(directory_to_write + '/residual_stresses_pos.dat', 'w') as stress_file:
        for i, label in enumerate(labels):
            line = str(label) + ", " + str(gp)
            for comp in stress[i, :]:
                line += ", " + str(comp)
            stress_file.write(line + '\n')
            gp += 1
            if gp == 9:
                gp = 1

    with open(directory_to_write + '/residual_stresses_pos.dat', 'w') as stress_file:
        for i, label in enumerate(labels):
            line = str(label) + ", " + str(gp)
            for comp in stress[i, :]:
                line += ", " + str(comp)
            stress_file.write(line + '\n')
            gp += 1
            if gp == 9:
                gp = 1

