"""
Reads a collection of partitions, created by BuildFragments, to produce their traversal graphs.

Input to this program are:
  * The base name of fragment files
  * The number of fragments to process

Output is a collection of mtx files, with the same base name, suffixed by the fragment number
and a capital T.
"""

from sys import argv
from typing import List, TextIO, Set

import numpy as np
from scipy.sparse import coo_matrix
from sklearn.utils.graph import single_source_shortest_path_length


class ProgramConfiguration:
    """User arguments

    Verifies that the program is supplied enough arguments and provides one function for
    each argument type.
    """

    def __init__(self, args: List[str]):
        if len(args) != 3:
            print("Usage: %s <fragments base name> <number of fragments>" % args[0])
            exit(1)
        self.args = args

    def input_basename(self) -> str:
        return self.args[1]

    def nr_fragments(self) -> int:
        return int(self.args[2])


class Node:
    def __init__(self, partition: int, index: int):
        self.partition = partition
        self.index = index

    def __str__(self) -> str:
        return "%d.%d" % (self.partition, self.index)


class Edge:
    def __init__(self, node1: Node, node2: Node):
        self.x = node1
        self.y = node2

    def __str__(self) -> str:
        return "(%s):(%s)" % (self.x, self.y)


class CooMatrixBuilder:
    def __init__(self, nodes: Set[int]):
        self.nodes = nodes

    def execute(self) -> coo_matrix:
        i = []
        j = []
        v = []
        nodes = sorted(self.nodes)
        for each_node in nodes:
            for each_other_node in nodes:
                if each_other_node > each_node:
                    i.append(each_node - 1)
                    j.append(each_other_node - 1)
                    v.append(1)
        npi = np.array(i)
        npj = np.array(j)
        npv = np.array(v)
        nr_nodes = nodes[-1]
        return coo_matrix((npv, (npi, npj)), shape=(nr_nodes, nr_nodes))


class PartitionDescriptor:
    def __init__(self, partition_id: int):
        self.pid = partition_id
        self.borders: Set[int] = set()
        self.all_nodes: Set[int] = set()
        self.inner_nodes: Set[int] = set()
        self.edges = []

    def add_edge(self, edge: Edge):
        self.edges.append(edge)
        self.__add_node_from_edge_if_in(edge.x, edge.y)
        self.__add_node_from_edge_if_in(edge.y, edge.x)

    def __add_node_from_edge_if_in(self, x: Node, edge_peer: Node):
        if x.partition == self.pid:
            self.all_nodes.add(x.index)
            if edge_peer.partition != self.pid:
                self.borders.add(x.index)

    def get_inner_nodes(self) -> Set[int]:
        if len(self.inner_nodes) == 0:
            result = set()
            for each_node in self.all_nodes:
                if each_node not in self.borders:
                    result.add(each_node)
            return result
        else:
            return self.inner_nodes

    def q(self) -> float:
        return float(len(self.borders)) / float(len(self.all_nodes))

    def summarize(self):
        inners = self.get_inner_nodes()
        print("Partition %d" % self.pid)
        print("\tInner nodes = %d = %s" % (len(inners), inners))
        print("\tBorders     = %d = %s" % (len(self.borders), self.borders))
        print("\tQ%%        = %d" % (100.0 * self.q()))

    def get_initial_graph(self) -> coo_matrix:
        return CooMatrixBuilder(self.all_nodes).execute()


class FragmentProcessor:
    """
    Assuming that a fragment name is <basename>_<n>.txt, creates the associated fragment information.
    """

    def __init__(self, fragment_file: TextIO, partition_id: int):
        self.file = fragment_file
        self.pid = partition_id

    def get_descriptor(self) -> PartitionDescriptor:
        result = PartitionDescriptor(self.pid)
        each_line = self.file.readline()
        while each_line:
            items = each_line.replace("(", "").replace(")", "").split(":")
            if len(items) == 2:
                (node1, node2) = map(lambda s: s.split("."), items)
                self.__add_edge_to(result, node1, node2)
            each_line = self.file.readline()
        return result

    @classmethod
    def __add_edge_to(cls, d: PartitionDescriptor, x: (str, str), y: (str, str)):
        nx = Node(int(x[0]), int(x[1]))
        ny = Node(int(y[0]), int(y[1]))
        d.add_edge(Edge(nx, ny))


class WeightedEdge:
    def __init__(self, x: int, y: int, weight: int):
        self.x = x
        self.y = y
        self.weight = weight


class TraversalGraphBuilder:
    def __init__(self, partition: PartitionDescriptor):
        self.partition = partition
        self.max_node = 0
        self.edges: List[WeightedEdge] = []

    def create_graph(self):
        initial_graph = self.partition.get_initial_graph()
        for each_node in self.partition.borders:
            shortest_paths = single_source_shortest_path_length(initial_graph, each_node - 1)
            for each_other_node in self.partition.borders:
                if each_other_node > each_node:
                    shortest_distance = shortest_paths[each_other_node - 1]
                    edge = WeightedEdge(each_node, each_other_node, shortest_distance)
                    self.edges.append(edge)
            if each_node > self.max_node:
                self.max_node = each_node
        return self


class Main:
    def __init__(self, configuration: ProgramConfiguration):
        self.configuration = configuration

    def execute(self):
        for each_fragment_id in range(0, self.configuration.nr_fragments()):
            with open("%s_%d.txt" % (self.configuration.input_basename(), each_fragment_id), "rt") as f:
                descriptor = FragmentProcessor(f, each_fragment_id).get_descriptor()
                descriptor.summarize()
                tg = TraversalGraphBuilder(descriptor).create_graph()
                self.__write_graph_into("%s_%dT.mtx" % (self.configuration.input_basename(), each_fragment_id),
                                        tg.max_node, tg.edges)

    @classmethod
    def __write_graph_into(self, file_name: str, nr_nodes: int, weighted_edges: List[WeightedEdge]):
        with open(file_name, "wt") as f:
            f.write("%%MatrixMarket matrix coordinate pattern symmetric\n")
            f.write("%d %d %d\n" % (nr_nodes, nr_nodes, len(weighted_edges)))
            for each_edge in weighted_edges:
                f.write("%d %d %d\n" % (each_edge.x, each_edge.y, each_edge.weight))


# ================================================================================
Main(ProgramConfiguration(argv)).execute()
