def create_path(points, path_name):
    path_points = []
    for point in points:
        path_points.append((point[0], point[1], point[2]))

    path = session.Path(name=path_name, type=POINT_LIST, expression=path_points)
    return path


def get_stress_tensors_from_path(path):
    stress_data = np.zeros((100, 3, 3))
    comps = ['S11', 'S22', 'S33', 'S12', 'S13', 'S23']
    for (idx1, idx2), comp in zip([(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)], comps):
        session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='S',
                                                                       outputPosition=ELEMENT_NODAL,
                                                                       refinement=[COMPONENT, comp])
        xy = xyPlot.XYDataFromPath(name='Stress profile', path=path,
                                   labelType=TRUE_DISTANCE, shape=UNDEFORMED, pathStyle=PATH_POINTS,
                                   includeIntersections=False)

        for idx, (_, stress_comp) in enumerate(xy):
            stress_data[idx, idx1, idx2] = stress_comp
    stress_data[:, 1, 0] = stress_data[:, 0, 1]
    stress_data[:, 2, 0] = stress_data[:, 0, 2]
    stress_data[:, 2, 1] = stress_data[:, 1, 2]
    return stress_data
