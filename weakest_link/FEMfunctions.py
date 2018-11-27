import numpy as np


class Element8:
    def __init__(self):
        self.pos = np.array([[-1, -1, -1],
                             [1, -1, -1],
                             [1, 1, -1],
                             [-1, 1, -1],
                             [-1, -1, 1],
                             [1, -1, 1],
                             [1, 1, 1],
                             [-1, 1, 1]])

    def N(self, x, y, z):
        shape_fcn = np.zeros(8)
        for i in range(8):
            shape_fcn[i] = (1.+x*self.pos[i, 0])*(1.+y*self.pos[i, 1])*(1.+z*self.pos[i, 2])/8
        return shape_fcn
    
    def d(self, x, y, z):
        d_matrix = np.zeros((3, 8))
        for i in range(8):
            d_matrix[0, i] = (1.+y*self.pos[i, 1])*(1.+z*self.pos[i, 2])*self.pos[i, 0]/8
            d_matrix[1, i] = (1.+x*self.pos[i, 0])*(1.+z*self.pos[i, 2])*self.pos[i, 1]/8
            d_matrix[2, i] = (1.+x*self.pos[i, 0])*(1.+y*self.pos[i, 1])*self.pos[i, 2]/8
        return d_matrix
    
    
class Element4:
    def __init__(self):
        self.pos = np.array([[-1, -1],
                             [1, -1],
                             [1,  1],
                             [-1, 1]])

    def N(self, x, y):
        shape_fcn = np.zeros(4)
        for i in range(4):
            shape_fcn[i] = (1.+x*self.pos[i, 0])*(1.+y*self.pos[i, 1])/4.
        return shape_fcn
    
    def d(self, x, y):
        d_matrix = np.zeros((2, 4))
        for i in range(4):
            d_matrix[0, i] = (1.+y*self.pos[i, 1])*self.pos[i, 0]/4.
            d_matrix[1, i] = (1.+x*self.pos[i, 0])*self.pos[i, 1]/4.
        return d_matrix
        
        
def det2(matrix):
    return matrix[0, 0]*matrix[1, 1] - matrix[0, 1]*matrix[1, 0]


def det3(matrix):
    return ((matrix[:, 0, 0]*matrix[:, 1, 1]*matrix[:, 2, 2] +
             matrix[:, 0, 1]*matrix[:, 1, 2]*matrix[:, 2, 0]+matrix[:, 0, 2]*matrix[:, 1, 0]*matrix[:, 2, 1]) -
            (matrix[:, 2, 0]*matrix[:, 1, 1]*matrix[:, 0, 2]+matrix[:, 2, 1]*matrix[:, 1, 2]*matrix[:, 0, 0] +
             matrix[:, 2, 2]*matrix[:, 1, 0]*matrix[:, 0, 1]))
