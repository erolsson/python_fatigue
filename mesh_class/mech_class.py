from math import atan2, sqrt


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
        self.eType = element_type
        # sort nodes according to angles
        # sort by angle in the x-z plane
        x0 = sum([n.x for n in nodes]) / len(nodes)
        y0 = sum([n.y for n in nodes]) / len(nodes)
        z0 = sum([n.z for n in nodes]) / len(nodes)

        nodes = sorted(nodes, key=lambda n: atan2(n.z - z0, sqrt((n.x - x0) ** 2 + (n.y - y0) ** 2)))

        # sorting each z-plane
        nodes = []
        for i in range(2):

            if element_type[3] == '8':
                planeNodes = nodes[4 * i:4 * (i + 1)]

            elif element_type[3] == '6':
                planeNodes = nodes[3 * i:3 * (i + 1)]
            x0 = sum([n.x for n in planeNodes]) / len(planeNodes)
            y0 = sum([n.y for n in planeNodes]) / len(planeNodes)
            nodes += sorted(planeNodes, key=lambda n: atan2(n.y - y0, n.x - x0))
        self.nodes = nodes