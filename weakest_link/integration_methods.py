from FEMfunctions import Element8
from FEMfunctions import det3
import numpy as np


def gauss_integration_3d(function_values, xyz):
    e = Element8()
    n = xyz.shape[0]
    gp = np.array([-1., 1.]) / np.sqrt(3.)

    n_vec = np.array([e.N(gp[0], gp[0], gp[0]), e.N(gp[0], gp[0], gp[1]),
                      e.N(gp[0], gp[1], gp[0]), e.N(gp[0], gp[1], gp[1]),
                      e.N(gp[1], gp[0], gp[0]), e.N(gp[1], gp[0], gp[1]),
                      e.N(gp[1], gp[1], gp[0]), e.N(gp[1], gp[1], gp[1])])
    d_vec = np.array([e.d(gp[0], gp[0], gp[0]), e.d(gp[0], gp[0], gp[1]),
                      e.d(gp[0], gp[1], gp[0]), e.d(gp[0], gp[1], gp[1]),
                      e.d(gp[1], gp[0], gp[0]), e.d(gp[1], gp[0], gp[1]),
                      e.d(gp[1], gp[1], gp[0]), e.d(gp[1], gp[1], gp[1])])

    integral = np.zeros((n, 8))

    # Interpolating values to each gauss point
    for i in range(8):
        integral[:, i] = np.dot(function_values[:, :], n_vec[i, :])*det3(np.matmul(d_vec[i], xyz))
    return np.sum(np.sum(integral, 1))


def axi_symmetric_cylinder(function_values, r, h):
    pass


if __name__ == '__main__':
    f = np.ones((1, 8))
    x = np.array([[[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                   [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]],
                  [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                   [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]]
                  ])*2
    print x.shape
    print gauss_integration_3d(f, x)
