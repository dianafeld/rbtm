import os

import h5py

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from storage import app

logger = app.logger


def get_and_save_3d_points(hdf5_filename, output_filename, rarefaction, level1, level2):
    # Script will create files for each level between level1 and level2 including
    colormap = plt.cm.hsv

    levels = range(level1, level2 + 1)
    logger.info("rarefaction = {}, levels = {}".format(rarefaction, levels))

    with h5py.File(hdf5_filename, "r") as hdf5_file:
        data_cube = hdf5_file["Results"]

        logger.info("Original cube shape: {}".format(data_cube.shape))

        logger.info("Rarefying data_cube...")
        if rarefaction > 1:
            data_cube = data_cube[::rarefaction, ::rarefaction, ::rarefaction]
        else:
            data_cube = data_cube[::2, :, :]

        logger.info("Rarefied cube shape: {}".format(data_cube.shape))
        n, m, k = data_cube.shape

        min_value = np.min(data_cube)
        max_value = np.max(data_cube)
        if max_value == min_value:
            logger.info("All values are the same - look for better data!\nStop.")
            return

        with h5py.File(output_filename, "w") as vis_file:
            pass

        logger.info("Looking for thresholds...")
        list_of_percents_to_left = [(1 - 0.5 ** level) * 100 for level in levels]
        thresholds_list = np.percentile(data_cube, list_of_percents_to_left)
        thresholds_dict = dict(zip(levels, thresholds_list))
        logger.info("Done")

        for level in levels:
            threshold = thresholds_dict[level]
            shape = (m, n, k)
            num_vertices, rgba, xyz = get_level(level, threshold, data_cube, rarefaction, colormap)
            with h5py.File(output_filename, "w") as vis_file:
                save_level(level, vis_file, num_vertices, shape, rgba, xyz)

            logger.info("Number of leftover vertices: {},  {:.2f}% from all".format(
                num_vertices, num_vertices * 100 / (n * m * k)))

        logger.info("Finish")


def get_level(level, threshold, data_cube, rarefaction, colormap):
    logger.info("Creating file with level: {}".format(level))

    n, m, k = data_cube.shape
    min_value = np.min(data_cube)
    max_value = np.max(data_cube)

    logger.info("Throwing away points with small values...")
    Ix, Iy, Iz = np.where(data_cube > threshold)

    logger.info("Calculating values to write...")
    num_vertices = len(Ix)
    left_values = np.empty(num_vertices, dtype=float)
    for i in range(num_vertices):
        left_values[i] = data_cube[Ix[i], Iy[i], Iz[i]]

    norm = matplotlib.colors.Normalize(vmin=threshold, vmax=max_value)
    m = matplotlib.cm.ScalarMappable(norm=norm, cmap=colormap)
    RGBA = m.to_rgba(left_values)
    RGBA = (RGBA * 256).astype(int)

    R, G, B = RGBA[:, 0], RGBA[:, 1], RGBA[:, 2]

    A = left_values
    del left_values
    A = (A - min_value) / (max_value - min_value)
    A = (A * 256).astype(int)

    if rarefaction != 1:
        X = Ix - n / 2
    else:
        X = 2 * Ix - n
        # strange multiplying by 2 when rarefaction==1, it's because of using half of
        # array, not full (look at code above where array is rarefied)
    Y = Iy - m / 2
    Z = Iz - k / 2

    rgba = (R, G, B, A)
    xyz = (X, Y, Z)

    return num_vertices, rgba, xyz


def save_level(level, hdf5_file, num_vertices, shape, rgba, xyz):
    n, m , k = shape
    R, G, B, A = rgba
    X, Y, Z = xyz

    logger.info("Writing to file...")
    group = hdf5_file.create_group(str(level))
    group.attrs["n"] = n
    group.attrs["m"] = m
    group.attrs["k"] = k
    group.attrs["num_vertices"] = num_vertices
    hdf5_file.create_dataset("R", data=R, compression="gzip", compression_opts=4)
    hdf5_file.create_dataset("G", data=G, compression="gzip", compression_opts=4)
    hdf5_file.create_dataset("B", data=B, compression="gzip", compression_opts=4)
    hdf5_file.create_dataset("A", data=A, compression="gzip", compression_opts=4)
    hdf5_file.create_dataset("X", data=X, compression="gzip", compression_opts=4)
    hdf5_file.create_dataset("Y", data=Y, compression="gzip", compression_opts=4)
    hdf5_file.create_dataset("Z", data=Z, compression="gzip", compression_opts=4)


def save_level_js(level, output_filename_prefix, num_vertices, shape, rgba, xyz):
    n, m , k = shape
    R, G, B, A = rgba
    X, Y, Z = xyz

    output_filename = "{}_level{}.js".format(output_filename_prefix, level)

    f = open(output_filename, 'w')
    logger.info("Writing to file...")
    f.seek(0)
    f.truncate()
    f.write("var NMK = [{}, {}, {}]".format(n, m, k))

    f.write(";\nvar R_arr = " + str(R.tolist()).replace(" ", ""))
    f.write(";\nvar G_arr = " + str(G.tolist()).replace(" ", ""))
    f.write(";\nvar B_arr = " + str(B.tolist()).replace(" ", ""))
    f.write(";\nvar A_arr = " + str(A.tolist()).replace(" ", ""))
    f.write(";\nvar X_arr = " + str(X.tolist()).replace(" ", ""))
    f.write(";\nvar Y_arr = " + str(Y.tolist()).replace(" ", ""))
    f.write(";\nvar Z_arr = " + str(Z.tolist()).replace(" ", ""))

    f.write(";\nvar num_vertices = " + str(num_vertices) + ";\n")
    f.close()

    logger.info("Finish writing, filename is: '{}', size of file: {:.1f} kB".format(
        output_filename, float(os.stat(output_filename).st_size) / 1024))


