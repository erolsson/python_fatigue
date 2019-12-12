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

    def __init__(self, inner_radius, outer_radius, width, angle=180.):
        self.inner_radius = float(inner_radius)
        self.outer_radius = float(outer_radius)
        self.width = float(width)
        self.angle = float(angle)

        self.mesh_parameters = self.MeshParameters(self.width)

        Mdb()
        self.modelDB = mdb.models['Model-1']
        self.modelDB.setValues(noPartsInputFile=OFF)
        self.assembly = mdb.models['Model-1'].rootAssembly
        self.part = None

    def create_mesh(self):
        package_directory = os.path.abspath(os.path.join(os.getcwd(), "../"))
        sys.path.append(package_directory)
        import mesh_class.mesh_class
        reload(mesh_class.mesh_class)
        from mesh_class.mesh_class import MeshClass

        mesher = MeshClass()
        nodes, _ = mesher.create_block(nx=self.mesh_parameters.number_fine_length + 1,
                                       ny=self.mesh_parameters.number_fine_width + 1,
                                       nz=self.mesh_parameters.number_fine_thickness + 1,
                                       dx=self.mesh_parameters.size_fine_length,
                                       dy=self.mesh_parameters.size_fine_width,
                                       dz=self.mesh_parameters.size_fine_thickness,
                                       x0=0,
                                       y0=0,
                                       z0=-self.outer_radius)

        surfz2 = mesher.create_transition_plate(nodes[:, :, -1], 'z', d=self.mesh_parameters.size_fine_thickness,
                                                order=1, direction=1)
        surfz = np.empty(shape=(surfz2.shape[0] + 1, surfz2.shape[1]), dtype=object)
        surfz[:-1, :] = surfz2
        for side, direction in zip([-1], [1]):
            surfx1 = mesher.create_transition_plate(nodes[side, :, :], 'x', d=self.mesh_parameters.size_fine_length,
                                                    order=1, direction=direction)

            corner = mesher.create_transition_corner_out(nodes[side, :, -1],
                                                         d1=self.mesh_parameters.size_fine_length,
                                                         d2=self.mesh_parameters.size_fine_thickness,
                                                         axis1='x',
                                                         axis2='z',
                                                         axis3='y',
                                                         order=1)

            surfx = np.empty(shape=(surfx1.shape[0], surfx1.shape[1]+1), dtype=object)

            surfx[:, 0:-1] = surfx1
            surfx[:, -1] = corner
            surfx2 = np.empty(shape=((surfx1.shape[0] - 1)/3 + 1, (surfx1.shape[1])/3 + 2), dtype=object)
            surfx2[:, 0:-1] = mesher.create_transition_plate(surfx, 'x', d=3*self.mesh_parameters.size_fine_length,
                                                             order=1, direction=direction)

            surfz[side, :] = corner

            surfx2[:, -1] = mesher.create_transition_corner_out(surfz[side, :],
                                                                d1=3*self.mesh_parameters.size_fine_length,
                                                                d2=3*self.mesh_parameters.size_fine_thickness,
                                                                axis1='x',
                                                                axis2='z',
                                                                axis3='y',
                                                                order=1)

            x = surfx2[0, 0].x
            xl = self.outer_radius*pi/2*direction
            dx = (xl - x)/(self.mesh_parameters.number_coarse_length - 1)
            dy = surfx2[1, 1].y - surfx2[0, 0].y
            dz = surfx2[1, 1].z - surfx2[0, 0].z

            mesher.create_block(nx=self.mesh_parameters.number_coarse_length,
                                ny=surfx2.shape[0],
                                nz=surfx2.shape[1],
                                dx=dx,
                                dy=dy,
                                dz=dz,
                                x0=surfx2[0, 0].x,
                                y0=surfx2[0, 0].y,
                                z0=surfx2[0, 0].z)

            dz = (-self.inner_radius - surfx2[0, -1].z)/(self.mesh_parameters.number_coarse_thickness - 1)
            mesher.create_block(nx=self.mesh_parameters.number_coarse_length,
                                ny=surfx2.shape[0],
                                nz=self.mesh_parameters.number_coarse_thickness,
                                dx=dx,
                                dy=dy,
                                dz=dz,
                                x0=surfx2[0, 0].x,
                                y0=surfx2[0, 0].y,
                                z0=surfx2[0, -1].z)

        surfz2 = mesher.create_transition_plate(surfz, 'z', d=3*self.mesh_parameters.size_fine_thickness,
                                                order=1, direction=1)

        mesher.create_block(nx=surfz2.shape[0] + 1,
                            ny=surfz2.shape[1],
                            nz=self.mesh_parameters.number_coarse_thickness,
                            dx=surfz2[1, 1].x - surfz2[0, 0].x,
                            dy=surfz2[1, 1].y - surfz2[0, 0].y,
                            dz=dz,
                            x0=0,
                            y0=surfz2[0, 0].y,
                            z0=surfz2[0, 0].z)

        nodes, elements = mesher.lists_for_part()
        self.part = self.modelDB.PartFromNodesAndElements(name='_tmp',
                                                          dimensionality=THREE_D,
                                                          type=DEFORMABLE_BODY,
                                                          nodes=nodes,
                                                          elements=elements)
        self.part.mergeNodes(nodes=self.part.nodes, tolerance=1E-8)

        mesher = MeshClass()
        for n in self.part.nodes:
            mesher.create_node(n.coordinates[0], n.coordinates[1], n.coordinates[2], label=n.label)
        for e in self.part.elements:
            e_nodes = []
            for n in e.getNodes():
                e_nodes.append(mesher.nodes[n.label])
            mesher.create_element(nodes=e_nodes, label=e.label)

        del mdb.models['Model-1'].parts['_tmp']

        bounding_box = mesher.get_bounding_box()

        node_sets = {'exposed_nodes': []}
        element_sets = {'exposed_elements': []}

        for set_list, func in zip([node_sets['exposed_nodes'], element_sets['exposed_elements']],
                                  [mesher.get_nodes_by_bounding_box, mesher.get_elements_by_bounding_box]):
            set_list += func(z_max=bounding_box[4] + 1e-5)
            set_list += func(z_min=bounding_box[5] - 1e-5)
            set_list += func(y_min=bounding_box[3] - 1e-5)

        node_sets['x0_nodes'] = mesher.get_nodes_by_bounding_box(x_max=1e-8)
        node_sets['y0_nodes'] = mesher.get_nodes_by_bounding_box(y_max=1e-8)

        # These will be the z0 nodes after rot
        node_sets['z0_nodes'] = mesher.get_nodes_by_bounding_box(x_min=bounding_box[1] - 1e-8)

        node_sets['inner_nodes'] = mesher.get_nodes_by_bounding_box(z_min=bounding_box[5] - 1e-8)
        node_sets['outer_nodes'] = mesher.get_nodes_by_bounding_box(z_max=bounding_box[4] + 1e-8)

        element_sets['inner_elements'] = mesher.get_elements_by_bounding_box(z_min=bounding_box[5] - 1e-8)
        element_sets['outer_elements'] = mesher.get_elements_by_bounding_box(z_max=bounding_box[4] + 1e-8)

        node_sets['monitor_node'] = mesher.get_nodes_by_bounding_box(x_max=1e-8, y_max=1e-8,
                                                                     z_max=bounding_box[4] + 1e-8)

        left_nodes = mesher.get_nodes_by_bounding_box()
        mesher.add_to_node_set(left_nodes, 'right_nodes')
        mesher.transform_block_radially('right_nodes', 'y', [0, 0, 0], 'x')

        nodal_data, element_data = mesher.lists_for_part()
        self.part = self.modelDB.PartFromNodesAndElements(name='roller',
                                                          dimensionality=THREE_D,
                                                          type=DEFORMABLE_BODY,
                                                          nodes=nodal_data,
                                                          elements=element_data)

        for name, node_list in node_sets.iteritems():
            label_list = [n.label for n in node_list]
            self.part.SetFromNodeLabels(name=name, nodeLabels=label_list)

        for name, element_list in element_sets.iteritems():
            label_list = [e.label for e in element_list]
            self.part.SetFromElementLabels(name=name, elementLabels=label_list)

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
    roller = Roller(25./2, 40.2/2, 10.4)
    roller.create_mesh()
    roller.write_file('input_files/roller.inp')
