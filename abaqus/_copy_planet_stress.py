from abaqusConstants import CYLINDRICAL
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

import sys

from odb_io_functions import read_field_from_odb
from odb_io_functions import write_field_to_odb
from odb_io_functions import CoordinateSystem


# There are a lot of argument to abaqus just use the five last ones
from_odb_name = sys.argv[-6]
to_odb_name = sys.argv[-5]
from_step = sys.argv[-4]
from_frame = int(sys.argv[-3])
to_frame = int(sys.argv[-2])
to_frame_value = float(sys.argv[-1])

planet_system = CoordinateSystem(name='planet_system', origin=(0., 83.5, 0.), point1=(1.0, 83.5, 0.0),
                                 point2=(0.0, 84.5, 0.0), system_type=CYLINDRICAL)

stress_data = read_field_from_odb('S', from_odb_name, 'GEARELEMS', from_step, from_frame,
                                  instance_name='EVAL_TOOTH_0', coordinate_system=planet_system)
write_field_to_odb(stress_data, 'S', to_odb_name, 'mechanical_stresses', frame_number=to_frame,
                   frame_value=to_frame_value, instance_name='tooth_left',
                   invariants=[MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL])

stress_data = read_field_from_odb('S', from_odb_name, 'GEARELEMS', from_step, from_frame,
                                  instance_name='EVAL_TOOTH_1', coordinate_system=planet_system)
write_field_to_odb(stress_data, 'S', to_odb_name, 'mechanical_stresses', frame_number=to_frame,
                   frame_value=to_frame_value, instance_name='tooth_right',
                   invariants=[MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL])
