from mechanical_analysis import perform_mechanical_analysis
from mechanical_analysis import SpecimenGeometry

SpecimenGeometry(L=100, R=3.5, q=30, t=6, h=24, h1=12, CD=2, delta=-2,
                 name='BendingSpecimenPart')

simulation_name = ''
# namedtuple._asdict() acceptable to use
# noinspection PyProtectedMember
for key, value in SpecimenGeometry._asdict().iteritems():
    simulation_name += key + '=' + str(value) + '_'
simulation_name = simulation_name[:, -1]
print simulation_name
# perform_mechanical_analysis(SpecimenGeometry, b1=8, b2=45, delta=.2, run_directory=)
