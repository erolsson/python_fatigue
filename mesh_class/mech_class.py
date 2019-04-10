from math import atan2, sqrt

import numpy as np


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
        self.id = label
        self.element_type = element_type

        if element_type[1] == '3':
            dim = 3
        else:
            dim = 2
        e_nodes = []
        for i in range(dim - 1):
            if element_type[3] == '8':
                plane_nodes = nodes[4*i:4*(i + 1)]

            elif element_type[3] == '6':
                plane_nodes = nodes[3*i:3*(i + 1)]
            else:
                raise NotImplementedError("Mesh class currently doesnt support " + element_type)

            x0 = sum([node.x for node in plane_nodes])/len(plane_nodes)
            y0 = sum([node.y for node in plane_nodes])/len(plane_nodes)
            e_nodes += sorted(plane_nodes, key=lambda n: atan2(n.y - y0, n.x - x0))
        self.nodes = e_nodes


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
                self.node_sets[node_set].append(n)
            else:
                self.node_sets[node_set] = [n]
        return n

    # def coordinates(self):
    #    return self.x, self.y, self.z

    def create_element(self, nodes, element_type='C3D8R', element_set=None, label=None):
        if label is None:
            e = Element(self.element_counter, nodes, element_type)
        else:
            e = Element(label, nodes, element_type)
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
        new_nodes = np.empty(shape=(nx, ny), dtype=object)
        for i in range(nx):
            for j in range(ny):
                if axis == 'x':
                    new_nodes[i, j] = self.create_node(nodes[i, j].x + distance, nodes[i, j].y, nodes[i, j].z,
                                                       node_set=node_set)
                elif axis == 'y':
                    new_nodes[i, j] = self.create_node(nodes[i, j].x, nodes[i, j].y + distance, nodes[i, j].z,
                                                       node_set=node_set)
                elif axis == 'z':
                    new_nodes[i, j] = self.create_node(nodes[i, j].x, nodes[i, j].y, nodes[i, j].z + distance,
                                                       node_set=node_set)
        return new_nodes

    def createBlock(self, nx, ny, nz, dx, dy, dz, x0=0, y0=0, z0=0,
                    xNeg=None, xPos=None, yNeg=None, yPos=None, zNeg=None, zPos=None, nSet='', eSet=''):
        nodesPlate = np.empty(shape=((nx, ny, nz)), dtype=object)
        elementsPlate = []

        if xNeg is not None:
            nodesPlate[0, :, :] = xNeg
            ny, nz = xNeg.shape
            dy = xNeg[1, 0].y - xNeg[0, 0].y
            dz = xNeg[0, 1].z - xNeg[0, 0].z
            x0 = xNeg[0, 0].x

        if xPos is not None:
            nodesPlate[-1, :, :] = xPos

        if yNeg is not None:
            nodesPlate[:, 0, :] = yNeg
            nx, nz = yNeg.shape

            dx = yNeg[1, 0].x - yNeg[0, 0].x
            dz = yNeg[0, 1].z - yNeg[0, 0].z
            y0 = yNeg[0, 0].y

        if zNeg is not None:
            nodesPlate[:, :, 0] = zNeg
            nx, ny = zNeg.shape

            dx = zNeg[1, 0].x - zNeg[0, 0].x
            dy = zNeg[0, 1].y - zNeg[0, 0].y
            z0 = zNeg[0, 0].z

        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    if nodesPlate[i, j, k] is None:
                        nodesPlate[i, j, k] = self.create_node(i*dx + x0, j*dy + y0, k*dz + z0, node_set=nSet)
                    if i > 0 and j > 0 and k > 0:
                        eNodes = [nodesPlate[i - 1, j - 1, k - 1], nodesPlate[i, j - 1, k - 1],
                                  nodesPlate[i - 1, j - 1, k], nodesPlate[i, j - 1, k],
                                  nodesPlate[i - 1, j, k - 1], nodesPlate[i, j, k - 1],
                                  nodesPlate[i - 1, j, k], nodesPlate[i, j, k]]
                        elementsPlate.append(self.create_element(eNodes, element_set=eSet))
        return nodesPlate, elementsPlate

    def createBlockAxi(self, nx, ny, nz, dx, dy, dz, x0=0, y0=0, z0=0,
                       xNeg=None, xPos=None, yNeg=None, yPos=None, zNeg=None, zPos=None, nSet='', eSet=''):
        nodesPlate = np.empty(shape=((nx, ny, nz)), dtype=object)
        elementsPlate = []

        if xNeg is not None:
            nodesPlate[0, :, :] = xNeg
            ny, nz = xNeg.shape
            dy = xNeg[1, 0].y - xNeg[0, 0].y
            dz = xNeg[0, 1].z - xNeg[0, 0].z
            x0 = xNeg[0, 0].x

        if xPos is not None:
            nodesPlate[-1, :, :] = xPos

        if yNeg is not None:
            nodesPlate[:, 0, :] = yNeg
            nx, nz = yNeg.shape

            dx = yNeg[1, 0].x - yNeg[0, 0].x
            dz = yNeg[0, 1].z - yNeg[0, 0].z
            y0 = yNeg[0, 0].y

        if zNeg is not None:
            nodesPlate[:, :, 0] = zNeg
            nx, ny = zNeg.shape

            dx = zNeg[1, 0].x - zNeg[0, 0].x
            dy = zNeg[0, 1].y - zNeg[0, 0].y
            z0 = zNeg[0, 0].z

        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    if nodesPlate[i, j, k] is None:
                        nodesPlate[i, j, k] = self.create_node(i*dx + x0, j*dy + y0, k*dz + z0, node_set=nSet)
                    if i > 0 and j > 0 and k > 0:
                        eNodes = [nodesPlate[i - 1, j - 1, k - 1], nodesPlate[i, j - 1, k - 1],
                                  nodesPlate[i - 1, j, k - 1], nodesPlate[i, j, k - 1]]
                        elementsPlate.append(self.create_element(eNodes, element_set=eSet, element_type='CAX4'))
        return nodesPlate, elementsPlate

    def transformSqureToCylinder(self, nodeSet, rotAxis, radialAxis, angle, bias=False, f=1):
        nodes = self.node_sets[nodeSet]
        Rmax = 0
        yMax = 0
        if bias:
            for n in nodes:
                if radialAxis == 'x':
                    Rmax = max(Rmax, n.x)
                    yMax = max(yMax, n.y)
                if radialAxis == 'y':
                    Rmax = max(Rmax, n.y)
                if radialAxis == 'z':
                    Rmax = max(Rmax, n.z)

        for n in nodes:
            if rotAxis == 'z':
                z = n.z
            if radialAxis == 'x' and n.x > 0 and n.y > 0:
                if n.x > n.y:
                    r = n.x
                    q = n.y/n.x*angle/2
                    dx = r*cos(q) - n.x
                    dy = r*sin(q) - n.y
                else:
                    r = n.y
                    q = n.x/n.y*angle/2
                    dy = r*cos(q) - n.y
                    dx = r*sin(q) - n.x
                k = r/Rmax
                n.x += dx*k**0.75
                n.y += dy*k**0.75

    def transformSqureToSector(self, nodeSet, rotAxis, radialAxis, angle, bias=False, f=1):
        nodes = self.node_sets[nodeSet]
        Rmax = 0
        yMax = 0
        if bias:
            for n in nodes:
                if radialAxis == 'x':
                    Rmax = max(Rmax, n.x)
                    yMax = max(yMax, n.y)
                if radialAxis == 'y':
                    Rmax = max(Rmax, n.y)
                if radialAxis == 'z':
                    Rmax = max(Rmax, n.z)

        for n in nodes:
            if rotAxis == 'z':
                z = n.z
            if radialAxis == 'x':
                if n.x > n.y:
                    r = n.x
                    if n.x > 0:
                        q = n.y/n.x*angle/2
                    else:
                        q = 0
                    dx = r*cos(q) - n.x
                    dy = r*sin(q) - n.y
                else:

                    r = n.y
                    if n.y > 0:
                        q = n.x/n.y*angle/2 + (pi/2 - angle)
                    else:
                        q = 0
                    dy = r*cos(q) - n.y
                    dx = r*sin(q) - n.x
                n.x += dx
                n.y += dy

    def sweepBlock(self, nodeSet, rotAxis, radialAxis, angle):
        nodes = self.node_sets[nodeSet]
        Rmax = 0
        yMax = 0
        for n in nodes:
            if radialAxis == 'x':
                Rmax = max(Rmax, n.x)
                yMax = max(yMax, n.y)
            if radialAxis == 'y':
                Rmax = max(Rmax, n.y)
                yMax = max(yMax, n.x)
            if radialAxis == 'z':
                Rmax = max(Rmax, n.z)

        for n in nodes:
            if rotAxis == 'z':
                z = n.z

            if radialAxis == 'x':
                r = abs(n.x)
                if abs(n.x) > 0:
                    q = n.y/yMax*angle
                else:
                    q = pi/2
                dx = r*cos(q) - n.x
                dy = r*sin(q) - n.y

            if radialAxis == 'y':
                r = abs(n.y)
                if abs(n.y) > 0:
                    q = n.x/yMax*angle
                else:
                    q = pi/2
                dy = r*cos(q) - n.y
                dx = r*sin(q) - n.x
            n.x += dx
            n.y += dy

    def findElementNodesCube(self, nodes, x, y, z):
        eNodes = []
        for i in [0, 1]:
            for j in [0, 1]:
                for k in [0, 1]:
                    eNodes.append(nodes[x + i, y + j, z + k])
        return eNodes

    def createTransitionCell(self, transitionBlock, axis, eSet='', nSet=''):
        # The mid element
        if axis == 'x':
            d = (transitionBlock[-1, 0, 0].x - transitionBlock[0, 0, 0].x)/3
            basePlate = transitionBlock[0, :, :]
            topNodes = transitionBlock[3, 0:4:3, 0:4:3]
        elif axis == 'y':
            d = (transitionBlock[0, -1, 0].y - transitionBlock[0, 0, 0].y)/3
            basePlate = transitionBlock[:, 0, :]
            topNodes = transitionBlock[0:4:3, 3, 0:4:3]
        elif axis == 'z':
            d = (transitionBlock[0, 0, -1].z - transitionBlock[0, 0, 0].z)/3
            basePlate = transitionBlock[:, :, 0]
            topNodes = transitionBlock[0:4:3, 0:4:3, 3]
        secondPlate = self.copy_node_plane(basePlate, axis, d, nSet)
        centerPlate = self.copy_node_plane(basePlate[1:3, 1:3], axis, 3*d/2, nSet)
        midPlateX = self.copy_node_plane(basePlate[1:3, 0:4:3], axis, 2*d, nSet)
        midPlateY = self.copy_node_plane(basePlate[0:4:3, 1:3], axis, 2*d, nSet)

        # Create the base plate
        nx, ny = basePlate.shape
        for i in range(1, nx):
            for j in range(1, ny):
                eNodes = basePlate[i - 1:i + 1, j - 1:j + 1].flatten().tolist()
                eNodes = eNodes + secondPlate[i - 1:i + 1, j - 1:j + 1].flatten().tolist()
                self.create_element(eNodes, element_set=eSet)

        # Create the center element
        eNodes = secondPlate[1:3, 1:3].flatten().tolist() + centerPlate.flatten().tolist()
        self.create_element(eNodes, element_set=eSet)

        # Create the side elements in the "+"
        for i in range(2):
            eNodes1 = midPlateX[:, i].tolist() + centerPlate[:, i].tolist() + secondPlate[1:3,
                                                                              2*i:2*i + 2].flatten().tolist()
            eNodes2 = midPlateY[i, :].tolist() + centerPlate[i, :].tolist() + secondPlate[2*i:2*i + 2,
                                                                              1:3].flatten().tolist()
            self.create_element(eNodes1, element_set=eSet)
            self.create_element(eNodes2, element_set=eSet)

        # Create the corner elements
        for i in range(2):
            for j in range(2):
                eNodes = ([topNodes[i, j]] + secondPlate[2*i:2*i + 2, 2*j:2*j + 2].flatten().tolist() + [
                    centerPlate[i, j]] +
                          [midPlateX[i, j]] + [midPlateY[i, j]])
                self.create_element(eNodes, element_set=eSet)

        # Create the "small" center element
        eNodes = midPlateX.flatten().tolist() + centerPlate.flatten().tolist()
        self.create_element(eNodes, element_set=eSet)

        # Create the side skewed elements
        for i in range(2):
            eNodes = midPlateY[i, :].tolist() + topNodes[i, :].tolist() + centerPlate[i, :].tolist() + midPlateX[i,
                                                                                                       :].tolist()
            self.create_element(eNodes, element_set=eSet)

        # create the top element
        eNodes = topNodes.flatten().tolist() + midPlateX.flatten().tolist()
        self.create_element(eNodes, element_set=eSet)

    def createTransitionCellCorner(self, transitionBlock, axis, eSet='', nSet=''):
        if axis == 'x':
            d1 = (transitionBlock[0, -1, 0].y - transitionBlock[0, 0, 0].y)/3
            d2 = (transitionBlock[0, 0, -1].z - transitionBlock[0, 0, 0].z)/3
            axis1, axis2 = 'y', 'z'
            base1 = transitionBlock[:, :, 0]
            base2 = transitionBlock[:, 0, :]
            centerLine = self.copy_node_plane(transitionBlock[:, 1:2, 0], 'z', d1, nSet)
        elif axis == 'y':
            d1 = (transitionBlock[-1, 0, 0].x - transitionBlock[0, 0, 0].x)/3
            d2 = (transitionBlock[0, 0, -1].z - transitionBlock[0, 0, 0].z)/3
            axis1, axis2 = 'x', 'z'
            base1 = transitionBlock[0, :, :]
            base2 = transitionBlock[:, :, 0].transpose()
            centerLine = self.copy_node_plane(transitionBlock[0, :, 1:2], 'x', d1, nSet)

        elif axis == 'z':
            axis1, axis2 = 'x', 'y'
            d1 = (transitionBlock[-1, 0, 0].x - transitionBlock[0, 0, 0].x)/3
            d2 = (transitionBlock[0, -1, 0].y - transitionBlock[0, 0, 0].y)/3
            base1 = transitionBlock[0, :, :].transpose()
            base2 = transitionBlock[:, 0, :].transpose()
            centerLine = self.copy_node_plane(transitionBlock[1:2, 0, :], 'y', d1, nSet).transpose()

        mid1 = self.copy_node_plane(base1[:, 1:], axis1, d1, nSet)
        mid2 = self.copy_node_plane(base2[:, 1:], axis2, d2, nSet)

        top1 = self.copy_node_plane(base1[1:3, 3:], axis1, 2*d1, nSet)
        top2 = self.copy_node_plane(base2[1:3, 3:], axis2, 2*d2, nSet)

        center2 = self.copy_node_plane(base1[0:4, 2:], axis1, 2*d1, nSet)

        corner = self.copy_node_plane(base1[0:4:3, 3:], axis1, 3*d1, nSet)

        # create the base plates
        for i in range(1, 4):
            eNodes = (base1[i - 1:i + 1, 0:2].flatten().tolist() + base2[i - 1:i + 1, 1].tolist()
                      + centerLine[i - 1:i + 1, 0].tolist())
            self.create_element(eNodes, element_set=eSet)

            eNodes = (base1[i - 1:i + 1, 1:3].flatten().tolist() + mid1[i - 1:i + 1, 1].tolist()
                      + centerLine[i - 1:i + 1, 0].tolist())
            self.create_element(eNodes, element_set=eSet)

            eNodes = (base2[i - 1:i + 1, 1:3].flatten().tolist() + mid2[i - 1:i + 1, 1].tolist()
                      + centerLine[i - 1:i + 1, 0].tolist())
            self.create_element(eNodes, element_set=eSet)

            eNodes = base1[i - 1:i + 1, 2:4].flatten().tolist() + mid1[i - 1:i + 1, 1:3].flatten().tolist()
            self.create_element(eNodes, element_set=eSet)

            eNodes = base2[i - 1:i + 1, 2:4].flatten().tolist() + mid2[i - 1:i + 1, 1:3].flatten().tolist()
            self.create_element(eNodes, element_set=eSet)

            eNodes = (center2[i - 1:i + 1, 0].tolist() + centerLine[i - 1:i + 1, 0].tolist() +
                      mid1[i - 1:i + 1, 1].tolist() + mid2[i - 1:i + 1, 1].tolist())
            self.create_element(eNodes, element_set=eSet)

        eNodes = mid1[1:3, 1:3].flatten().tolist() + center2[1:3, 0].tolist() + top1[:, 0].tolist()
        self.create_element(eNodes, element_set=eSet)

        eNodes = mid2[1:3, 1:3].flatten().tolist() + center2[1:3, 0].tolist() + top2[:, 0].tolist()
        self.create_element(eNodes, element_set=eSet)

        # creating the corners
        eNodes = ([corner[0, 0]] + center2[0:2, 0].tolist() + mid1[0:2, 1:3].flatten().tolist() +
                  [top1[0, 0]])
        self.create_element(eNodes, element_set=eSet)

        eNodes = ([corner[0, 0]] + center2[0:2, 0].tolist() + mid2[0:2, 1:3].flatten().tolist() +
                  [top2[0, 0]])
        self.create_element(eNodes, element_set=eSet)

        eNodes = ([corner[1, 0]] + center2[2:4, 0].tolist() + mid1[2:4, 1:3].flatten().tolist() +
                  [top1[1, 0]])
        self.create_element(eNodes, element_set=eSet)

        eNodes = ([corner[1, 0]] + center2[2:4, 0].tolist() + mid2[2:4, 1:3].flatten().tolist() +
                  [top2[1, 0]])
        self.create_element(eNodes, element_set=eSet)

        # Creating the large element
        eNodes = corner[:, 0].tolist() + top1[:, 0].tolist() + top2[:, 0].tolist() + center2[1:3, 0].tolist()
        self.create_element(eNodes, element_set=eSet)

    def createTransitionCellCornerOut(self, transitionBlock, axis, eSet='', nSet=''):
        if axis == 'x':
            d1 = (transitionBlock[0, -1, 0].y - transitionBlock[0, 0, 0].y)/3
            d2 = (transitionBlock[0, 0, -1].z - transitionBlock[0, 0, 0].z)/3
            axis1, axis2 = 'y', 'z'
            base1 = transitionBlock[:, 0:2, 0]
            base2 = transitionBlock[:, 0, 0:2]
            centerLine = self.copy_node_plane(transitionBlock[:, 1:2, 0], 'z', d1, nSet)

        elif axis == 'y':
            d1 = (transitionBlock[1, 0, 0].x - transitionBlock[0, 0, 0].x)
            d2 = (transitionBlock[0, 0, 1].z - transitionBlock[0, 0, 0].z)
            axis1, axis2 = 'x', 'z'
            base1 = transitionBlock[0, :, 0:2]
            base2 = transitionBlock[0:2, :, 0].transpose()
            centerLine = self.copy_node_plane(transitionBlock[0, :, 1:2], 'x', d1, nSet)

        elif axis == 'z':
            axis1, axis2 = 'x', 'y'
            d1 = (transitionBlock[-1, 0, 0].x - transitionBlock[0, 0, 0].x)/3
            d2 = (transitionBlock[0, -1, 0].y - transitionBlock[0, 0, 0].y)/3
            base1 = transitionBlock[0, 0:2, :].transpose()
            base2 = transitionBlock[0:2, 0, :].transpose()
            centerLine = self.copy_node_plane(transitionBlock[1:2, 0, :], 'y', d1, nSet).transpose()

        mid1 = self.copy_node_plane(base1[1:3, 1:2], axis2, d2, nSet)
        mid2 = self.copy_node_plane(base2[1:3, 1:2], axis1, d1, nSet)

        edge1 = self.copy_node_plane(base1[0:4:3, 0:1], axis2, 3*d2, nSet)
        edge2 = self.copy_node_plane(base1[0:4:3, 0:1], axis1, 3*d1, nSet)

        corner = self.copy_node_plane(edge1, axis1, 3*d1, nSet)

        center2 = self.copy_node_plane(mid2, axis2, 2*d2, nSet)
        corner = self.copy_node_plane(edge1, axis1, 3*d1, nSet)
        if axis == 'x':
            transitionBlock[0:4:3, -1, -1] = corner[:, 0]
        elif axis == 'y':
            transitionBlock[-1, 0:4:3, -1] = corner[:, 0]
        elif axis == 'z':
            transitionBlock[-1, -1, 0:4:3] = corner[:, 0]

        # create the base row
        for i in range(1, 4):
            eNodes = (base1[i - 1:i + 1, 0:2].flatten().tolist() + base2[i - 1:i + 1, 1].tolist()
                      + centerLine[i - 1:i + 1, 0].tolist())
            self.create_element(eNodes, element_set=eSet)

        # create the mid sharp elements
        eNodes = base1[1:3, 1].tolist() + mid1.flatten().tolist() + centerLine[1:3, 0].tolist() + center2[:, 0].tolist()
        self.create_element(eNodes, element_set=eSet)
        eNodes = base2[1:3, 1].tolist() + mid2.flatten().tolist() + centerLine[1:3, 0].tolist() + center2[:, 0].tolist()
        self.create_element(eNodes, element_set=eSet)

        # creating the edge elements
        eNodes = (base1[0:2, 1].tolist() + [edge1[0, 0], corner[0, 0], center2[0, 0], mid1[0, 0]] + centerLine[0:2,
                                                                                                    0].tolist())
        self.create_element(eNodes, element_set=eSet)
        eNodes = (base2[0:2, 1].tolist() + [edge2[0, 0], corner[0, 0], center2[0, 0], mid2[0, 0]] + centerLine[0:2,
                                                                                                    0].tolist())
        self.create_element(eNodes, element_set=eSet)

        eNodes = (base1[2:4, 1].tolist() + [edge1[1, 0], corner[1, 0], center2[1, 0], mid1[1, 0]] + centerLine[2:4,
                                                                                                    0].tolist())
        self.create_element(eNodes, element_set=eSet)
        eNodes = (base2[2:4, 1].tolist() + [edge2[1, 0], corner[1, 0], center2[1, 0], mid2[1, 0]] + centerLine[2:4,
                                                                                                    0].tolist())
        self.create_element(eNodes, element_set=eSet)

        # creating the large plates
        eNodes = mid1.flatten().tolist() + center2[:, 0].tolist() + edge1.flatten().tolist() + corner.flatten().tolist()
        self.create_element(eNodes, element_set=eSet)

        eNodes = mid2.flatten().tolist() + center2[:, 0].tolist() + edge2.flatten().tolist() + corner.flatten().tolist()
        self.create_element(eNodes, element_set=eSet)

    def createTransitionPlate(self, surf, axis, order=1, direction=1, eSet='', nSet=''):
        n2, n3 = surf.shape
        if (n2 - 1)/(3**order) == 0 or (n3 - 1)/(3**order) == 0:
            return
        i = 0
        if axis == 'x':
            block = np.empty(shape=((4, n2, n3)), dtype=object)
            block[0, :, :] = surf
            dx = abs(block[0, 0, 1].z - block[0, 0, 0].z)*direction
            block[1, :, :] = self.copy_node_plane(block[0, :, :], 'x', dx, nSet)
            block[3, ::3, ::3] = self.copy_node_plane(block[0, ::3, ::3], 'x', 3*dx, nSet)
            while i + 3 < n2:
                j = 0
                while j + 3 < n3:
                    self.createTransitionCell(block[0:4, i:i + 4, j:j + 4], axis, eSet, nSet)
                    j += 3
                i += 3
            surf = block[-1, ::3, ::3]

        if axis == 'y':
            block = np.empty(shape=((n2, 4, n3)), dtype=object)
            block[:, 0, :] = surf
            dy = abs(block[0, 0, 1].z - block[0, 0, 0].z)*direction
            block[:, 1, :] = self.copy_node_plane(block[:, 0, :], 'y', dy, nSet)
            for i in range(n2):
                for j in range(n3):
                    self.createTransitionCell(block[i:i + 4, 0:4, j:j + 4], axis, eSet, nSet)
            surf = block[::3, -1, ::3]
        if axis == 'z':
            block = np.empty(shape=((n2, n3, 4)), dtype=object)
            block[:, :, 0] = surf
            dz = abs(block[1, 0, 0].x - block[0, 0, 0].x)*direction
            block[:, :, 1] = self.copy_node_plane(block[:, :, 0], 'z', dz, nSet)

            block[::3, ::3, 3] = self.copy_node_plane(block[::3, ::3, 0], 'z', 3*dz, nSet)
            while i + 3 < n2:
                j = 0
                while j + 3 < n3:
                    self.createTransitionCell(block[i:i + 4, j:j + 4, 0:4], axis, eSet, nSet)
                    j += 3
                i += 3
            surf = block[::3, ::3, -1]

        return self.createTransitionPlate(surf, axis, order=order, direction=direction, eSet=eSet, nSet=nSet)

    def createTransitionCornerOut(self, nodeLine, axes1, axes2, axis3, order=1, eSet='', nSet=''):
        n1 = nodeLine.shape[0]
        if (n1 - 1)/(3**order) == 0:
            return nodeLine
        if len(axes1) == 2:
            dir1, axis1 = -1, axes1[-1]
        else:
            dir1 = 1
        if len(axes2) == 2:
            dir2, axis2 = -1, axes2[-1]
        else:
            dir2 = 1
        order2 = int((n1 - 1)**(1./3))
        if axis3 == 'x':
            d = abs(nodeLine[1].x - nodeLine[0].x)
            nodeBlock = np.empty(shape=((n1, 4, 4)), dtype=object)
            nodeBlock[:, 0, 0] = nodeLine
            nodeBlock[:, 0:1, 1] = self.copy_node_plane(nodeBlock[:, 0:1, 0], 'y', dir1*d, nSet)
            nodeBlock[:, 1, 0:1] = self.copy_node_plane(nodeBlock[:, 0:1, 0], 'z', dir2*d, nSet)
            for i in range(0, n1 + 3, 3):
                self.createTransitionCellCornerOut(nodeBlock[i:i + 4, :, :], 'x', eSet, nSet)
        if axis3 == 'y':
            d = abs(nodeLine[1].y - nodeLine[0].y)
            nodeBlock = np.empty(shape=((4, n1, 4)), dtype=object)
            nodeBlock[0, :, 0] = nodeLine
            nodeBlock[0:1, :, 1] = self.copy_node_plane(nodeBlock[0:1, :, 0], 'z', dir2*d, nSet)
            nodeBlock[1, :, 0:1] = self.copy_node_plane(nodeBlock[0, :, 0:1], 'x', dir1*d, nSet)

            nodeBlock[0:1, ::3, -1] = self.copy_node_plane(nodeBlock[0:1, ::3, 0], 'z', 3*dir2*d, nSet)
            nodeBlock[-1, ::3, 0:1] = self.copy_node_plane(nodeBlock[0, ::3, 0:1], 'x', 3*dir1*d, nSet)
            for i in range(0, n1 - 1, 3):
                self.createTransitionCellCornerOut(nodeBlock[:, i:i + 4, :], 'y', eSet, nSet)
            nodeLine = nodeBlock[-1, ::3, -1]
            return self.createTransitionCornerOut(nodeLine, axes1, axes2, axis3, order, eSet, nSet)

        if axis3 == 'z':
            d = abs(nodeLine[1].z - nodeLine[0].z)
            nodeBlock = np.empty(shape=((4, 4, n1)), dtype=object)
            nodeBlock[0, 0, :] = nodeLine
            nodeBlock[0:1, 1, :] = self.copy_node_plane(nodeBlock[0:1, 0, :], 'x', dir1*d, nSet)
            nodeBlock[1, 0:1, :] = self.copy_node_plane(nodeBlock[0:1, 0, :], 'y', dir2*d, nSet)
            for i in range(0, n1, 3):
                self.createTransitionCellCornerOut(nodeBlock[:, :, i:i + 4], 'z', eSet, nSet)

    def createTransitionCornerOut2D(self, node_line_1, node_line_2, eSet='', nSet=''):

        nodeBlock = np.empty(shape=((4, 4, 1)), dtype=object)
        nodeBlock[0, 0, 0] = node_line_1[0]
        nodeBlock[1, 0, 0] = node_line_1[1]
        nodeBlock[3, 0, 0] = node_line_1[2]

        nodeBlock[0, 1, 0] = node_line_2[1]
        nodeBlock[0, 3, 0] = node_line_2[2]
        dx = node_line_1[1].x - node_line_1[0].x
        dy = node_line_2[1].y - node_line_2[0].y

        nodeBlock[1, 1, 0] = self.create_node(nodeBlock[1, 0, 0].x, nodeBlock[0, 1, 0].y, 0, nSet)
        nodeBlock[3, 3, 0] = self.create_node(nodeBlock[3, 0, 0].x, nodeBlock[0, 3, 0].y, 0, nSet)

        self.create_element([nodeBlock[0, 0, 0], nodeBlock[0, 1, 0], nodeBlock[1, 0, 0], nodeBlock[1, 1, 0]],
                            element_set=eSet, element_type='CAX4')
        self.create_element([nodeBlock[1, 0, 0], nodeBlock[1, 1, 0], nodeBlock[3, 0, 0], nodeBlock[3, 3, 0]],
                            element_set=eSet, element_type='CAX4')
        self.create_element([nodeBlock[0, 1, 0], nodeBlock[0, 3, 0], nodeBlock[3, 3, 0], nodeBlock[1, 1, 0]],
                            element_set=eSet, element_type='CAX4')

    def createTransitionCorner(self, surf1, surf2, eSet='', nSet='', order=1):
        nx = surf1.shape[0]
        ny = surf1.shape[1]
        nz = surf2.shape[1]
        nodesPlate = np.empty(shape=((nx, ny, nz)), dtype=object)
        nodesPlate[:, :, 0] = surf1
        nodesPlate[0, :, :] = surf2

        if (nx - 1)/3**order == 0 or (ny - 1)/3**order == 0 or (nz - 1)/3**order == 0:
            for i in range(1, nx):
                dx = nodesPlate[i, 0, 0].x - nodesPlate[0, 0, 0].x

                nodesPlate[i, :, :] = self.copy_node_plane(nodesPlate[0, :, :], 'x', dx, nSet)
                for j in range(1, ny):
                    for k in range(1, nz):
                        eNodes = nodesPlate[i - 1:i + 1, j - 1:j + 1, k - 1:k + 1].flatten().tolist()
                        self.create_element(eNodes, element_set=eSet)
            return

            # Create the first layer in z-direction
        k = 0
        i = 3

        distance = nodesPlate[3, 0, 0].x - nodesPlate[0, 0, 0].x
        i = 0
        while i + 1 < ny:
            transitionBlock = nodesPlate[0:4, i:i + 4, 0:4]
            self.createTransitionCellCorner(transitionBlock, 'y', eSet=eSet)
            i += 3

        i = 3
        while i + 3 < nx:
            j = 0
            while j + 3 < ny:
                # creating the 4 upper nodes
                cornerNodes = nodesPlate[i:i + 4:3, j:j + 4:3, k]
                nodesPlate[i:(i + 4):3, j:(j + 4):3, k + 3] = self.copy_node_plane(cornerNodes,
                                                                                 'z',
                                                                                   -distance, nSet)
                transitionBlock = nodesPlate[i:i + 4, j:j + 4, k:k + 4]
                self.createTransitionCell(transitionBlock, 'z', eSet=eSet, nSet=nSet)
                j += 3
            i += 3

        # Create the first layer in y-direction
        i = 3
        k = 0
        while i + 3 < nz:
            j = 0
            while j + 3 < ny:
                # creating the 4 upper nodes
                cornerNodes = nodesPlate[k, j:j + 4:3, i:i + 4:3]
                nodesPlate[k + 3, j:(j + 4):3, i:(i + 4):3] = self.copy_node_plane(cornerNodes,
                                                                                 'x',
                                                                                   distance, nSet)
                transitionBlock = nodesPlate[k:k + 4, j:j + 4, i:i + 4]
                self.createTransitionCell(transitionBlock, 'x', eSet=eSet, nSet=nSet)
                j += 3
            i += 3

        surf1 = nodesPlate[3::3, ::3, 3]
        surf2 = nodesPlate[3, ::3, 3::3]
        return self.createTransitionCorner(surf1, surf2, eSet=eSet, nSet=nSet, order=order)

    def create2DTransition(self, axis1, axis2, axis3, x0, y0, z0, d1, d2, d3, eSet='', nSet=''):
        # assume that axis1 is x, 2 is y, z is 3
        nodes = np.empty(shape=((2, 4, 4)), dtype=object)

        # creating the base plate
        for i in range(2):
            for j in range(4):
                nodes[i, j, 0] = self.create_node(d1*i, d2*j, 0, nSet)
                nodes[i, j, 1] = self.create_node(d1*i, d2*j, d3, nSet)
            nodes[i, 1, 2] = self.create_node(d1*i, d2, 2*d3, nSet)
            nodes[i, 2, 2] = self.create_node(d1*i, 2*d2, 2*d3, nSet)
            nodes[i, 0, 3] = self.create_node(d1*i, 0, 3*d3, nSet)
            nodes[i, 3, 3] = self.create_node(d1*i, 3*d2, 3*d3, nSet)

        for i in range(2):
            for j in range(4):
                for k in range(4):
                    if nodes[i, j, k] is not None:
                        n = nodes[i, j, k]
                        x, y, z = n.x, n.y, n.z
                        if axis1 is not 'x':
                            if axis1 is 'y':
                                n.x = y
                            if axis1 is 'z':
                                n.x = z
                        if axis2 is not 'y':
                            if axis2 is 'x':
                                n.y = x
                            if axis2 is 'z':
                                n.y = z
                        if axis3 is not 'z':
                            if axis3 is 'x':
                                n.z = x
                            if axis3 is 'y':
                                n.z = y
        for n in nodes.flatten().flatten().flatten():
            if n is not None:
                n.x += x0
                n.y += y0
                n.z += z0

        # create the base layer
        for i in range(1, 4):
            eNodes = nodes[:, i - 1:i + 1, 0:2].flatten().flatten().tolist()
            self.create_element(eNodes, element_set=eSet)
        # the center element
        eNodes = nodes[:, 1:3, 1:3].flatten().flatten().tolist()
        self.create_element(eNodes, element_set=eSet)
        # create the corner elements
        eNodes = nodes[:, 0, 1:4:2].flatten().tolist() + nodes[:, 1, 1:3].flatten().tolist()
        self.create_element(eNodes, element_set=eSet)
        eNodes = nodes[:, 3, 1:4:2].flatten().tolist() + nodes[:, 2, 1:3].flatten().tolist()
        self.create_element(eNodes, element_set=eSet)
        # create the top element
        eNodes = nodes[:, 1:3, 2].flatten().flatten().tolist() + nodes[:, 0:4:3, 3].flatten().flatten().tolist()
        self.create_element(eNodes, element_set=eSet)

    def create2DTransitionAxi(self, axis1, axis2, axis3, x0, y0, z0, d1, d2, d3, eSet='', nSet=''):
        # assume that axis1 is x, 2 is y, z is 3
        nodes = np.empty(shape=((1, 4, 4)), dtype=object)

        # creating the base plate
        for i in range(1):
            for j in range(4):
                nodes[i, j, 0] = self.create_node(d1*i, d2*j, 0, nSet)
                nodes[i, j, 1] = self.create_node(d1*i, d2*j, d3, nSet)
            nodes[i, 1, 2] = self.create_node(d1*i, d2, 2*d3, nSet)
            nodes[i, 2, 2] = self.create_node(d1*i, 2*d2, 2*d3, nSet)
            nodes[i, 0, 3] = self.create_node(d1*i, 0, 3*d3, nSet)
            nodes[i, 3, 3] = self.create_node(d1*i, 3*d2, 3*d3, nSet)

        for i in range(1):
            for j in range(4):
                for k in range(4):
                    if nodes[i, j, k] is not None:
                        n = nodes[i, j, k]
                        x, y, z = n.x, n.y, n.z
                        if axis1 is not 'x':
                            if axis1 is 'y':
                                n.x = y
                            if axis1 is 'z':
                                n.x = z
                        if axis2 is not 'y':
                            if axis2 is 'x':
                                n.y = x
                            if axis2 is 'z':
                                n.y = z
                        if axis3 is not 'z':
                            if axis3 is 'x':
                                n.z = x
                            if axis3 is 'y':
                                n.z = y
        for n in nodes.flatten().flatten().flatten():
            if n is not None:
                n.x += x0
                n.y += y0
                n.z += z0

        # create the base layer
        for i in range(1, 4):
            eNodes = nodes[:, i - 1:i + 1, 0:2].flatten().flatten().tolist()
            self.create_element(eNodes, element_set=eSet, element_type='CAX4')
        # the center element
        eNodes = nodes[:, 1:3, 1:3].flatten().flatten().tolist()
        self.create_element(eNodes, element_set=eSet, element_type='CAX4')
        # create the corner elements
        eNodes = nodes[:, 0, 1:4:2].flatten().tolist() + nodes[:, 1, 1:3].flatten().tolist()
        self.create_element(eNodes, element_set=eSet, element_type='CAX4')
        eNodes = nodes[:, 3, 1:4:2].flatten().tolist() + nodes[:, 2, 1:3].flatten().tolist()
        self.create_element(eNodes, element_set=eSet, element_type='CAX4')
        # create the top element
        eNodes = nodes[:, 1:3, 2].flatten().flatten().tolist() + nodes[:, 0:4:3, 3].flatten().flatten().tolist()
        self.create_element(eNodes, element_set=eSet, element_type='CAX4')

    def noOfElements(self):
        return len(self.elements)

    def noOfNodes(self):
        return len(self.nodes)

    def listsForPart(self):
        nIDs = []
        coords = []
        for label, n in self.nodes.iteritems():
            nIDs.append(label)
            coords.append([n.x, n.y, n.z])
        eData = []
        for eType in self.elements.keys():
            eIDs = []
            conn = []
            for e in self.elements[eType]:
                eIDs.append(e.ID)
                conn.append([n.ID for n in e.nodes])
            eData.append([eType, eIDs, conn])
        return [nIDs, coords], eData

    def copyElementSet(self, oldSet, newSet, nSet='', axisOrder='xyz'):
        elements = self.element_sets[oldSet]
        for e in elements:
            eNodes = []
            for n in e.nodes:
                if axisOrder == 'xyz':
                    x, y, z = n.x, n.y, n.z
                if axisOrder == 'yzx':
                    x, y, z = n.y, n.z, n.x
                if axisOrder == 'zxy':
                    x, y, z = n.z, n.x, n.y

                if axisOrder == 'yxz':
                    x, y, z = n.y, n.x, n.z
                if axisOrder == 'xzy':
                    x, y, z = n.x, n.z, n.y
                if axisOrder == 'zyx':
                    x, y, z = n.z, n.y, n.x
                eNodes.append(self.create_node(x, y, z, nSet))
            self.create_element(eNodes, element_type=e.eType, element_set=newSet)

    def addToNodeSet(self, nodes, nodeSet):
        if type(nodes).__module__ is 'numpy':
            while len(nodes.shape) > 1:
                nodes = nodes.flatten()
        if not nodeSet in self.node_sets:
            self.node_sets[nodeSet] = []
        for n in nodes:
            self.node_sets[nodeSet].append(n)

    def getBoundingBox(self, nSet=''):
        xMin = 1E99
        xMax = -1E99
        yMin = 1E99
        yMax = -1E99
        zMin = 1E99
        zMax = -1E99
        for _, n in self.nodes.iteritems():
            xMin = min(xMin, n.x)
            yMin = min(yMin, n.y)
            zMin = min(zMin, n.z)

            xMax = max(xMax, n.x)
            yMax = max(yMax, n.y)
            zMax = max(zMax, n.z)
        return xMin, xMax, yMin, yMax, zMin, zMax

    def getNodesByBoundingBox(self, xMin=-1E88, xMax=1E88, yMin=-1E88, yMax=1E88,
                              zMin=-1E88, zMax=1E88, nSet=''):
        nodes = []
        if nSet == '':
            nodeList = self.nodes.iteritems()
            for _, n in nodeList:
                if n.x >= xMin and n.x <= xMax:
                    if n.y >= yMin and n.y <= yMax:
                        if n.z >= zMin and n.z <= zMax:
                            nodes.append(n)

        else:
            nodeList = self.node_sets[nSet]
            for n in nodeList:
                if n.x >= xMin and n.x <= xMax:
                    if n.y >= yMin and n.y <= yMax:
                        if n.z >= zMin and n.z <= zMax:
                            nodes.append(n)

        return nodes
