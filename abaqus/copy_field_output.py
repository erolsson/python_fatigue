import odbAccess
import numpy as np

from abaqusConstants import *

odb = odbAccess.openOdb('/scratch/users/erik/scania_gear_analysis/odb_files/dante_interpolation/danteTooth20170220.odb',
                        readOnly=False)

frame = odb.steps['danteResults_DC1_4'].frames[0]
field = frame.fieldOutputs['Q_MARTENSITE']
field = field.getSubset(position=NODAL)
print len(field.values)
frame.FieldOutput(name='NT', type=SCALAR)
