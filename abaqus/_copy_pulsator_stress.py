from abaqusConstants import CYLINDRICAL
from abaqusConstants import MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL

import sys

from odb_io_functions import read_field_from_odb
from odb_io_functions import write_field_to_odb
from odb_io_functions import CoordinateSystem
from odb_io_functions import flip_node_order

# There are a lot of arguments to abaqus just use the seven last ones
from_odb_name = sys.argv[-5]
to_odb_name = sys.argv[-4]
from_step = sys.argv[-3]
from_frame = int(sys.argv[-2])
to_step = sys.argv[-1]

planet_system = CoordinateSystem(name='planet_system', origin=(0.0, 0.0, 0.0), point1=(1.0, 0.0, 0.0),
                                 point2=(0.0, 1.0, 0.0), system_type=CYLINDRICAL)

stress_data = read_field_from_odb('S', from_odb_name, 'GEARELEMS', from_step, from_frame,
                                  instance_name='EVAL_TOOTH_1', coordinate_system=planet_system)

write_field_to_odb(stress_data, 'S', to_odb_name, to_step, instance_name='tooth_left',
                   invariants=[MISES, MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL])
