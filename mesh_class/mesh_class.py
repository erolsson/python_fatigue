from math import atan2, sin, cos

import numpy as np

xyz_idx = {'x': 0, 'y': 1, 'z': 2}


class Node:
    def __init__(self, label, x, y, z):
        self.label = label
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return str(self.label)


class Element:
    def __init__(self, label, nodes, element_type):
        self.label = label
        self.element_type = element_type

        if element_type[1] == '3':
            dim = 3
        else:
            dim = 2
        e_nodes = []
        x0 = sum([node.x for node in nodes])/len(nodes)
        y0 = sum([node.y for node in nodes])/len(nodes)
        z0 = sum([node.z for node in nodes])/len(nodes)
        nodes = sorted(nodes, key=lambda n: atan2(n.z - z0, (n.y - y0)**2 + (n.x - x0)**2))
        for i in range(dim - 1):
            stride = len(nodes)/(dim - 1)
            plane_nodes = nodes[i*stride:(i+1)*stride]
            x0 = sum([node.x for node in plane_nodes]) / len(plane_nodes)
            y0 = sum([node.y for node in plane_nodes]) / len(plane_nodes)
            e_nodes += sorted(plane_nodes, key=lambda n: atan2(n.y - y0, n.x - x0))
        self.nodes = e_nodes

    def get_bounding_box(self):
        bbox = np.zeros(6)
        i = 0
        for axis in ['x', 'y', 'z']:
            for func in [np.min, np.max]:
                bbox[i] = func([getattr(n, axis) for n in self.nodes])
                i += 1
        return bbox


class MeshClass:
    def __init__(self):
        self.nodes = {}
        self.node_sets = {}
        self.element_sets = {}
        self.elements = {}
        self.node_counter = 1
        self.element_counter = 1

    def create_node(self, x, y, z, node_set=None, label=None):
        if label is None:
            label = self.node_counter
            self.node_counter += 1
        else:
            self.node_counter = label + 1
        n = Node(label, x, y, z)
        self.nodes[label] = n
        if node_set is not None:
            if node_set in self.node_sets:
                self.node_sets[node_set].add(n)
            else:
                self.node_sets[node_set] = {n}
        return n

    def create_element(self, nodes, element_type='C3D8R', element_set=None, label=None):
        node_list = []
        for n in nodes:
            if isinstance(n, Node):
                node_list.append(n)
            else:
                if isinstance(n, np.ndarray):
                    while len(n.shape) > 1:
                        n = n.flatten()
                    n = n.tolist()
                node_list += n
        if label is None:
            e = Element(self.element_counter, node_list, element_type)
        else:
            e = Element(label, node_list, element_type)
        if element_type in self.elements:
            self.elements[element_type].append(e)
        else:
            self.elements[element_type] = [e]
        self.element_counter += 1

        if element_set is not None:
            if element_set in self.element_sets:
                self.element_sets[element_set].append(e)
            else:
                self.element_sets[element_set] = [e]
        return e

    def copy_node_plane(self, nodes, axis, distance, node_set):
        nx, ny = nodes.shape
        axis_idx = xyz_idx[axis]
        new_nodes = np.empty(shape=(nx, ny), dtype=object)
        for i in range(nx):
            for j in range(ny):
                args = [nodes[i, j].x, nodes[i, j].y, nodes[i, j].z]
                args[axis_idx] += distance
                new_nodes[i, j] = self.create_node(*args, node_set=node_set)
        return new_nodes

    @staticmethod
    def _attach_node_plane(nodes_plate, x0=0., y0=0., z0=0.,
                           x_neg=None, y_neg=None, z_neg=None, x_pos=None, y_pos=None, z_pos=None):
        if x_pos is not None:
            nodes_plate[-1, :, :] = x_pos
            x0 = x_pos[0, 0].x
        if x_neg is not None:
            nodes_plate[0, :, :] = x_neg
            x0 = x_neg[0, 0].x

        if y_pos is not None:
            nodes_plate[:, -1, :] = y_pos
            y0 = y_pos[0, 0].y
        if y_neg is not None:
            nodes_plate[:, 0, :] = y_neg
            y0 = y_neg[0, 0].y

        if z_pos is not None:
            nodes_plate[:, :, -1] = z_pos
            z0 = z_pos[0, 0].z
        if z_neg is not None:
            nodes_plate[:, :, 0] = z_neg
            z0 = z_pos[0, 0].z

        return nodes_plate, x0, y0, z0

    def create_block(self, nx, ny, nz, dx, dy, dz, x0=0., y0=0., z0=0.,
                     x_neg=None, y_neg=None, z_neg=None, x_pos=None, y_pos=None, z_pos=None,
                     node_set='', element_set=''):
        nodes_plate = np.empty(shape=(nx, ny, nz), dtype=object)
        elements_plate = []

        nodes_plate, x0, y0, z0 = self._attach_node_plane(nodes_plate, x0, y0, z0, x_neg, y_neg, z_neg,
                                                          x_pos, y_pos, z_pos)

        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    if nodes_plate[i, j, k] is None:
                        nodes_plate[i, j, k] = self.create_node(i*dx + x0, j*dy + y0, k*dz + z0, node_set=node_set)
                    if i > 0 and j > 0 and k > 0:
                        e_nodes = [nodes_plate[i - 1, j - 1, k - 1], nodes_plate[i, j - 1, k - 1],
                                   nodes_plate[i - 1, j - 1, k], nodes_plate[i, j - 1, k],
                                   nodes_plate[i - 1, j, k - 1], nodes_plate[i, j, k - 1],
                                   nodes_plate[i - 1, j, k], nodes_plate[i, j, k]]
                        elements_plate.append(self.create_element(e_nodes, element_set=element_set))
        return nodes_plate, elements_plate

    def create_block_axi(self, nx, ny, nz, dx, dy, dz, x0=0, y0=0, z0=0,
                         x_neg=None, y_neg=None, z_neg=None, x_pos=None, y_pos=None, z_pos=None,
                         node_set='', element_set=''):

        nodes_plate = np.empty(shape=(nx, ny, nz), dtype=object)
        elements_plate = []

        nodes_plate, x0, y0, z0 = self._attach_node_plane(nodes_plate, x0, y0, z0, x_neg, y_neg, z_neg,
                                                          x_pos, y_pos, z_pos)

        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    if nodes_plate[i, j, k] is None:
                        nodes_plate[i, j, k] = self.create_node(i*dx + x0, j*dy + y0, k*dz + z0, node_set=node_set)
                    if i > 0 and j > 0 and k > 0:
                        e_nodes = [nodes_plate[i - 1, j - 1, k - 1], nodes_plate[i, j - 1, k - 1],
                                   nodes_plate[i - 1, j, k - 1], nodes_plate[i, j, k - 1]]
                        elements_plate.append(self.create_element(e_nodes, element_set=element_set,
                                                                  element_type='CAX4'))
        return nodes_plate, elements_plate

    @staticmethod
    def _assign_axes_for_rotation(nodes, rotation_axis, radial_axis):
        if rotation_axis not in 'xyz' and radial_axis not in 'xyz':
            raise ValueError('Rotation axis or radial axis not specified correctly')

        axis1 = radial_axis
        axis2 = 'xyz'.replace(rotation_axis, '').replace(radial_axis, '')

        r_max = 0
        l_max = 0
        for n in nodes:
            r_max = max(r_max, abs(getattr(n, axis1)), abs(getattr(n, axis2)))
            l_max = max(l_max, abs(getattr(n, axis2)))

        return axis1, axis2, r_max, l_max

    def transform_square_to_cylinder(self, node_set, rotation_axis, radial_axis, angle, f=0.75):
        nodes = self.node_sets[node_set]

        axis1, axis2, r_max, _ = self._assign_axes_for_rotation(nodes, rotation_axis, radial_axis)

        for n in nodes:
            n1 = getattr(n, axis1)
            n2 = getattr(n, axis2)
            if n1 > 0 and n2 > 0:
                if n1 > n2:
                    n2, n1 = n1, n2
                r = n2
                q = n1/n2*angle/2
                d2 = r*cos(q) - n2
                d1 = r*sin(q) - n1
                k = r/r_max
                setattr(n, axis1, getattr(n, axis1) + d1*k**f)
                setattr(n, axis2, getattr(n, axis2) + d2*k**f)

    def transform_square_to_sector(self, node_set, rotation_axis, radial_axis, angle):
        # Todo: Check this one for bugs!!!
        nodes = self.node_sets[node_set]
        axis1, axis2, r_max, _ = self._assign_axes_for_rotation(nodes, rotation_axis, radial_axis)

        for n in nodes:
            n1 = getattr(n, axis1)
            n2 = getattr(n, axis2)
            if n1 > n2:
                n2, n1 = n1, n2
            r = n1
            if n1 > 0:
                q = n2/n1*angle/2
            else:
                q = 0
            dx = r*cos(q) - n1
            dy = r*sin(q) - n2

            setattr(n, axis1, getattr(n, axis1) + dx)
            setattr(n, axis2, getattr(n, axis2) + dy)

    def sweep_block(self, node_set, rotation_axis, radial_axis, angle):
        nodes = self.node_sets[node_set]
        axis1, axis2, r_max, l_max = self._assign_axes_for_rotation(nodes, rotation_axis, radial_axis)

        for n in nodes:
            n1 = getattr(n, axis1)   # Coordinate of node along radial axis
            n2 = getattr(n, axis2)   # Coordinate of node along other axis
            r = abs(n1)
            q = n2/l_max*angle
            d1 = r*cos(q) - n1
            d2 = r*sin(q) - n2

            setattr(n, axis1, getattr(n, axis1) + d1)
            setattr(n, axis2, getattr(n, axis2) + d2)

    def transform_block_radially(self, node_set, rotation_axis, rotation_point, circ_axis):
        radial_axis = 'xyz'.replace(rotation_axis, '').replace(circ_axis, '')
        nodes = self.node_sets[node_set]
        r_max = max([abs(getattr(n, radial_axis)) for n in nodes])
        for n in nodes:
            n1 = getattr(n, radial_axis)   # Coordinate of node along radial axis
            n2 = getattr(n, circ_axis)   # Coordinate of node along other axis
            r = abs(n1)

            # q = 0
            # if n1 != 0:
            q = abs(n2/r_max)
            if n1 != 0:
                d1 = r*cos(q)*n1/abs(n1) - n1
                setattr(n, radial_axis, getattr(n, radial_axis) + d1)
            if n2 != 0:
                d2 = r*sin(q)*n2/abs(n2) - n2
                setattr(n, circ_axis, getattr(n, circ_axis) + d2)

    def create_transition_cell(self, transition_block, axis, element_set='', node_set=''):
        # The mid element
        if axis == 'x':
            d = (transition_block[-1, 0, 0].x - transition_block[0, 0, 0].x)/3
            base_plate = transition_block[0, :, :]
            top_nodes = transition_block[3, 0:4:3, 0:4:3]
        elif axis == 'y':
            d = (transition_block[0, -1, 0].y - transition_block[0, 0, 0].y)/3
            base_plate = transition_block[:, 0, :]
            top_nodes = transition_block[0:4:3, 3, 0:4:3]
        elif axis == 'z':
            d = (transition_block[0, 0, -1].z - transition_block[0, 0, 0].z)/3
            base_plate = transition_block[:, :, 0]
            top_nodes = transition_block[0:4:3, 0:4:3, 3]
        else:
            raise ValueError('Rotation axis or radial axis not specified correctly')

        second_plate = self.copy_node_plane(base_plate, axis, d, node_set)
        center_plate = self.copy_node_plane(base_plate[1:3, 1:3], axis, 3*d/2, node_set)
        mid_plate_x = self.copy_node_plane(base_plate[1:3, 0:4:3], axis, 2*d, node_set)
        mid_plate_y = self.copy_node_plane(base_plate[0:4:3, 1:3], axis, 2*d, node_set)

        # Create the base plate
        nx, ny = base_plate.shape
        for i in range(1, nx):
            for j in range(1, ny):
                e_nodes = [base_plate[i - 1:i + 1, j - 1:j + 1], second_plate[i - 1:i + 1, j - 1:j + 1]]
                self.create_element(e_nodes, element_set=element_set)

        # Create the center element
        e_nodes = [second_plate[1:3, 1:3], center_plate]
        self.create_element(e_nodes, element_set=element_set)

        # Create the side elements in the "+"
        for i in range(2):
            e_nodes1 = [mid_plate_x[:, i], center_plate[:, i], second_plate[1:3, 2*i:2*i + 2]]
            e_nodes2 = [mid_plate_y[i, :], center_plate[i, :], second_plate[2*i:2*i + 2, 1:3]]

            self.create_element(e_nodes1, element_set=element_set)
            self.create_element(e_nodes2, element_set=element_set)

        # Create the corner elements
        for i in range(2):
            for j in range(2):
                e_nodes = [top_nodes[i, j], second_plate[2*i:2*i + 2, 2*j:2*j + 2], center_plate[i, j],
                           mid_plate_x[i, j], mid_plate_y[i, j]]
                self.create_element(e_nodes, element_set=element_set)

        # Create the "small" center element
        e_nodes = [mid_plate_x, center_plate]
        self.create_element(e_nodes, element_set=element_set)

        # Create the side skewed elements
        for i in range(2):
            e_nodes = [mid_plate_y[i, :], top_nodes[i, :], center_plate[i, :], mid_plate_x[i, :]]
            self.create_element(e_nodes, element_set=element_set)

        # create the top element
        e_nodes = [top_nodes, mid_plate_x]
        self.create_element(e_nodes, element_set=element_set)

    def _assign_bases_and_axes(self, axis, transition_block, node_set):
        if axis == 'x':
            d1 = (transition_block[0, -1, 0].y - transition_block[0, 0, 0].y)/3
            d2 = (transition_block[0, 0, -1].z - transition_block[0, 0, 0].z)/3
            axis1, axis2 = 'y', 'z'
            base1 = transition_block[:, :, 0]
            base2 = transition_block[:, 0, :]
            center_line = self.copy_node_plane(transition_block[:, 1:2, 0], 'z', d1, node_set)
        elif axis == 'y':
            d1 = (transition_block[-1, 0, 0].x - transition_block[0, 0, 0].x)/3
            d2 = (transition_block[0, 0, -1].z - transition_block[0, 0, 0].z)/3
            axis1, axis2 = 'x', 'z'
            base1 = transition_block[0, :, :]
            base2 = transition_block[:, :, 0].transpose()
            center_line = self.copy_node_plane(transition_block[0, :, 1:2], 'x', d1, node_set)

        elif axis == 'z':
            axis1, axis2 = 'x', 'y'
            d1 = (transition_block[-1, 0, 0].x - transition_block[0, 0, 0].x)/3
            d2 = (transition_block[0, -1, 0].y - transition_block[0, 0, 0].y)/3
            base1 = transition_block[0, :, :].transpose()
            base2 = transition_block[:, 0, :].transpose()
            center_line = self.copy_node_plane(transition_block[1:2, 0, :], 'y', d1, node_set).transpose()
        else:
            raise ValueError('Rotation axis or radial axis not specified correctly')
        return d1, d2, axis1, axis2, base1, base2, center_line

    def create_transition_cell_corner(self, transition_block, axis, element_set='', node_set=''):
        d1, d2, axis1, axis2, base1, base2, center_line = self._assign_bases_and_axes(axis, transition_block, node_set)

        mid1 = self.copy_node_plane(base1[:, 1:], axis1, d1, node_set)
        mid2 = self.copy_node_plane(base2[:, 1:], axis2, d2, node_set)

        top1 = self.copy_node_plane(base1[1:3, 3:], axis1, 2*d1, node_set)
        top2 = self.copy_node_plane(base2[1:3, 3:], axis2, 2*d2, node_set)

        center2 = self.copy_node_plane(base1[0:4, 2:], axis1, 2*d1, node_set)

        corner = self.copy_node_plane(base1[0:4:3, 3:], axis1, 3*d1, node_set)

        # create the base plates
        for i in range(1, 4):
            e_nodes = [base1[i - 1:i + 1, 0:2], base2[i - 1:i + 1, 1], center_line[i - 1:i + 1, 0]]
            self.create_element(e_nodes, element_set=element_set)

            e_nodes = [base1[i - 1:i + 1, 1:3], mid1[i - 1:i + 1, 1], center_line[i - 1:i + 1, 0]]
            self.create_element(e_nodes, element_set=element_set)

            e_nodes = [base2[i - 1:i + 1, 1:3], mid2[i - 1:i + 1, 1], center_line[i - 1:i + 1, 0]]
            self.create_element(e_nodes, element_set=element_set)

            e_nodes = [base1[i - 1:i + 1, 2:4], mid1[i - 1:i + 1, 1:3]]
            self.create_element(e_nodes, element_set=element_set)

            e_nodes = [base2[i - 1:i + 1, 2:4], mid2[i - 1:i + 1, 1:3]]
            self.create_element(e_nodes, element_set=element_set)

            e_nodes = [center2[i - 1:i + 1, 0], center_line[i - 1:i + 1, 0], mid1[i - 1:i + 1, 1],
                       mid2[i - 1:i + 1, 1]]
            self.create_element(e_nodes, element_set=element_set)

        e_nodes = [mid1[1:3, 1:3], center2[1:3, 0], top1[:, 0]]
        self.create_element(e_nodes, element_set=element_set)

        e_nodes = [mid2[1:3, 1:3], center2[1:3, 0], top2[:, 0]]
        self.create_element(e_nodes, element_set=element_set)

        # creating the corners
        e_nodes = [corner[0, 0], center2[0:2, 0], mid1[0:2, 1:3], top1[0, 0]]
        self.create_element(e_nodes, element_set=element_set)

        e_nodes = [corner[0, 0], center2[0:2, 0], mid2[0:2, 1:3], top2[0, 0]]
        self.create_element(e_nodes, element_set=element_set)

        e_nodes = [corner[1, 0], center2[2:4, 0], mid1[2:4, 1:3], top1[1, 0]]
        self.create_element(e_nodes, element_set=element_set)

        e_nodes = [corner[1, 0], center2[2:4, 0], mid2[2:4, 1:3], top2[1, 0]]
        self.create_element(e_nodes, element_set=element_set)

        # Creating the large element
        e_nodes = [corner[:, 0], top1[:, 0], top2[:, 0], center2[1:3, 0]]
        self.create_element(e_nodes, element_set=element_set)

    def create_transition_cell_corner_out(self, transition_block, axis, element_set='', node_set=''):
        d1, d2, axis1, axis2, base1, base2, center_line = self._assign_bases_and_axes(axis, transition_block, node_set)

        mid1 = self.copy_node_plane(base1[1:3, 1:2], axis2, d2, node_set)
        mid2 = self.copy_node_plane(base2[1:3, 1:2], axis1, d1, node_set)

        edge1 = self.copy_node_plane(base1[0:4:3, 0:1], axis2, 3*d2, node_set)
        edge2 = self.copy_node_plane(base1[0:4:3, 0:1], axis1, 3*d1, node_set)

        center2 = self.copy_node_plane(mid2, axis2, 2*d2, node_set)
        corner = self.copy_node_plane(edge1, axis1, 3*d1, node_set)
        if axis == 'x':
            transition_block[0:4:3, -1, -1] = corner[:, 0]
        elif axis == 'y':
            transition_block[-1, 0:4:3, -1] = corner[:, 0]
        elif axis == 'z':
            transition_block[-1, -1, 0:4:3] = corner[:, 0]

        # create the base row
        for i in range(1, 4):
            e_nodes = [base1[i - 1:i + 1, 0:2], base2[i - 1:i + 1, 1], center_line[i - 1:i + 1, 0]]
            self.create_element(e_nodes, element_set=element_set)

        # create the mid sharp elements
        e_nodes = [base1[1:3, 1], mid1, center_line[1:3, 0], center2[:, 0]]
        self.create_element(e_nodes, element_set=element_set)
        e_nodes = [base2[1:3, 1], mid2, center_line[1:3, 0], center2[:, 0]]
        self.create_element(e_nodes, element_set=element_set)

        # creating the edge elements
        e_nodes = [base1[0:2, 1], edge1[0, 0], corner[0, 0], center2[0, 0], mid1[0, 0], center_line[0:2, 0]]
        self.create_element(e_nodes, element_set=element_set)
        e_nodes = [base2[0:2, 1], edge2[0, 0], corner[0, 0], center2[0, 0], mid2[0, 0], center_line[0:2, 0]]
        self.create_element(e_nodes, element_set=element_set)
        e_nodes = [base1[2:4, 1], edge1[1, 0], corner[1, 0], center2[1, 0], mid1[1, 0], center_line[2:4, 0]]
        self.create_element(e_nodes, element_set=element_set)
        e_nodes = [base2[2:4, 1], edge2[1, 0], corner[1, 0], center2[1, 0], mid2[1, 0], center_line[2:4, 0]]
        self.create_element(e_nodes, element_set=element_set)

        # creating the large plates
        e_nodes = [mid1, center2[:, 0], edge1, corner]
        self.create_element(e_nodes, element_set=element_set)

        e_nodes = [mid2, center2[:, 0], edge2, corner]
        self.create_element(e_nodes, element_set=element_set)

    @staticmethod
    def _refinement(ns, order):
        ns = np.array(ns)
        orders = (np.log(ns - 1)/np.log(3))
        max_order = int(np.min(orders))
        if order is None:
            return 1
        else:
            return max_order - order + 1

    def create_transition_plate(self, surf, axis, d=None, order=None, direction=1, element_set='', node_set=''):
        n2, n3 = surf.shape
        refinement = self._refinement([n2, n3], order)
        if refinement == 0:
            return surf
        i = 0

        if d is None:
            d = np.max([surf[1, 1].x - surf[0, 0].x,
                       surf[1, 0].y - surf[0, 0].y,
                       surf[1, 0].z - surf[0, 0].z])*direction
        elif d > 0 and direction == -1:
            d *= direction

        if axis == 'x':
            block = np.empty(shape=(4, n2, n3), dtype=object)
            block[0, :, :] = surf
            block[1, :, :] = self.copy_node_plane(block[0, :, :], 'x', d, node_set)
            block[3, ::3, ::3] = self.copy_node_plane(block[0, ::3, ::3], 'x', 3*d, node_set)
            while i + 3 < n2:
                j = 0
                while j + 3 < n3:
                    self.create_transition_cell(block[0:4, i:i + 4, j:j + 4], axis, element_set, node_set)
                    j += 3
                i += 3
            surf = block[-1, ::3, ::3]

        if axis == 'y':
            block = np.empty(shape=(n2, 4, n3), dtype=object)
            block[:, 0, :] = surf
            block[:, 1, :] = self.copy_node_plane(block[:, 0, :], 'y', d, node_set)
            block[3, ::3, ::3] = self.copy_node_plane(block[::3, 0, ::3], 'y', 3*d, node_set)
            for i in range(n2):
                for j in range(n3):
                    self.create_transition_cell(block[i:i + 4, 0:4, j:j + 4], axis, element_set, node_set)
            surf = block[::3, -1, ::3]
        if axis == 'z':
            block = np.empty(shape=(n2, n3, 4), dtype=object)
            block[:, :, 0] = surf
            block[:, :, 1] = self.copy_node_plane(block[:, :, 0], 'z', d, node_set)
            block[::3, ::3, 3] = self.copy_node_plane(block[::3, ::3, 0], 'z', 3*d, node_set)
            while i + 3 < n2:
                j = 0
                while j + 3 < n3:
                    self.create_transition_cell(block[i:i + 4, j:j + 4, 0:4], axis, element_set, node_set)
                    j += 3
                i += 3
            surf = block[::3, ::3, -1]

        return self.create_transition_plate(surf, axis, d=3*d, order=refinement, direction=direction,
                                            element_set=element_set,
                                            node_set=node_set)

    def create_transition_corner_out(self, node_line, axis1, axis2, axis3, d1=None, d2=None, order=None,
                                     element_set='', node_set=''):
        n1 = node_line.shape[0]
        refinement = self._refinement([n1], order)
        if refinement == 0:
            return node_line

        dir1 = -1 if axis1[0] == '-' else 1
        dir2 = -1 if axis2[0] == '-' else 1

        d = abs(getattr(node_line[1], axis3) - getattr(node_line[0], axis3))
        dvec = [d1, d2]
        for i, (ds, direction) in enumerate(zip(dvec, [dir1, dir2])):
            if ds is None:
                dvec[i] = d*direction
            elif ds > 0 and direction == -1:
                dvec[i] = ds*direction
        d1, d2 = dvec

        if axis3 == 'x':
            node_block = np.empty(shape=(n1, 4, 4), dtype=object)
            node_block[:, 0, 0] = node_line
            node_block[:, 0:1, 1] = self.copy_node_plane(node_block[:, 0:1, 0], 'y', d1, node_set)
            node_block[:, 1, 0:1] = self.copy_node_plane(node_block[:, 0:1, 0], 'z', d2, node_set)

            node_block[::3, 0:1, -1] = self.copy_node_plane(node_block[0:1, ::3, 0], 'z', 3*d2, node_set)
            node_block[::3, -1, 0:1] = self.copy_node_plane(node_block[0, ::3, 0:1], 'y', 3*d1, node_set)

            for i in range(0, n1 + 3, 3):
                self.create_transition_cell_corner_out(node_block[i:i + 4, :, :], 'x', element_set, node_set)
            node_line = node_block[::3, -1, -1]

        if axis3 == 'y':
            node_block = np.empty(shape=(4, n1, 4), dtype=object)
            node_block[0, :, 0] = node_line
            node_block[0:1, :, 1] = self.copy_node_plane(node_block[0:1, :, 0], 'z', d2, node_set)
            node_block[1, :, 0:1] = self.copy_node_plane(node_block[0, :, 0:1], 'x', d1, node_set)

            node_block[0:1, ::3, -1] = self.copy_node_plane(node_block[0:1, ::3, 0], 'z', 3*d2, node_set)
            node_block[-1, ::3, 0:1] = self.copy_node_plane(node_block[0, ::3, 0:1], 'x', 3*d1, node_set)
            for i in range(0, n1 - 1, 3):
                self.create_transition_cell_corner_out(node_block[:, i:i + 4, :], 'y', element_set, node_set)
            node_line = node_block[-1, ::3, -1]

        if axis3 == 'z':
            node_block = np.empty(shape=(4, 4, n1), dtype=object)
            node_block[0, 0, :] = node_line
            node_block[0:1, 1, :] = self.copy_node_plane(node_block[0:1, 0, :], 'x', d1, node_set)
            node_block[1, 0:1, :] = self.copy_node_plane(node_block[0:1, 0, :], 'y', d2, node_set)

            node_block[0:1, -1, ::3] = self.copy_node_plane(node_block[0:1, ::3, 0], 'x', 3*d1, node_set)
            node_block[-1, 0:1, ::3] = self.copy_node_plane(node_block[0, ::3, 0:1], 'y', 3*d2, node_set)

            for i in range(0, n1, 3):
                self.create_transition_cell_corner_out(node_block[:, :, i:i + 4], 'z', element_set, node_set)
            node_line = node_block[-1, -1, ::3]
        return self.create_transition_corner_out(node_line, axis1, axis2, axis3, 3*d1, 3*d2, refinement,
                                                 element_set, node_set)

    def create_transition_corner_out_2d(self, node_line_1, node_line_2, element_set='', node_set=''):

        node_block = np.empty(shape=(4, 4, 1), dtype=object)
        node_block[0, 0, 0] = node_line_1[0]
        node_block[1, 0, 0] = node_line_1[1]
        node_block[3, 0, 0] = node_line_1[2]

        node_block[0, 1, 0] = node_line_2[1]
        node_block[0, 3, 0] = node_line_2[2]

        node_block[1, 1, 0] = self.create_node(node_block[1, 0, 0].x, node_block[0, 1, 0].y, 0, node_set)
        node_block[3, 3, 0] = self.create_node(node_block[3, 0, 0].x, node_block[0, 3, 0].y, 0, node_set)

        self.create_element([node_block[0, 0, 0], node_block[0, 1, 0], node_block[1, 0, 0], node_block[1, 1, 0]],
                            element_set=element_set, element_type='CAX4')
        self.create_element([node_block[1, 0, 0], node_block[1, 1, 0], node_block[3, 0, 0], node_block[3, 3, 0]],
                            element_set=element_set, element_type='CAX4')
        self.create_element([node_block[0, 1, 0], node_block[0, 3, 0], node_block[3, 3, 0], node_block[1, 1, 0]],
                            element_set=element_set, element_type='CAX4')

    def create_transition_corner(self, surf1, surf2, element_set='', node_set='', order=1):
        nx = surf1.shape[0]
        ny = surf1.shape[1]
        nz = surf2.shape[1]

        nodes_plate = np.empty(shape=(nx, ny, nz), dtype=object)
        nodes_plate[:, :, 0] = surf1
        nodes_plate[0, :, :] = surf2

        if (nx - 1)/3**order == 0 or (ny - 1)/3**order == 0 or (nz - 1)/3**order == 0:
            for i in range(1, nx):
                dx = nodes_plate[i, 0, 0].x - nodes_plate[0, 0, 0].x

                nodes_plate[i, :, :] = self.copy_node_plane(nodes_plate[0, :, :], 'x', dx, node_set)
                for j in range(1, ny):
                    for k in range(1, nz):
                        e_nodes = nodes_plate[i - 1:i + 1, j - 1:j + 1, k - 1:k + 1]
                        self.create_element(e_nodes, element_set=element_set)
            return

        # Create the first layer in z-direction
        distance = nodes_plate[3, 0, 0].x - nodes_plate[0, 0, 0].x
        k = 0
        i = 0
        while i + 1 < ny:
            transition_block = nodes_plate[0:4, i:i + 4, 0:4]
            self.create_transition_cell_corner(transition_block, 'y', element_set=element_set)
            i += 3

        i = 3
        while i + 3 < nx:
            j = 0
            while j + 3 < ny:
                # creating the 4 upper nodes
                corner_nodes = nodes_plate[i:i + 4:3, j:j + 4:3, k]
                nodes_plate[i:(i + 4):3, j:(j + 4):3, k + 3] = self.copy_node_plane(corner_nodes, 'z',
                                                                                    -distance, node_set)
                transition_block = nodes_plate[i:i + 4, j:j + 4, k:k + 4]
                self.create_transition_cell(transition_block, 'z', element_set=element_set, node_set=node_set)
                j += 3
            i += 3

        # Create the first layer in y-direction
        i = 3
        k = 0
        while i + 3 < nz:
            j = 0
            while j + 3 < ny:
                # creating the 4 upper nodes
                corner_nodes = nodes_plate[k, j:j + 4:3, i:i + 4:3]
                nodes_plate[k + 3, j:(j + 4):3, i:(i + 4):3] = self.copy_node_plane(corner_nodes, 'x',
                                                                                    distance, node_set)
                transition_block = nodes_plate[k:k + 4, j:j + 4, i:i + 4]
                self.create_transition_cell(transition_block, 'x', element_set=element_set, node_set=node_set)
                j += 3
            i += 3
        
        surf1 = nodes_plate[3::3, ::3, 3]
        surf2 = nodes_plate[3, ::3, 3::3]

        return self.create_transition_corner(surf1, surf2, element_set=element_set, node_set=node_set, order=order)

    def create_2d_transition(self, axis1, axis2, axis3, x0, y0, z0, d1, d2, d3, element_set='', node_set=''):
        # assume that axis1 is x, 2 is y, z is 3
        nodes = np.empty(shape=(2, 4, 4), dtype=object)

        # creating the base plate
        for i in range(2):
            for j in range(4):
                nodes[i, j, 0] = self.create_node(d1*i, d2*j, 0, node_set)
                nodes[i, j, 1] = self.create_node(d1*i, d2*j, d3, node_set)
            nodes[i, 1, 2] = self.create_node(d1*i, d2, 2*d3, node_set)
            nodes[i, 2, 2] = self.create_node(d1*i, 2*d2, 2*d3, node_set)
            nodes[i, 0, 3] = self.create_node(d1*i, 0, 3*d3, node_set)
            nodes[i, 3, 3] = self.create_node(d1*i, 3*d2, 3*d3, node_set)

        for i in range(2):
            for j in range(4):
                for k in range(4):
                    if nodes[i, j, k] is not None:
                        n = nodes[i, j, k]
                        x, y, z = n.x, n.y, n.z
                        setattr(n, axis1, x)
                        setattr(n, axis2, y)
                        setattr(n, axis3, z)

        for n in nodes.flatten().flatten().flatten():
            if n is not None:
                n.x += x0
                n.y += y0
                n.z += z0

        # create the base layer
        for i in range(1, 4):
            e_nodes = nodes[:, i - 1:i + 1, 0:2]
            self.create_element(e_nodes, element_set=element_set)

        # the center element
        e_nodes = nodes[:, 1:3, 1:3]
        self.create_element(e_nodes, element_set=element_set)

        # create the corner elements
        e_nodes = [nodes[:, 0, 1:4:2], nodes[:, 1, 1:3]]
        self.create_element(e_nodes, element_set=element_set)
        e_nodes = [nodes[:, 3, 1:4:2], nodes[:, 2, 1:3]]
        self.create_element(e_nodes, element_set=element_set)

        # create the top element
        e_nodes = [nodes[:, 1:3, 2], nodes[:, 0:4:3, 3]]
        self.create_element(e_nodes, element_set=element_set)

    def create_2d_transition_axi(self, axis1, axis2, axis3, x0, y0, z0, d1, d2, d3, element_set='', node_set=''):
        # assume that axis1 is x, 2 is y, z is 3
        nodes = np.empty(shape=(1, 4, 4), dtype=object)

        # creating the base plate
        for i in range(1):
            for j in range(4):
                nodes[i, j, 0] = self.create_node(d1*i, d2*j, 0, node_set)
                nodes[i, j, 1] = self.create_node(d1*i, d2*j, d3, node_set)
            nodes[i, 1, 2] = self.create_node(d1*i, d2, 2*d3, node_set)
            nodes[i, 2, 2] = self.create_node(d1*i, 2*d2, 2*d3, node_set)
            nodes[i, 0, 3] = self.create_node(d1*i, 0, 3*d3, node_set)
            nodes[i, 3, 3] = self.create_node(d1*i, 3*d2, 3*d3, node_set)

        for i in range(1):
            for j in range(4):
                for k in range(4):
                    if nodes[i, j, k] is not None:
                        n = nodes[i, j, k]
                        x, y, z = n.x, n.y, n.z
                        setattr(n, axis1, x)
                        setattr(n, axis2, y)
                        setattr(n, axis3, z)

        for n in nodes.flatten().flatten().flatten():
            if n is not None:
                n.x += x0
                n.y += y0
                n.z += z0

        # create the base layer
        for i in range(1, 4):
            e_nodes = nodes[:, i - 1:i + 1, 0:2]
            self.create_element(e_nodes, element_set=element_set, element_type='CAX4')

        # the center element
        e_nodes = nodes[:, 1:3, 1:3]
        self.create_element(e_nodes, element_set=element_set, element_type='CAX4')

        # create the corner elements
        e_nodes = [nodes[:, 0, 1:4:2], nodes[:, 1, 1:3]]
        self.create_element(e_nodes, element_set=element_set, element_type='CAX4')
        e_nodes = [nodes[:, 3, 1:4:2], nodes[:, 2, 1:3]]
        self.create_element(e_nodes, element_set=element_set, element_type='CAX4')

        # create the top element
        e_nodes = [nodes[:, 1:3, 2], nodes[:, 0:4:3, 3]]
        self.create_element(e_nodes, element_set=element_set, element_type='CAX4')

    def number_of_elements(self):
        return len(self.elements)

    def number_of_nodes(self):
        return len(self.nodes)

    def lists_for_part(self):
        node_ids = []
        coords = []
        for label, n in self.nodes.iteritems():
            node_ids.append(label)
            coords.append([n.x, n.y, n.z])
        e_data = []
        for element_type in self.elements.keys():
            element_ids = []
            conn = []
            for e in self.elements[element_type]:
                element_ids.append(e.label)
                conn.append([n.label for n in e.nodes])
            e_data.append([element_type, element_ids, conn])
        return [node_ids, coords], e_data

    def copy_element_set(self, old_set, new_set, node_set='', axis_order='xyz'):
        elements = self.element_sets[old_set]
        for e in elements:
            e_nodes = []
            for n in e.nodes:
                x, y, z = getattr(n, axis_order[0]), getattr(n, axis_order[1]), getattr(n, axis_order[2])
                e_nodes.append(self.create_node(x, y, z, node_set))
            self.create_element(e_nodes, element_type=e.element_type, element_set=new_set)

    def add_to_node_set(self, nodes, node_set):
        if isinstance(nodes, np.ndarray):
            while len(nodes.shape) > 1:
                nodes = nodes.flatten()

        if node_set not in self.node_sets:
            self.node_sets[node_set] = set()
        for n in nodes:
            self.node_sets[node_set].add(n)

    def get_bounding_box(self):
        x_min = 1E99
        x_max = -1E99
        y_min = 1E99
        y_max = -1E99
        z_min = 1E99
        z_max = -1E99
        for _, n in self.nodes.iteritems():
            x_min = min(x_min, n.x)
            y_min = min(y_min, n.y)
            z_min = min(z_min, n.z)

            x_max = max(x_max, n.x)
            y_max = max(y_max, n.y)
            z_max = max(z_max, n.z)
        return x_min, x_max, y_min, y_max, z_min, z_max

    def get_nodes_by_bounding_box(self, x_min=-1E88, x_max=1E88, y_min=-1E88, y_max=1E88,
                                  z_min=-1E88, z_max=1E88, node_set=None):
        nodes = []
        if node_set:
            node_list = self.node_sets[node_set]
        else:
            node_list = self.nodes.itervalues()
        for n in node_list:
            if x_min <= n.x <= x_max:
                if y_min <= n.y <= y_max:
                    if z_min <= n.z <= z_max:
                        nodes.append(n)
        return nodes

    def get_elements_by_bounding_box(self, x_min=-1E88, x_max=1E88, y_min=-1E88, y_max=1E88,
                                     z_min=-1E88, z_max=1E88, element_set=None):
        elements = set()
        if element_set:
            element_list = self.element_sets[element_set]
        else:
            element_list = []
            for e_list in self.elements.values():
                element_list += e_list

        for e in element_list:
            bbox = e.get_bounding_box()
            if bbox[0] < x_max and bbox[1] > x_min:
                if bbox[2] < y_max and bbox[3] > y_min:
                    if bbox[4] < z_max and bbox[5] > z_min:
                        elements.add(e)
        return elements
