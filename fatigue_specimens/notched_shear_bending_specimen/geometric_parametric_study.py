import os

from mechanical_analysis import perform_mechanical_analysis
from mechanical_analysis import SpecimenGeometry

specimen = SpecimenGeometry(L=100, R=3.5, q=30, t=6, h=24, h1=12, CD=2, delta=-2,
                            name='BendingSpecimenPart')

simulation_name = os.path.expanduser('~/scania_gear_analysis/abaqus/fatigue_specimens/notched_shear_bending_specimen/')
# namedtuple._asdict() acceptable to use
# noinspection PyProtectedMember
for key, value in specimen._asdict().iteritems():
    if key != 'name':
        simulation_name += key + '=' + str(value) + '_'
simulation_name = simulation_name[:-1]

# noinspection PyProtectedMember
perform_mechanical_analysis(specimen._asdict(), b1=8, b2=45, delta=.2, run_directory=simulation_name)
