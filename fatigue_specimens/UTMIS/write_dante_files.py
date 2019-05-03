from abaqus_files.odb_io_functions import read_field_from_odb

from abaqusConstants import INTEGRATION_POINT


def write_dante_files(dante_odb, directory_to_write):
    stress, _, labels = read_field_from_odb('S', dante_odb, step_name='Tempering', frame_number=-1,
                                            position=INTEGRATION_POINT, get_position_numbers=True)
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
