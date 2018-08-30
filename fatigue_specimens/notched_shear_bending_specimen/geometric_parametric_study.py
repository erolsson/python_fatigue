import os

from mechanical_analysis import perform_mechanical_analysis
from mechanical_analysis import SpecimenGeometry


def run_simulation(geometry):
    simulation_name = os.path.expanduser('~/scania_gear_analysis/abaqus/fatigue_specimens/'
                                         'notched_shear_bending_specimen/')
    # namedtuple._asdict() acceptable to use
    # noinspection PyProtectedMember
    for key, value in geometry._asdict().iteritems():
        if key != 'name':
            simulation_name += key + '=' + str(value).replace('.', '_') + '_'
    simulation_name = simulation_name[:-1]

    # noinspection PyProtectedMember
    perform_mechanical_analysis(geometry._asdict(), delta=.2, run_directory=simulation_name)


if __name__ == '__main__':
    for r in (4.5, 5.5):
            for q in (0, 15, 30, 45):
                specimen = SpecimenGeometry(L=100, R=r, q=q, t=6, h=24, h1=8, CD=2, delta=0,
                                            name='BendingSpecimenPart')
                run_simulation(specimen)
