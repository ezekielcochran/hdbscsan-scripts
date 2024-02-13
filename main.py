#!venv/bin/python

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import hdbscan
import argparse
from typing import Tuple

#
# parse command line arguments
#
def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compares two minimum spanning trees over the same points.\nIf no .csv file is given, the program will prompt you for data.\nIf no k value is given, the program will use 5 as the minimum cluster size.")
    parser.add_argument('-c', '--conceal-graph', action='store_true', help="suppress MVT plots")
    parser.add_argument('-v', '--verbose', action='store_true', help="enable verbose output")
    parser.add_argument('-f', '--filename', type=str, help="input the path to a .csv file to read data from")
    parser.add_argument('-s', '--second-filename', type=str, help="input the path to a .csv file to read the second ordering from: must be used along with the --filename flag")
    parser.add_argument('-k', '--set-min-cluster', type=int, help="manually set a minimum cluster size (expects integer)")
    return parser.parse_args()

# 
# Make some test data
# 
def _get_data() -> Tuple[np.ndarray, np.ndarray]:
    explicit_second_data = False
    csv_file = args.filename
    if csv_file == None:
        num_points = int(input("Enter the number of points in your data: "))
        print("Enter {} whitespace-separated points, one per line: ".format(num_points))
        test_data = []
        for i in range(num_points):
            test_data.append([int(x) for x in input().split()])
        test_data = np.array(test_data)
    else:
        try:
            test_data = np.genfromtxt(csv_file, delimiter=',', skip_header=True)
        except:
            print("Error! Trouble getting data from \"{}\"... does the file exist? ".format(csv_file))
            exit(1)
        csv_file2 = args.second_filename
        if csv_file2 != None:
            explicit_second_data = True
            try:
                data2 = np.genfromtxt(csv_file2, delimiter=',', skip_header=True)
            except:
                print("Error! Trouble getting data from \"{}\"... does the file exist? ".format(csv_file2))
                exit(1) 

    data1 = np.copy(test_data)
    if not explicit_second_data:
        np.random.shuffle(test_data)
        data2 = np.copy(test_data)
    return (data1, data2) # type: ignore            ...it says data2 could be unbound but that's not true

#
# compares two np MATRICES and returns whether they are equal
#
def are_identical_matrices(m1: np.ndarray, m2: np.ndarray) -> bool:
    if m1.shape != m2.shape:
        return False
    for i in range(m1.shape[0]):
        for j in range(m1.shape[1]):
            if m1[i, j] != m2[i, j]:
                return False
    return True

#
# compares two MSTs (given by matrices as well as data) and returns whether they are equal
#
def are_identical_msts(m1: np.ndarray, d1: np.ndarray, m2: np.ndarray, d2: np.ndarray) -> bool:
    if m1.shape != m2.shape:
        return False
    edges1 = set()
    edges2 = set()
    for row in m1:
        point1 = tuple(d1[int(row[0])])
        point2 = tuple(d1[int(row[1])])
        # need to enforce consistant ordering of points becuase edges are non-directional
        # note that "sorted" is stable, even for tuples
        point1, point2 = sorted([point1, point2])
        distance = float(row[2])
        edges1.add((point1, point2, distance))
    for row in m2:
        point1 = tuple(d2[int(row[0])])
        point2 = tuple(d2[int(row[1])])
        point1, point2 = sorted([point1, point2])
        distance = float(row[2])
        edges2.add((point1, point2, distance))
    # print("First 10 elements of edges1:\n{}".format(sorted(list(edges1))[:10]))
    # print("First 10 elements of edges2:\n{}".format(sorted(list(edges2))[:10]))
    return edges1 == edges2
    
#
# Plot both minimum spanning trees
# depends on global variables
#
def _make_plots():
    sns.set_context('poster')
    sns.set_style('white')
    sns.set_color_codes()
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    clusterer1.minimum_spanning_tree_.plot(edge_cmap='viridis', # type: ignore
                                        edge_alpha=0.6,
                                        node_size=80,
                                        edge_linewidth=2,
                                        colorbar=False,
                                        )
    plt.title("MST 1")
    plt.subplot(1, 2, 2)
    clusterer2.minimum_spanning_tree_.plot(edge_cmap='viridis', # type: ignore
                                        edge_alpha=0.6,
                                        node_size=80,
                                        edge_linewidth=2,
                                        colorbar=False,
                                        )
    plt.title("MST 2")
    plt.show()

#
# displays information about the MST matrices and points
# depends on global variables
#
def _echo_info():
    # print("data1:\n{}".format(data1))
    # print("data2:\n{}".format(data2))
    mst1_matrix = clusterer1.minimum_spanning_tree_.to_numpy() # type: ignore
    mst2_matrix = clusterer2.minimum_spanning_tree_.to_numpy() # type: ignore
    mst1_data = clusterer1.minimum_spanning_tree_._data # type: ignore
    mst2_data = clusterer2.minimum_spanning_tree_._data # type: ignore
    if args.verbose:
        print("\nMST 1: ")
        print(mst1_matrix)
        print("\nMST 2: ")
        print(mst2_matrix)

        print("\nData order for MST 1: ")
        i = 0
        for point in mst1_data:
            print("{}: {}".format(i, point))
            i += 1
        print()
        print("Data order for MST 2: ")
        i = 0
        for point in mst2_data:
            print("{}: {}".format(i, point))
            i += 1
    print("\n" + "=" * 100)
#    print("MST matrices equal:\t{}".format(are_identical_matrices(mst1_matrix, mst2_matrix)))
#    print("MSTs actually equal:\t{}".format(are_identical_msts(mst1_matrix, mst1_data, mst2_matrix, mst2_data)))
    print("Minimum Spanning Trees are Equivalent:\t{}".format(are_identical_msts(mst1_matrix, mst1_data, mst2_matrix, mst2_data)))
    print("=" * 100 + "\n")

if __name__ == "__main__":
    args = _get_args()

    try:
        data1, data2 = _get_data()
    except ValueError as e:
        print("Error while trying to get data: \n\"{}\"\n... did you enter data in a bad shape?".format(e))
        exit(1)

    #
    # use HDBSCAN
    #
    k = args.set_min_cluster
    if k == None:
        k = 5
    clusterer1 = hdbscan.HDBSCAN(min_cluster_size=k, gen_min_span_tree=True)
    clusterer2 = hdbscan.HDBSCAN(min_cluster_size=k, gen_min_span_tree=True)
    try:
        clusterer1.fit(data1)
        clusterer2.fit(data2)
    except ValueError as e:
        print("Error while trying to use HDBSCAN: \n\"{}\"\n... did you pick a bad value for minimum cluster size?".format(e))
        exit(1)

    _echo_info()

    if not args.conceal_graph:
        try:
            _make_plots()
        except ValueError as e:
            print("Error while trying to plot: \n\"{}\"\n... plotting is weird in dimensions higher than 2".format(e))
