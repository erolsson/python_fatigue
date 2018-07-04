import odbAccess
import numpy as np

from abaqusConstants import *

odb = odbAccess.openOdb('/scratch/users/erik/scania_gear_analysis/odb_files/dante_interpolation/'
                        'Toolbox_Carbon_1_4_quarter.odb', readOnly=False)

step = odb.steps['Carburization-3']
frame = step.frames[len(step.frames) - 1]
field = frame.fieldOutputs['CONC']
new_step = odb.Step(name='dante_data', description='', domain=TIME, timePeriod=1)
new_frame = new_step.Frame(incrementNumber=0, frameValue=0, description='')
new_field = -2.07934384e+04*field*field + 2.98225944e+02*field-1.60574051e-01
new_frame.FieldOutput(name='NT11', field=new_field)

odb.save()
odb.close()
