import sys

import os

from math import pi

import numpy as np

try:
    import mesh
    from abaqus import session, Mdb, mdb
    import assembly
    import section
    import step
    import mesh
    import interaction
    from abaqusConstants import COORDINATE, STANDALONE, ON, DEFORMABLE_BODY, AXISYM, OFF, THREE_D, DELETE, GEOMETRY
    from abaqusConstants import SINGLE, FIXED, SWEEP, MEDIAL_AXIS, DC3D8, DC3D6, C3D8, C3D6, STANDARD, ANALYSIS
    from abaqusConstants import PERCENTAGE, DOMAIN, DEFAULT, INDEX, YZPLANE, XYPLANE
    from abaqus import backwardCompatibility
    backwardCompatibility.setValues(reportDeprecated=False)
except ImportError:
    print " ERROR: This script require Abaqus CAE to run"
    raise


class Roller:
    class MeshParameters:
        def __init__(self, width):
            self.number_fine_thickness = 24
            self.fine_thickness = 0.5
            self.size_fine_thickness = self.fine_thickness/self.number_fine_thickness

            self.number_fine_length = 60
            self.fine_length = 1.
            self.size_fine_length = self.fine_length/self.number_fine_length

            self.number_fine_width = 27
            self.size_fine_width = width/self.number_fine_width/2

            self.number_coarse_length = 20
            self.number_coarse_thickness = 10

    def __init__(self, inner_radius, outer_radius, width, curvature, angle=5.):
        self.inner_radius = float(inner_radius)
        self.outer_radius = float(outer_radius)
        self.curvature = float(curvature)
        self.width = float(width)
        self.angle = float(angle)

        self.mesh_parameters = self.MeshParameters(self.width)

        Mdb()
        self.modelDB = mdb.models['Model-1']
        self.modelDB.setValues(noPartsInputFile=OFF)
        self.assembly = mdb.models['Model-1'].rootAssembly
        self.part = None

    def write_file(self, file_name):

        # Set filename and path
        output_file_name = os.path.basename(file_name)
        output_file_name_no_ext, extension = output_file_name.split('.')[0:2]

        output_directory = os.path.dirname(file_name)
        if not os.path.isdir(output_directory):
            os.makedirs(output_directory)

        # Set path as working directory
        workdir = os.getcwd()
        if output_directory:
            os.chdir(output_directory)

        self.assembly.Instance(name='roller', part=self.part, dependent=ON)

        # Create job
        mdb.Job(name=output_file_name_no_ext, model=self.modelDB, description='', type=ANALYSIS,
                atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
                memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
                explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
                modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
                scratch='', parallelizationMethodExplicit=DOMAIN, numDomains=1,
                activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=1)

        # Write job to file
        mdb.jobs[output_file_name_no_ext].writeInput(consistencyChecking=OFF)
        # Remove job
        del mdb.jobs[output_file_name_no_ext]
        print output_file_name_no_ext + '.inp'

        # Fix file name
        os.rename(output_file_name_no_ext + '.inp', output_file_name_no_ext + '.' + extension)
        os.chdir(workdir)


if __name__ == '__main__':
    roller = Roller(inner_radius=25./2, outer_radius=40.2/2, width=10.4, curvature=46., angle=5.)

    roller.write_file('input_files/roller.inp')
