import sys

from odb_io_functions import read_field_from_odb
from odb_io_functions import write_field_to_odb
from odb_io_functions import CoordinateSystem


from_odb_name = sys.argv[1]
to_odb_name = sys.argv[2]
from_step = sys.argv[3]
from_frame = int(sys.argv[4])
to_frame = int(sys.argv[5])

planet_system = CoordinateSystem(name='planet_system', origin=(0., 83.5, 0.), point1=(0.0, 1.0, 0.0),
                                 point2=(1.0, 0.0, 0.0), system_type=CYLINDRICAL)

stress_data = read_field_from_odb('S', from_odb_name, 'GEARELEMS', from_step, from_frame,
                                  instance_name='EVAL_TOOTH_0', coordinate_system=planet_system)
write_field_to_odb(stress_data, 'S', to_odb_name, 'mechanical_stresses', frame_number=frame_counter,
                   instance_name='tooth_left')

stress_data = read_field_from_odb('S', from_odb_name, 'GEARELEMS', from_step, from_frame,
                                  instance_name='EVAL_TOOTH_1', coordinate_system=planet_system)
write_field_to_odb(stress_data, 'S', to_odb_name, 'mechanical_stresses', frame_number=frame_counter,
                   instance_name='tooth_right')
